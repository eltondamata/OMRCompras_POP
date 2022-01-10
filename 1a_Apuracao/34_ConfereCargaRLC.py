#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format
from tabulate import tabulate

with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    NUMANOMESOCD = f.read()
NUMMESOCD = int(str(NUMANOMESOCD)[-2:])

#Consulta
mysql = ("""     
SELECT NOMMES,
		DESTIPCNLVNDOMR,
		SUM(VLRVNDFATLIQ) AS FAT,
		SUM(VLRRCTLIQAPU) AS RL,
		SUM(VLRMRGBRT) AS MB,
		SUM(VLRMRGCRB) AS MC
FROM DWH.RLCOMRCMPOCDOPE
GROUP BY NOMMES,
		 DESTIPCNLVNDOMR
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
NUMMES = list(range(13))[1:]
dic_NUMMES = dict(zip(NOMMES, NUMMES))
df['NUMMES'] = df['NOMMES'].map(dic_NUMMES)
dfcnl = df.query(f'NUMMES=={NUMMESOCD}').groupby(['NOMMES','DESTIPCNLVNDOMR'])[['FAT', 'RL', 'MB', 'MC']].sum().reset_index()
dfmes = df.groupby(['NOMMES','NUMMES'])[['FAT', 'RL', 'MB', 'MC']].sum().reset_index()
dfmes.loc['TOTAL',:] = dfmes[['FAT','RL','MB','MC']].sum(axis=0)

print('Tabela: DWH.RLCOMRCMPOCDOPE')
print(tabulate(dfcnl, headers='keys', tablefmt='psql', floatfmt=',.2f', showindex=False, numalign='right'),'\n')
print(tabulate(dfmes.sort_values(by='NUMMES').fillna(''), headers='keys', tablefmt='psql', floatfmt=',.2f', showindex=False, numalign='right'))