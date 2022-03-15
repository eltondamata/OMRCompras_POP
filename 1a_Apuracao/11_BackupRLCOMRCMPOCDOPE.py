#elton.mata@martins.com.br

#definir arquivo feather
with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()
filname = caminho + 'bd/RLCOMRCMPOCDOPE_bkp.ft'

#Importa as Bibliotecas
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn

#Código SQL
my_sql_query = ("""
SELECT * from dwh.RLCOMRCMPOCDOPE
		""")
pd.read_sql(my_sql_query, con=conn).to_feather(filname)

conn.close()