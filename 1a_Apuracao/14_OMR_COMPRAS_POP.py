#elton.mata@martins.com.br
#Objetivo: Distribuir a meta (FAT, RL, MB, MC) definida por Fornecedor e UF no processo anterior para todas as dimensoes do OMR Compras
#distribuicao proporcional ao valor orcado original = OCD

import pandas as pd

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()
    
BDCPL = pd.read_feather(caminho + 'bd/OMR_COMPRAS_OCD.ft')
OMR_FRNUFCNL = pd.read_feather(caminho + 'bd/OMR_FRNUFCNL_POP.ft')
OMR_FRN_FIL = pd.read_feather(caminho + 'bd/OMR_FRN_FIL_POP.ft')
OMR_CODESTUNI = pd.read_feather(caminho + 'bd/OMR_CODESTUNI_POP.ft')

valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRCSTMC']

#Base completa OMR_COMPRAS
BDCPL = pd.melt(
	BDCPL, id_vars=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'DESDRTCLLATU', 'DESCLLCMPATU'],
	value_vars=valores,
	var_name='MEDIDA',
	value_name='DRIVER')
#print('\n', "OMR_COMPRAS OCD -- Fonte: Base Completa")
#confere = BDCPL.pivot_table(index=['DESDRTCLLATU','MEDIDA'], values='DRIVER', aggfunc=sum)
#print(confere.unstack().to_markdown(tablefmt='github', floatfmt=',.2f'))
#print(confere.pivot_table(index=['MEDIDA'], values='DRIVER', aggfunc=sum).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

#OMR Fornecedor x UF
OMR_FRNUFCNL = pd.melt(
	OMR_FRNUFCNL, id_vars=['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'],
	value_vars=valores,
	var_name='MEDIDA',
	value_name='VALOR')
