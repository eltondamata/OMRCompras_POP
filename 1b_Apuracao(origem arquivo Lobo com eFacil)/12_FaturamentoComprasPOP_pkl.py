#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()
with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    NUMANOMESOCD = f.read()
NUMANOMESOCD = int(NUMANOMESOCD)
NUMMESOCD = int(str(NUMANOMESOCD)[-2:])

#Parametros (ultimas 8 semandas seg a dom)
segunda = datetime.now() - timedelta(days = datetime.now().weekday()+ (7*8) ) #Segunda de 8 semanas atras
domingo = datetime.now() - timedelta(days = datetime.now().weekday()+1) #Ultimo Domingo
DATINI = int(segunda.strftime("%Y%m%d")) #Segunda de 8 semanas atras (formato AnoMesDia)
DATFIM = int(domingo.strftime("%Y%m%d")) #Ultimo Domingo (formato AnoMesDia)
print('Periodo (Ultimas 8 semanas):', DATINI, "-", DATFIM)

#arquivo de vendas (Faturamento por Fornecedor x Filial)
#['DIRETORIA_VENDA', 'CODUNDREG', 'DESUNDREG', 'DESDRTCLLATU', 'DESCLLCMPATU', 'CODGRPECOFRN', 'NOMGRPECOFRN', 'CODDIVFRN', 'DESDIVFRN', 'Média 2M', 'OMR JANEIRO 2022', 'POP', 'POP ajustado', 'AJUSTE COMPRAS']
dfvnd = pd.read_excel(caminho + 'ArquivosRecebidos/POP_Janeiro_2022 Geral (email Lobo 23dez21).xlsx', 'BD POP', usecols = "B:O")
dfvnd = dfvnd.groupby(['DIRETORIA_VENDA', 'CODDIVFRN', 'CODUNDREG', 'DESCLLCMPATU'])[['AJUSTE COMPRAS']].sum().reset_index()
dfvnd.rename(columns={'DIRETORIA_VENDA': 'DESTIPCNLVNDOMR', 'CODUNDREG':'CODFIL'}, inplace=True)
dfvnd['DESTIPCNLVNDOMR'].replace('ATACADO', 'OUTROS CANAIS', inplace=True)

