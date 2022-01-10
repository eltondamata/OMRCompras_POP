#Python 3.8.2
#elton.mata@martins.com.br

#definir arquivo csv
filname = r'..\RLCOMRCMPOCDOPE_bkp.csv'

#Importa as Bibliotecas
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn

#Código SQL
my_sql_query = ("""
SELECT * from dwh.RLCOMRCMPOCDOPE
		""")

#Exporta os dados para o arquivo csv
write_header = True
for chunk in pd.read_sql(my_sql_query, chunksize=1000, con=conn):
    chunk.to_csv(filname, sep=";", encoding="iso-8859-1", decimal=",", mode='a', header=write_header, index=False)
    write_header = False

#Fecha a conexão com banco de dados Oracle
conn.close()