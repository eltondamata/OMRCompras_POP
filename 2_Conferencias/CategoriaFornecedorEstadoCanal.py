#elton.mata@matins.com.br

import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

dfajt = pd.read_feather(caminho + 'bd/OMR_COMPRAS_Final.ft')

df = dfajt.groupby(['DESDRTCLLATU', 'DESCTGPRD', 'DESDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT']].sum().reset_index()
df.to_csv(caminho + 'CategoriaFornecedorEstadoCanal.csv', sep=";", encoding="iso-8859-1", decimal=",", float_format='%.2f', date_format='%d/%m/%Y', index=False)

