import pandas as pd
import dao

## carregando os registros do banco de dados
tb_emissor, tb_item, tb_transportadora, tb_embalagens_ticket, tb_itens_ticket, tb_ticket = dao.carregar_db()

## inserir os dados de empolamento
empolamento = pd.DataFrame({'MATERIAL':[
                               'MATERIAL ESCAVAÇÃO',
                               'MATERIAL TBM - LAMA',
                               'ENTULHO',
                               'LAMA',
                               'MATERIAL TBM - ESCAVAÇÃO',
                               'AÇO',
                               'BRITA',
                               'PEDRA RACHÃO',
                               'B. G. S.',
                               'CONCRETO USINADO'],
                            'EMPOLAMENTO': [
                                1.7, 1.9, 1.9, 1.9, 1.7, 1, 1, 1, 1, 1 ]})

# agrupando os dados
## juntando as descrições dos materiais
df_materiais = tb_embalagens_ticket.merge(tb_item, on=['ITM_SEQUENCIAL'])

## juntando as descrições dos destinos
df_destinos = tb_itens_ticket.merge(tb_item, on=['ITM_SEQUENCIAL'])

## juntando os nomes dos emissores
ticket_com_emissor = tb_ticket.merge(tb_emissor, on=['EMS_SEQUENCIAL'])

## juntando as transportadoras
ticket_com_transpostadora = ticket_com_emissor.merge(tb_transportadora, on=['TRP_SEQUENCIAL'])

## juntando a tabela dos materiais
ticket_com_materiais = ticket_com_transpostadora.merge(df_materiais, on=['TCK_SEQUENCIAL'])

## juntando a tabela dos destinos
ticket = ticket_com_materiais.merge(df_destinos, on=['TCK_SEQUENCIAL'])

# transformando os dados
## deletando colunas desnecessárias
ticket.drop(['EMS_SEQUENCIAL', 'TRP_SEQUENCIAL', 'ITM_SEQUENCIAL_x', 'ITM_SEQUENCIAL_y'], axis=1, inplace=True)

## renomeando as colunas
ticket.columns = ['TICKET', 'PLACA', 'STATUS', 'DATA', 'PESO LIQUIDO', 'EMISSOR', 'TRANSPORTADORA', 'MATERIAL', 'DESTINO']

## reordenando as colunas
ticket = ticket[['TICKET', 'PLACA', 'STATUS', 'DATA', 'EMISSOR', 'TRANSPORTADORA', 'MATERIAL', 'DESTINO', 'PESO LIQUIDO']]

## resolver metro cúbico
ticket = ticket.merge(empolamento, on=['MATERIAL'])

## tratamento da coluna status
ticket['STATUS'] = ticket['STATUS'].map({3:'Válido',
                                         6:'Cancelado'})

## tratamento da coluna emissor
ticket['EMISSOR'] = ticket['EMISSOR'].map({'CONSÓRCIO FTS (LINHA LESTE)':'BALANÇA'})
ticket['EMISSOR'].fillna('NÃO IDENTIFICADO', inplace=True)

## transformando a coluna registros
ticket['DATA'] = pd.to_datetime(ticket['DATA'], unit='ns')

## inserindo coluna de m3
ticket['M3'] = ticket['PESO LIQUIDO'] / ticket['EMPOLAMENTO']

## funções para dashboard

## filtrar o df pelo intervalo de datas
def filtrar_por_data(data_inicial, data_final):
    filtro_data = (ticket['DATA'] >= data_inicial) &\
                  (ticket['DATA'] <= data_final)
    return ticket.loc[filtro_data]

## tratando os dados para exibição
def tratar_dataframe(df):
    ## removendo os tickets cancelados
    df_validos = df.drop(df[df['STATUS'] == 'Cancelado'].index)

    ## agrupando os dados
    dados_tratados = df_validos.groupby(['TRANSPORTADORA', 'EMISSOR', 'DESTINO', 'MATERIAL'])\
                                .agg({'PESO LIQUIDO':['sum']})
    dados_tratados.columns = ['PESO TOTAL']

    ## resetando o index
    dados_tratados.reset_index(inplace=True)

    ## adicionando coluna de tonelada
    dados_tratados['TON'] = (dados_tratados['PESO TOTAL'] / 1000)

    ## removendo coluna desnecessária
    #dados_tratados.drop(['PESO TOTAL'], axis=1, inplace=True)

    ## adicionando coluna empolamento
    dados_tratados = dados_tratados.merge(empolamento, on=['MATERIAL'])

    ## adicionando coluna de m3
    dados_tratados['M3'] = (dados_tratados['TON'] / dados_tratados['EMPOLAMENTO'])

    ## reordenando as colunas
    dados_tratados = dados_tratados[['TRANSPORTADORA', 'EMISSOR', 'DESTINO', 'MATERIAL',
                                     'M3', 'EMPOLAMENTO', 'TON']]

    ## formando os números
    #dados_tratados['PESO TOTAL'] = dados_tratados.apply(lambda x: "{:,.0f}".format(x['PESO TOTAL']), axis=1)
    dados_tratados['TON'] = dados_tratados.apply(lambda x: "{:,.2f}".format(x['TON']), axis=1)
    dados_tratados['EMPOLAMENTO'] = dados_tratados.apply(lambda x: "{:,.1f}".format(x['EMPOLAMENTO']), axis=1)
    dados_tratados['M3'] = dados_tratados.apply(lambda x: "{:,.2f}".format(x['M3']), axis=1)

    return dados_tratados

def get_transportadoras():
    return ticket['TRANSPORTADORA'].unique()
