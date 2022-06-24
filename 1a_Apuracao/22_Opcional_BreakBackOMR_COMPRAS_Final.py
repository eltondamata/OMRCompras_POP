#elton.mata@martins.com.br
'''
Processo para retorno das metas definidas no arquivo "OMR_CategoriaFornecedorEstadoCanal.xlsx"
Executar esse processo apenas caso as metas sejam definidas por esse arquivo.
Se a meta for definida pelo arquivo "Plan_Operacional_CARGA.xlsx" executar esse outro processo "22_BreakBackOMR_COMPRAS_Final.py"

Gera base de carga OMR Compras POP (alem das dimensoes do arquivo abre a meta por subcategoria e filial)
'''

import pandas as pd
import numpy as np
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

#Dataset e arquivos import
Planilha_Contribuicao = (caminho + 'OMR_CategoriaFornecedorEstadoCanal_CARGA.xlsx')
omrcmp = pd.read_feather(caminho + 'bd/OMR_COMPRAS_POPAJT.ft')

valores_calc = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRCSTMC']
df = pd.read_excel(Planilha_Contribuicao, 'VAREJO', skiprows=6, usecols="B:K,O:Q")
df.insert(0,'DESDRTCLLATU','VAREJO ALIMENTAR E FARMA')
df1 = pd.read_excel(Planilha_Contribuicao, 'ELETRO', skiprows=6, usecols="B:K,O:Q")
df1.insert(0,'DESDRTCLLATU','ELETRO')
df = df.append(df1)
df1 = pd.read_excel(Planilha_Contribuicao, 'MARTCON', skiprows=6, usecols="B:K,O:Q")
df1.insert(0,'DESDRTCLLATU','MARTCON/AGROVET')
df = df.append(df1)
df = df.query('~FAT.isnull()', engine='python') #eliminar linhas com valores nulos
df.rename(columns={'CODFRN':'CODDIVFRN', 'Célula':'DESCLLCMPATU', 'Estado':'CODESTUNI', 'Canal':'DESTIPCNLVNDOMR', 'FAT':'VLRVNDFATLIQ', 'RL':'VLRRCTLIQAPU', 'MB':'VLRMRGBRT', 'MC':'VLRMRGCRB'}, inplace=True)
df[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT', 'VLRMRGCRB']] = df[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT', 'VLRMRGCRB']].mul(1000)
df['VLRCSTMC'] = df['VLRMRGCRB'] - df['VLRMRGBRT']
df['DESTIPCNLVNDOMR'].replace('ATACADO', 'OUTROS CANAIS', inplace=True)

print('-------------------------------------- IMPUTS --------------------------------------')
print('\nVALOR IMPORTADO DO ARQUIVO EXCEL -- OMR_CategoriaFornecedorEstadoCanal_CARGA.xlsx') 
#DIRETORIA
confere = df.groupby(['DESDRTCLLATU'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT', 'VLRMRGCRB']].sum()
confere.loc['TOTAL'] = confere.iloc[:,-4:].sum(axis=0)
confere = confere.reset_index()
print(confere.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')
#CANAL
confere = df.groupby(['DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT', 'VLRMRGCRB']].sum()
confere.loc['TOTAL'] = confere.iloc[:,-4:].sum(axis=0)
confere = confere.reset_index()
print(confere.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')

df = pd.melt(
	df, id_vars=['DESDRTCLLATU', 'CODGRPPRD', 'CODCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR'],
	value_vars=valores_calc,
	var_name='MEDIDA',
	value_name='VALOR')

#transpor medidas de coluna para linha OMR_COMPRAS e salva no dataset = df_full
#df_full = omrcmp.groupby(['DESDRTCLLATU', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'DESCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']].sum().reset_index()
df_full = omrcmp.groupby(['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'DESCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'DESDRTCLLATU', 'DESCLLCMPATU', 'DESTIPCNLVNDOMR', 'CODESTUNI', 'CODFILEPD'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']].sum().reset_index()
df_full.eval('VLRCSTMC=VLRMRGCRB-VLRMRGBRT', inplace=True)
df_full = pd.melt(
	df_full, id_vars=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'DESCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'DESDRTCLLATU', 'DESCLLCMPATU', 'DESTIPCNLVNDOMR', 'CODESTUNI', 'CODFILEPD'],
	value_vars=valores_calc,
	var_name='MEDIDA',
	value_name='DRIVER')

#Base Completa após Distribuir o valor de DIRETORIA x CATEGORIA x FORN na base completa
df_full['DRIVER'] = (df_full['DRIVER'] / df_full.groupby(['DESDRTCLLATU', 'CODGRPPRD', 'CODCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR','MEDIDA'])['DRIVER'].transform('sum'))
df_full = df_full.merge(df, how='inner', on=['DESDRTCLLATU', 'CODGRPPRD', 'CODCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR','MEDIDA'])
df_full['DRIVER'] = df_full['DRIVER'] * df_full['VALOR']
del df_full['VALOR']

#Transpor linhas para colunas no dataset OMR_Compras (base completa)
df_full = df_full.pivot_table(index=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'DESCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'DESDRTCLLATU', 'DESCLLCMPATU', 'DESTIPCNLVNDOMR', 'CODESTUNI', 'CODFILEPD'], values='DRIVER', columns=['MEDIDA'], aggfunc=sum).reset_index()
df_full = df_full.query('VLRVNDFATLIQ>0')
df_full.eval('VLRMRGCRB=VLRMRGBRT+VLRCSTMC', inplace=True)
df_full.to_feather(caminho + 'bd/OMR_COMPRAS_Final.ft')

print('-------------------------------------- CONFERENCIA BASES DE CARGA CALCULADA --------------------------------------')
print('\n', "==> OMR COMPRAS FINAL") 
#FILIAL
confere = df_full.groupby(['CODFILEPD'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.to_markdown(tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')
#DIRETORIA
confere = df_full.groupby(['DESDRTCLLATU'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.to_markdown(tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')
#Gera arquivo formato tabela de carga dwh.RLCOMRCMPOCDOPE
df_full = df_full.groupby(['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum().reset_index()
df_full.rename(columns={'CODDIVFRN':'CODFRN'}, inplace=True)
#CANAL
confere = df_full.groupby(['DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.to_markdown(tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')

#Confere os cinco maiores e menores registros da tabela de carga
print('\n', "TABELA DE CARGA (Cinco Maiores e Menores registros no dataset de carga)")
print(df_full.nlargest(5, 'VLRVNDFATLIQ').to_string(index=False))
print(df_full.nsmallest(5, 'VLRVNDFATLIQ').to_string(index=False),'\n')
print('\n', "==> Describe do dataset de carga (count: 80~90 mil; min: não pode ser negativo para FAT, RL, MB)")
print(df_full.describe().to_string())

df_full.to_feather(caminho + 'bd/RLCOMRCMPOCDOPE_CARGA.ft')
print("Dataset gerado: OMR_COMPRAS_Final.ft")
print("Dataset gerado: RLCOMRCMPOCDOPE_CARGA.ft")