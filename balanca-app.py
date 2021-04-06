import streamlit as st
import model as df
import pandas as pd
import base64

st.set_page_config(
    page_title='Balança APP',
    page_icon="⚖️",
    layout='wide')

## função para download do arquivo em CSV
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode("UTF-8")).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

## main
col1, col2 = st.beta_columns(2)
col1.image('https://i.ibb.co/FK4QZkY/logo.png', width=300)
col2.title('Relatório da Balança - TESTE')

## filtro por data de emissão do ticket
start_date = st.date_input('Data inicial')
final_date = st.date_input('Data final')
data_inicial = pd.to_datetime(start_date, unit='ns')
data_final = pd.to_datetime(final_date, unit='ns')

## filtrando e formatando para exibição
frame = df.filtrar_por_data(data_inicial, data_final)
resumo_dados = df.tratar_dataframe(frame)

## mostrando a tabela no painel
st.subheader('Resumo de Materiais Transportados')
st.dataframe(resumo_dados)

## botão de download
if st.button('Download do resumo'):
    tmp_download_link = download_link(resumo_dados, 'resumo_balanca.csv', 'Download do arquivo')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

## exibição dos dados dos tickets filtrados
st.write('   ')
if st.checkbox('Exibir Tickets'):
    coluna1, coluna2 = st.beta_columns(2)
    coluna1.subheader('Tickets do Período Selecionado')
    filtro_transportadora = coluna2.selectbox('Transportadora', options=df.get_transportadoras())

    ## filtrando o dataframe por transportadora
    frame = frame[frame['TRANSPORTADORA'] == filtro_transportadora]

    frame['PESO LIQUIDO'] = frame.apply(lambda x: "{:,.0f}".format(x['PESO LIQUIDO']), axis=1)
    frame = frame.sort_values(by=['DATA'])
    frame.set_index('TICKET', inplace=True)

    st.table(frame)
