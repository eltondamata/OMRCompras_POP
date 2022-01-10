#elton.mata@matins.com.br

import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

dfajt = pd.read_pickle(r'..\OMR_COMPRAS_Final.pkl')

df = dfajt.groupby(['DESDRTCLLATU', 'DESCTGPRD', 'DESDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT']].sum().reset_index()
df.to_csv(r'..\CategoriaFornecedorEstadoCanal.csv', sep=";", encoding="iso-8859-1", decimal=",", float_format='%.2f', date_format='%d/%m/%Y', index=False)

