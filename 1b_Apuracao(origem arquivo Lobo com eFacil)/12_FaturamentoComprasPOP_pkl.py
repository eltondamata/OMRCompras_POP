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
NUMMESOCD = int(str(NUMANOMESOCD)[-2:])

#Parametros (ultimas 8 semandas seg a dom)
segunda = datetime.now() - timedelta(days = datetime.now().weekday()+ (7*8) ) #Segunda de 8 semanas atras
domingo = datetime.now() - timedelta(days = datetime.now().weekday()+1) #Ultimo Domingo
DATINI = int(segunda.strftime("%Y%m%d")) #Segunda de 8 semanas atras (formato AnoMesDia)
DATFIM = int(domingo.strftime("%Y%m%d")) #Ultimo Domingo (formato AnoMesDia)
print('Periodo (Ultimas 8 semanas):', DATINI, "-", DATFIM)

#arquivo de vendas (Faturamento por Fornecedor x Filial)
dfvnd = pd.read_excel(caminho + 'ArquivosRecebidos/POP_Janeiro_2022 Geral (email Lobo 23dez21).xlsx', 'BD POP', usecols = "B:O")

#Consulta realizado
mysql = (f"""
   SELECT {NUMANOMESOCD} AS NUMANOMESOCD,
          {NUMMESOCD} AS NUMMESOCD,
          SUBCTGPRD.CODGRPPRD, 
          SUBCTGPRD.CODCTGPRD, 
          DIVFRN.CODDIVFRN, 
          DIVFRN.DESDIVFRN, 
          DIVFRN.NOMGRPECOFRN, 
          t7.CODESTUNI, 
          t5.CODFIL,
          SUBCTGPRD.DESCTGPRD, 
          DIVFRN.CODDRTCLLATU, 
          DIVFRN.DESDRTCLLATU, 
          DIVFRN.DESCLLCMPATU,
          SUM(t1.VLRVNDFATLIQ) AS VLRVNDFATLIQ
      FROM DWH.FTOOMRCMPDIA t1
         , DWH.DIMPOD t2
         , DWH.DIMTIP t3
         , DWH.DIMCNOOCD t4
         , DWH.DIMPRD DIVFRN
         , DWH.DIMPRD SUBCTGPRD
         , DWH.DIMGEO t7
         , DWH.DIMFIL t5
      WHERE t1.SRKPODREF = t2.SRKPOD 
        AND t1.SRKTIPOPEVND = t3.SRKTIP 
        AND t1.SRKCNOOCD = t4.SRKCNOOCD 
        AND t1.SRKDIVFRN = DIVFRN.SRKPRD 
        AND t1.SRKSUBCTGPRD = SUBCTGPRD.SRKPRD
        AND t1.SRKGEO = t7.SRKGEO 
        AND t1.SRKFIL = t5.SRKFIL
        AND t3.CODTIP = 'VND'
        AND t4.CODCNOOCD = 'RLZ'
        AND t2.NUMANOMESDIA BETWEEN {DATINI} AND {DATFIM}
      GROUP BY SUBCTGPRD.CODGRPPRD,
               SUBCTGPRD.CODCTGPRD,
               DIVFRN.CODDIVFRN,
               DIVFRN.DESDIVFRN,
               DIVFRN.NOMGRPECOFRN,
               t7.CODESTUNI,
               t5.CODFIL,
               SUBCTGPRD.DESCTGPRD,
               DIVFRN.CODDRTCLLATU,
               DIVFRN.DESDRTCLLATU,
               DIVFRN.DESCLLCMPATU
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

#NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
#dic_NUMMES = dict(list(enumerate(NOMMES, start=1)))
#df['NOMMES'] = df['NUMMESOCD'].map(dic_NUMMES)

dfvnd['VLRFAT'] = dfvnd.iloc[:,-1:]
dfvnd.rename(columns={'CODUNDREG':'CODFIL'}, inplace=True)
dffrnfil = dfvnd.groupby(['CODDIVFRN', 'CODFIL'])[['VLRFAT']].sum().reset_index()
dffrnfil = dffrnfil.query('VLRFAT>0')

#Distribui VLRFAT por UF (com base na participacao historica das ultimas 8 semanas)
df['DRIVER'] = (df['VLRVNDFATLIQ'] / df.groupby(['CODDIVFRN', 'CODFIL'])['VLRVNDFATLIQ'].transform('sum'))
df = df.merge(dffrnfil, how='inner', on=['CODDIVFRN', 'CODFIL'])
df.eval('VLRVNDFATLIQ=VLRFAT * DRIVER', inplace=True)
df.drop(['DRIVER', 'VLRFAT'], axis=1, inplace=True)

#Agrupa base de vendas por celula
dfcel = dfvnd.groupby(['DESCLLCMPATU'])[['VLRFAT']].sum().reset_index()

#Alinha total por Celula
df['DRIVER'] = (df['VLRVNDFATLIQ'] / df.groupby(['DESCLLCMPATU'])['VLRVNDFATLIQ'].transform('sum'))
df = df.merge(dfcel, how='inner', on=['DESCLLCMPATU'])
df.eval('POP=VLRFAT * DRIVER', inplace=True)
df.drop(['DRIVER', 'VLRFAT'], axis=1, inplace=True)

#Confere
pd.options.display.float_format = '{:,.2f}'.format
print('Confere TOTAL por DIRETORIA')
print(df.groupby('DESDRTCLLATU')[['VLRVNDFATLIQ', 'POP']].sum().reset_index(),'\n')
print('Confere TOTAL por celula VLRVNDFATLIQ=Faturamento distribuido na base Historica e POP=Faturamento alinhado com a base de vendas no total da celula')
confere = df.groupby('DESCLLCMPATU')[['VLRVNDFATLIQ', 'POP']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index())

#Export base final com Faturamento por Fornecedor x Filial x UF (alem das dimensoes relacionadas a estrutura de compras)
df.to_feather(caminho + 'bd/FaturamentoComprasPOP.ft')