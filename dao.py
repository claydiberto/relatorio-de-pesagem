import pyodbc
import pandas as pd

server = 'tcp:servername\sqlexpress'
database = 'database'
username = 'sa'
password = 'sa'
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

def carregar_db():
    ## buscando as tabelas
    emissor = pd.read_sql('SELECT EMS_SEQUENCIAL, EMS_DESCRICAO FROM dbo.tbEmissor', conn)
    item = pd.read_sql('SELECT ITM_SEQUENCIAL, ITM_NOME FROM dbo.tbItem', conn)
    transportadora = pd.read_sql('SELECT TRP_SEQUENCIAL, TRP_DESCRICAO FROM dbo.tbTransportadora', conn)
    embalagem_ticket = pd.read_sql('SELECT ITM_SEQUENCIAL, TCK_SEQUENCIAL FROM dbo.tbEmbalagensTicket', conn)
    item_ticket = pd.read_sql('SELECT TCK_SEQUENCIAL, ITM_SEQUENCIAL FROM dbo.tbItensTicket', conn)
    ticket = pd.read_sql('SELECT TCK_SEQUENCIAL, TCK_PLACA_CARRETA, EMS_SEQUENCIAL, TRP_SEQUENCIAL, TCK_ESTADO, TCK_DATA, TCK_PESO_LIQUIDO FROM dbo.tbTicket', conn)

    return emissor, item, transportadora, embalagem_ticket, item_ticket, ticket
