#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

OMRPOP_ft = caminho + 'bd/OMR_COMPRAS_POP.ft'

dfpop = pd.read_feather(OMRPOP_ft)
frncel = dfpop.drop_duplicates(['CODDIVFRN'])[['CODDIVFRN','DESDRTCLLATU','DESCLLCMPATU']]
frncel.reset_index(drop=True, inplace=True)
frncel.to_feather(caminho + 'bd/frncel.ft')