print("OMR Fornecedor x UF POP -- Fonte: Arquivo de Vendas após abertura RL MB e MC")
confere = OMR_FRNUFCNL.pivot_table(index=['DESDRTCLLATU','MEDIDA'], values='VALOR', aggfunc=sum)
print(confere.unstack().to_markdown(tablefmt='github', floatfmt=',.2f'))
print(confere.pivot_table(index=['MEDIDA'], values='VALOR', aggfunc=sum).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

#OMR Fornecedor x Filial
OMR_FRN_FIL = pd.melt(
	OMR_FRN_FIL, id_vars=['CODDIVFRN', 'CODFILEPD'],
	value_vars=valores,
	var_name='MEDIDA',
	value_name='VALOR')
#print("OMR Fornecedor POP")
#confere = OMR_FRN.pivot_table(index=['MEDIDA'], values='VALOR', aggfunc=sum)
#print(confere.transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

#OMR Estado
OMR_CODESTUNI = pd.melt(
	OMR_CODESTUNI, id_vars=['CODESTUNI'],
	value_vars=valores,
	var_name='MEDIDA',
	value_name='VALOR')
#print("OMR Estado POP")
#confere = OMR_CODESTUNI.pivot_table(index=['MEDIDA'], values='VALOR', aggfunc=sum)
#print(confere.transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')


#Base Completa após Distribuir Fornecedor x UF x Filial
dimensoes = ['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'MEDIDA']
BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
BDCPL = BDCPL.merge(OMR_FRNUFCNL, how='inner', on=dimensoes)
BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
del BDCPL['VALOR']
#print('\n', "ATENCAO == OMR Compras POP -- após distribuir Proposta de Vendas na Base Completa")
#confere = BDCPL.pivot_table(index=['DESDRTCLLATU','MEDIDA'], values='DRIVER', aggfunc=sum)
#print(confere.unstack().to_markdown(tablefmt='github', floatfmt=',.2f'))
#print(confere.pivot_table(index=['MEDIDA'], values='DRIVER', aggfunc=sum).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

print('Calculando Breakback DIVFRN CELULA e UF, AGUARDE...')
#BREAKBACK DIVFRN e UF
for x in range(5):
	#Distribui ESTADO
	dimensoes = ['CODESTUNI', 'MEDIDA']
	BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
	BDCPL = BDCPL.merge(OMR_CODESTUNI, how='inner', on=dimensoes)
	BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
	del BDCPL['VALOR']

	#Distribui FORNECEDOR x FILIAL
	dimensoes = ['CODDIVFRN', 'CODFILEPD', 'MEDIDA']
	BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
	BDCPL = BDCPL.merge(OMR_FRN_FIL, how='inner', on=dimensoes)
	BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
	del BDCPL['VALOR']
#print('\n', "OMR Compras POP -- após BREAKBACK alinhamento DIVFRN e UF")
#confere = BDCPL.pivot_table(index=['DESDRTCLLATU','MEDIDA'], values='DRIVER', aggfunc=sum)
#print(confere.unstack().to_markdown(tablefmt='github', floatfmt=',.2f'))
#print(confere.pivot_table(index=['MEDIDA'], values='DRIVER', aggfunc=sum).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

#BREAKBACK CELULA e UF
#Objetivo alinhar o total da celula e total do estado (distribui as diferencas nos cruzamentos)
OMR_CEL = OMR_FRNUFCNL.groupby(['DESCLLCMPATU', 'DESTIPCNLVNDOMR','MEDIDA'])[['VALOR']].sum().reset_index()
for x in range(50):
	#Distribui ESTADO
	dimensoes = ['CODESTUNI', 'MEDIDA']
	BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
	BDCPL = BDCPL.merge(OMR_CODESTUNI, how='inner', on=dimensoes)
	BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
	del BDCPL['VALOR']

	#Distribui CELULA X CANAL
	dimensoes = ['DESCLLCMPATU', 'DESTIPCNLVNDOMR', 'MEDIDA']
	BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
	BDCPL = BDCPL.merge(OMR_CEL, how='inner', on=dimensoes)
	BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
	del BDCPL['VALOR']
#print('\n', "OMR Compras POP -- após BREAKBACK CELULA e UF")
print('\n', "OMR Compras POP -- BASE FINAL CALCULADA")
confere = BDCPL.pivot_table(index=['DESDRTCLLATU','MEDIDA'], values='DRIVER', aggfunc=sum)
print(confere.unstack().to_markdown(tablefmt='github', floatfmt=',.2f'))
print(confere.pivot_table(index=['MEDIDA'], values='DRIVER', aggfunc=sum).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')

#Gera arquivo formato tabela de carga dwh.RLCOMRCMPOCDOPE
BDCPL = BDCPL.pivot_table(index=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'NOMGRPECOFRN', 'DESDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'DESDRTCLLATU', 'DESCLLCMPATU', 'MEDIDA'], values='DRIVER', aggfunc=sum).unstack()
BDCPL.columns = BDCPL.columns.get_level_values(1).rename('')
BDCPL = BDCPL.reset_index()
BDCPL['VLRMRGCRB'] = BDCPL['VLRMRGBRT'] + BDCPL['VLRCSTMC']

#Conferencia total UF
pd.options.display.float_format = '{:,.2f}'.format
dfufori = OMR_FRNUFCNL.query('MEDIDA=="VLRVNDFATLIQ"').groupby(['CODESTUNI'])['VALOR'].sum()
dfuffim = BDCPL.groupby(['CODESTUNI'])['VLRVNDFATLIQ'].sum()
print('Conferencia Faturamento por UF')
totuf = pd.merge(dfufori, dfuffim, how='inner', on='CODESTUNI').reset_index()
totuf.columns = ['CODESTUNI', 'FAT ORIGEM', 'FAT FINAL']
print(totuf,'\n')

#Conferencia total Filial
pd.options.display.float_format = '{:,.2f}'.format
dfufori = OMR_FRNUFCNL.query('MEDIDA=="VLRVNDFATLIQ"').groupby(['CODFILEPD'])['VALOR'].sum()
dfuffim = BDCPL.groupby(['CODFILEPD'])['VLRVNDFATLIQ'].sum()
print('Conferencia Faturamento por Filial -- (Nao tem que bater, apenas aproxima)')
totuf = pd.merge(dfufori, dfuffim, how='inner', on='CODFILEPD').reset_index()
totuf.columns = ['CODFILEPD', 'FAT ORIGEM', 'FAT FINAL']
print(totuf,'\n')

#Conferencia total CELULA
dfori = OMR_FRNUFCNL.query('MEDIDA=="VLRVNDFATLIQ"').groupby(['DESCLLCMPATU'])['VALOR'].sum()
dffim = BDCPL.groupby(['DESCLLCMPATU'])['VLRVNDFATLIQ'].sum()
print('Conferencia Faturamento por CELULA (TEM QUE BATER)')
totuf = pd.merge(dfori, dffim, how='outer', on='DESCLLCMPATU')
totuf.loc['TOTAL'] = totuf.sum(axis=0, numeric_only=True)
totuf = totuf.reset_index()
totuf.columns = ['DESCLLCMPATU', 'FAT ORIGEM', 'FAT FINAL']
print(totuf.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'),'\n')

#Conferencia total CANAL
dfori = OMR_FRNUFCNL.query('MEDIDA=="VLRVNDFATLIQ"').groupby(['DESTIPCNLVNDOMR'])['VALOR'].sum()
dffim = BDCPL.groupby(['DESTIPCNLVNDOMR'])['VLRVNDFATLIQ'].sum()
print('Conferencia Faturamento por CANAL (TEM QUE BATER)')
totuf = pd.merge(dfori, dffim, how='inner', on='DESTIPCNLVNDOMR')
totuf.loc['TOTAL'] = totuf.sum(axis=0, numeric_only=True)
totuf = totuf.reset_index()
totuf.columns = ['DESTIPCNLVNDOMR', 'FAT ORIGEM', 'FAT FINAL']
print(totuf.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'),'\n')

#Conferencia total FORNECEDOR (Top 20)
dfori = OMR_FRNUFCNL.query('MEDIDA=="VLRVNDFATLIQ"').groupby(['CODDIVFRN'])['VALOR'].sum().reset_index()
dffim = BDCPL.groupby(['CODDIVFRN','DESDIVFRN'])['VLRVNDFATLIQ'].sum().reset_index()
print('Conferencia Faturamento por FORNECEDOR (TOP 20) -- Nao tem objetivo de bater, apenas aproximar do valor original')
print('Divergencia por fornecedor ocorre quando é definido meta para fornecedor sem referencia historica, processo alinha no total da celula e distribui diferença para todos os fornecedores')
dftot = pd.merge(dfori, dffim, how='inner', on='CODDIVFRN').reset_index()[['CODDIVFRN', 'DESDIVFRN', 'VALOR', 'VLRVNDFATLIQ']]
dftot.columns = ['CODDIVFRN', 'DESDIVFRN', 'FAT ORIGEM', 'FAT FINAL']
print(dftot.sort_values(by='FAT FINAL', ascending=False).head(20),'\n')

#Export dataset OMR_COMPRAS_POP (Meta POP aberta em todas as dimensoes do OMR_Compras)
BDCPL.to_feather(caminho + 'bd/OMR_COMPRAS_POP.ft')
print('CONCLUIDO!!!')