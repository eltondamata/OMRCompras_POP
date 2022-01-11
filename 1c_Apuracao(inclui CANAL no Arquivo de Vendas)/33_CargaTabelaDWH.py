#Atualiza POP na tabela DWH.RLCOMRCMPOCDOPE
#Tempo execução = 29 segundos

import pandas as pd
from sqlalchemy.types import String
from sqlalchemy.types import Integer
from sqlalchemy.types import Float
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn, connx
import time

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

start = time.strftime("%b %d %Y %H:%M:%S")
arquivo_ft = caminho + 'bd/RLCOMRCMPOCDOPE_CARGA_AJT.ft'
df = pd.read_feather(arquivo_ft)

#Filtra os meses e cenarios que estao no arquivos (usado para deletar os registros do DWH)
DELETAR = df[['NOMMES']].drop_duplicates()
DELETAR['NOMMES'] = "'" + DELETAR['NOMMES'] + "'"
conteudo = [tuple(x) for x in DELETAR.values]
print("Registros serao excluidos e carregados ", conteudo)

#Deleta os registros do DWH (Exclui os meses e cenários do arquivo)
cursor = conn.cursor()
sqldel = "delete from DWH.RLCOMRCMPOCDOPE where NOMMES = %s"
for x in conteudo:
    mysql = (sqldel % x)
    cursor.execute(mysql)
    conn.commit()
cursor.close()
conn.close()
print('registros exluidos com sucesso!')

tipo_dados = {"NOMMES": String,
"CODGRPPRD": Integer,
"CODCTGPRD": Integer,
"CODSUBCTGPRD": Integer,
"CODFRN": Integer,
"CODESTUNI": String,
"DESTIPCNLVNDOMR": String,
"VLRVNDFATLIQ": Float,
"VLRRCTLIQAPU": Float,
"VLRMRGBRT": Float,
"VLRMRGCRB": Float}

#Carrega os registros do arquivo no DWH
df.to_sql('rlcomrcmpocdope', connx, schema='dwh', if_exists='append', index=False, chunksize=1000, dtype=tipo_dados)
print('carga efetuada com sucesso!')
print(start, '--', time.strftime("%H:%M:%S"))