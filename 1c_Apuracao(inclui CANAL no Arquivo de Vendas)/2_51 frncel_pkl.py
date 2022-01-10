#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
OMRPOP_pkl = r'..\OMR_COMPRAS_POP.pkl'

dfpop = pd.read_pickle(OMRPOP_pkl)
frncel = dfpop.drop_duplicates(['CODDIVFRN'])[['CODDIVFRN','DESDRTCLLATU','DESCLLCMPATU']]
frncel.to_pickle(r'..\frncel.pkl')