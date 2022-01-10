import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

df = pd.read_pickle(r'..\OMR_COMPRAS_Final.pkl')

print(df[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']].sum())
print(df.groupby('DESTIPCNLVNDOMR')[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']].sum())