#Consulta realizado
mysql = (f"""
   SELECT {NUMANOMESOCD} AS NUMANOMESOCD,
          {NUMMESOCD} AS NUMMESOCD,
          DIMPRD.CODGRPPRD, 
          DIMPRD.CODCTGPRD, 
          DIMPRD.CODDIVFRN, 
          DIMPRD.DESDIVFRN, 
          DIMPRD.NOMGRPECOFRN, 
          DIMCLI.CODESTCLI, 
          DIMFILEPD.CODFIL,
          DIMPRD.DESCTGPRD, 
          DIMPRD.CODDRTCLLATU, 
          DIMPRD.DESDRTCLLATU, 
          DIMPRD.DESCLLCMPATU,
          DIMCNLVND.DESTIPCNLVNDOMR,
          SUM(FTOFAT.VLRFATLIQ) AS VLRVNDFATLIQ
   FROM DWH.FTOFAT FTOFAT
      , DWH.DIMPRD DIMPRD
      , DWH.DIMCLIEND DIMCLI
      , DWH.DIMPOD DIMPOD
      , DWH.DIMTIP DIMTIP
      , DWH.DIMCNLVND DIMCNLVND
      , DWH.DIMFIL DIMFILEPD
   WHERE FTOFAT.SRKPRD = DIMPRD.SRKPRD 
     AND FTOFAT.SRKCLIENDVND = DIMCLI.SRKCLIEND 
     AND FTOFAT.SRKDATFAT = DIMPOD.SRKPOD 
     AND FTOFAT.SRKTIPFAT = DIMTIP.SRKTIP 
     AND FTOFAT.SRKCNLVNDINI = DIMCNLVND.SRKCNLVND 
     AND FTOFAT.SRKFILEPD = DIMFILEPD.SRKFIL 
     AND DIMTIP.CODTIP = 'VNDMER' 
     AND DIMPOD.NUMANOMESDIA BETWEEN {DATINI} AND {DATFIM}
 GROUP BY DIMPRD.CODGRPPRD, 
          DIMPRD.CODCTGPRD, 
          DIMPRD.CODDIVFRN, 
          DIMPRD.DESDIVFRN, 
          DIMPRD.NOMGRPECOFRN, 
          DIMCLI.CODESTCLI, 
          DIMFILEPD.CODFIL,
          DIMPRD.DESCTGPRD, 
          DIMPRD.CODDRTCLLATU, 
          DIMPRD.DESDRTCLLATU, 
          DIMPRD.DESCLLCMPATU,
          DIMCNLVND.DESTIPCNLVNDOMR
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

df['DESTIPCNLVNDOMR'].replace("E-FÁCIL", "EFACIL", inplace=True)
df['DESTIPCNLVNDOMR'].replace('VENDAS DIGITAIS', 'OUTROS CANAIS', inplace=True)
df = df.groupby(['NUMANOMESOCD', 'NUMMESOCD', 'CODGRPPRD', 'CODCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'CODESTCLI', 'CODFIL', 'DESCTGPRD', 'CODDRTCLLATU', 'DESDRTCLLATU', 'DESCLLCMPATU', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ']].sum().reset_index()

NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
dic_NUMMES = dict(list(enumerate(NOMMES, start=1)))
df['NOMMES'] = df['NUMMESOCD'].map(dic_NUMMES)

dfvnd['VLRFAT'] = dfvnd.iloc[:,-1:]
dffrnfilcnl = dfvnd.groupby(['CODDIVFRN', 'CODFIL', 'DESTIPCNLVNDOMR'])[['VLRFAT']].sum().reset_index()
dffrnfilcnl = dffrnfilcnl.query('VLRFAT>0')

#Distribui VLRFAT por UF (com base na participacao historica das ultimas 4 semanas)
df['DRIVER'] = (df['VLRVNDFATLIQ'] / df.groupby(['CODDIVFRN', 'CODFIL', 'DESTIPCNLVNDOMR'])['VLRVNDFATLIQ'].transform('sum'))
df = df.merge(dffrnfilcnl, how='inner', on=['CODDIVFRN', 'CODFIL', 'DESTIPCNLVNDOMR'])
df.eval('VLRVNDFATLIQ=VLRFAT * DRIVER', inplace=True)
df.drop(['DRIVER', 'VLRFAT'], axis=1, inplace=True)

#Agrupa base de vendas por celula
dfcel = dfvnd.groupby(['DESCLLCMPATU', 'DESTIPCNLVNDOMR'])[['VLRFAT']].sum().reset_index()

#Alinha total por Celula x Canal
df['DRIVER'] = (df['VLRVNDFATLIQ'] / df.groupby(['DESCLLCMPATU', 'DESTIPCNLVNDOMR'])['VLRVNDFATLIQ'].transform('sum'))
df = df.merge(dfcel, how='inner', on=['DESCLLCMPATU', 'DESTIPCNLVNDOMR'])
df.eval('POP=VLRFAT * DRIVER', inplace=True)
df.drop(['DRIVER', 'VLRFAT'], axis=1, inplace=True)

#Confere
pd.options.display.float_format = '{:,.2f}'.format
print('Confere TOTAL por DIRETORIA')
print(df.groupby('DESDRTCLLATU')[['VLRVNDFATLIQ', 'POP']].sum().reset_index(),'\n')
print('Confere TOTAL por celula VLRVNDFATLIQ=Faturamento distribuido na base Historica e POP=Faturamento alinhado com a base de vendas no total da celula')
confere = df.groupby('DESCLLCMPATU')[['VLRVNDFATLIQ', 'POP']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index(), '\n')
confere = df.groupby('DESTIPCNLVNDOMR')[['VLRVNDFATLIQ', 'POP']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index())


#Export base final com Faturamento por Fornecedor x Filial x UF (alem das dimensoes relacionadas a estrutura de compras)
df.to_feather(caminho + 'bd/FaturamentoComprasPOP.ft')