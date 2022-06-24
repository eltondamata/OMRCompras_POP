'''
Autor: elton.mata@martins.com.br
Objetivo: Calcular RL, MB, MC para o POP por Fornecedor x UF (Referencia = orcado original OCD)
Dataset final POP DIVFRN x UF com FAT, RL, MB, MC, CSTMC = OMR_FRNUFCNL (Exportado para OMR_FRNUF_POP.pkl)
Pega a descricao da Diretoria e da Celula da base orcado original (OMR_COMPRAS_OCD.pkl), quando ha meta POP definida para fornecedor que nao tem orcado entao pega a descricao do arquivo (Faturamento Compras POP.xlsx)

Glossario:
OCD=Meta do Orcado original (Planejamento Anual)
POP=Meta do Planejamento Operacional
FAT=Faturamento, RL=Receita Liquida, MB=Margem Bruta, MC=Margem de Contribuicao, CSTMC=Custos na Margem de Contribuicao (MB-MC)

==> SEGUNDO PASSO
Objetivo: Distribuir a meta (FAT, RL, MB, MC) definida por "Fornecedor x UF x Filial x Canal" no processo anterior para todas as dimensoes do OMR Compras
Dimensoes adicionais no OMR Compras: Categoria > Sub-Categoria
distribuicao proporcional ao valor orcado original = OCD
quando não existe combinacao no OCD, distribui para todas as categorias do fornecedor que estão na base do OMR_COMPRAS_OCD.ft
quando não existe o fornecedor na base OMR_COMPRAS_OCD.ft, associa a meta para a primeira categoria do fornecedor no cadastro de produtos
'''

import pandas as pd
import numpy as np
import agate
import agateexcel
pd.options.display.float_format = '{:,.2f}'.format

#Import parametro path
with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

#Import datasets 
DIVFRN_UF_FIL_CNL = pd.read_feather(caminho + 'bd/DIVFRN_UF_FIL_CNL.ft') #Fornecedor x UF (FAT, RL, MB, MC) da base orcamento original (OCD). Salva no dataset = DIVFRN_UF_FIL_CNL
DIMFRN = pd.read_feather(caminho + 'bd/DIMFRN.ft') #Usado para relacionar a divisao do fornecedor com a descricao da celula e diretoria
BDCPL = pd.read_feather(caminho + 'bd/OMR_COMPRAS_OCD.ft') #['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'CODDRTCLLATU', 'DESDRTCLLATU', 'DESCLLCMPATU', 'CODCNOOCD', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
DIMFRNCTG = pd.read_feather(caminho + 'bd/DIMFRNCTG.ft')
#Import arquivo com meta definida por Fornecedor, Filial e UF. Salva dados no dataset = FRNFILUF_POP
arquivo = caminho + 'Faturamento Compras POP.xlsx'
planilha = 'URN_UF'
column_arquivo = ['DIRETORIA_VENDA', 'DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODUNDREG', 'CODESTCLI', 'POP']
data_type =      ['string'         , 'string'      , 'string'      , 'int32'    , 'int32'    , 'string'   , 'float']
table = agate.Table.from_xlsx(arquivo, sheet=planilha).select(column_arquivo)
FRNFILUF_POP = pd.DataFrame(table)
FRNFILUF_POP = pd.DataFrame(table.rows, columns=table.column_names)
dic_dtype = dict(zip(column_arquivo, data_type))
FRNFILUF_POP = FRNFILUF_POP.query('~DIRETORIA_VENDA.isnull()', engine='python') #Exclui as linhas em branco importadas do final do arquivo -- linhas vazias sao importadas quando as celulas estao formatadas 
FRNFILUF_POP = FRNFILUF_POP.astype(dtype=dic_dtype)
FRNFILUF_POP.rename(columns={'DIRETORIA_VENDA': 'DESTIPCNLVNDOMR', 'CODUNDREG':'CODFILEPD'}, inplace=True)
FRNFILUF_POP['DESTIPCNLVNDOMR'].replace('ATACADO', 'OUTROS CANAIS', inplace=True)

#Confere valor total
confere = FRNFILUF_POP.groupby('DESDRTCLLATU')[['POP']].sum()
confere.loc['TOTAL'] = confere.sum(axis=0)
print("Fat. POP -- Fonte Arquivo de Vendas")
print(confere.to_markdown(headers=('DIRETORIA','FAT'), tablefmt='github', floatfmt=',.2f'), '\n')

#Agrupa meta POP fornecedor x UF e salva no dataset = AJT_FRNUF
AJT_FRNUF = FRNFILUF_POP.groupby(['CODDIVFRN', 'CODESTCLI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[['POP']].sum().reset_index()
AJT_FRNUF.columns = ['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'FAT']

#junta registros do POP com OCD (Planejamento Operacional com Orcado Original) e salva no dataset = OMR_FRNUF_A
OMR_FRNUF_A = pd.merge(AJT_FRNUF, DIVFRN_UF_FIL_CNL, how='left', on=['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'], indicator='i')

#filtra registros POP sem OCD (Fornecedor x UF). Salva no Dataset = OMR_FRNUF_null
OMR_FRNUF_null = OMR_FRNUF_A[['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'FAT', 'i']].query('i=="left_only"')
#Inclui despcricao da Diretoria e da Celula quando nao existe registro no OCD
OMR_FRNUF_null = pd.merge(DIMFRN, OMR_FRNUF_null, how='inner', on='CODDIVFRN')

#filtra registros comuns POP com OCD (Fornecedor x UF) e salva no dataset = OMR_FRNUF_A
OMR_FRNUF_A = OMR_FRNUF_A.query('i!="left_only"')

#OMR_FRNUF_A = Base que contem os registros comuns POP com OMR Original na combinacao DIVFRN x UF
#OMR_FRNUF_B = Base que contem os registros comuns POP com OMR Original na DIVFRN (e nao estao no OMR_FRNUF_A)
#OMR_FRNUF_C = Base que contem os registros POP que nao tem no OMR Original

#Calcula RL, MB, MC, CSTMC para o POP que possuem registro no OCD por DIVFRN x UF
vlrajt = dict({'RL':'VLRRCTLIQAPU', 'MB':'VLRMRGBRT', 'MC':'VLRMRGCRB', 'CSTMC':'VLRCSTMC'})
for key, value in vlrajt.items():
	OMR_FRNUF_A[key] = OMR_FRNUF_A[value].div(OMR_FRNUF_A['VLRVNDFATLIQ']).mul(OMR_FRNUF_A['FAT'])

#Calcula RL, MB, MC, CSTMC para o POP que possuem registro no OCD por DIVFRN. Nao possuem OCD na combinacao DIVFRN x UF x CANAL.
valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT','VLRMRGCRB','VLRCSTMC']
DIVFRN = DIVFRN_UF_FIL_CNL.groupby('CODDIVFRN')[valores].sum().reset_index()
OMR_FRNUF_B = pd.merge(OMR_FRNUF_null, DIVFRN, how='inner', on='CODDIVFRN')
for key, value in vlrajt.items():
	OMR_FRNUF_B[key] = OMR_FRNUF_B[value].div(OMR_FRNUF_B['VLRVNDFATLIQ']).mul(OMR_FRNUF_B['FAT'])

#Calcula RL, MB, MC, CSTMC para o POP que não tem OCD por DIVFRN. Usa os percentuais (RL, MB, MC / Fat) do valor total OCD
OMR_FRNUF_C = pd.merge(OMR_FRNUF_null, DIVFRN, how='left', on='CODDIVFRN', indicator='i2')
OMR_FRNUF_C.drop(['i', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC'], axis=1, inplace=True)
OMR_FRNUF_C = OMR_FRNUF_C.query('i2=="left_only"')
DIVFRN_UF_FIL_CNL['TOT'] = 'TOT'
OMR_FRNUF_C['TOT'] = 'TOT'
TOTOMR = DIVFRN_UF_FIL_CNL.groupby('TOT')[valores].sum().reset_index()
OMR_FRNUF_C = pd.merge(OMR_FRNUF_C, TOTOMR, how='inner', on='TOT')
for key, value in vlrajt.items():
	OMR_FRNUF_C[key] = OMR_FRNUF_C[value].div(OMR_FRNUF_C['VLRVNDFATLIQ']).mul(OMR_FRNUF_C['FAT'])

#Junta os dataset's usados para calcular a RL, MB, MC, CSTMC do POP (OMR_FRNUF_A + OMR_FRNUF_B + OMR_FRNUF_C)
#Dataset final com RL, MB, MC calculada para POP. Dataset = OMR_FRNUFCNL
OMR_FRNUFCNL = pd.concat([OMR_FRNUF_A, OMR_FRNUF_B, OMR_FRNUF_C])
OMR_FRNUFCNL = OMR_FRNUFCNL[['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'FAT', 'RL', 'MB', 'MC', 'CSTMC']]
OMR_FRNUFCNL.columns = ['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT','VLRMRGCRB','VLRCSTMC']
OMR_FRNUFCNL.reset_index(drop=True, inplace=True)

#Gera dataset's POP agrupado por fornecedor e estado (OMR_FRN = Total por Fornecedor, OMR_CODESTUNI = total por Estado)
#OMR_FRN = POP total por fornecedor
#OMR_CODESTUNI = POP total por fornecedor
#OMR_FRNUFCNL =  POP combinacao FORNECEDOR X UF
OMR_FRN_FIL = OMR_FRNUFCNL.groupby(['CODDIVFRN', 'CODFILEPD'])[valores].sum().reset_index()
OMR_CODESTUNI = OMR_FRNUFCNL.groupby('CODESTUNI')[valores].sum().reset_index()

#Conferencia valor por diretoria
print('Fat. RL MB MC POP -- Proposta de Vendas com abertura até MC')
confere = OMR_FRNUFCNL.groupby('DESDRTCLLATU')[valores].sum()
confere.loc['TOTAL POP'] = confere.sum(axis=0)
confere.loc['TOTAL OCD ORIGINAL'] = DIVFRN_UF_FIL_CNL[valores].sum()
print(confere.reset_index().to_markdown(tablefmt='github', floatfmt=',.2f', index=False),'\n')

##Exporta dataset's para arquivo .feather
#OMR_FRNUFCNL.to_feather(caminho + 'bd/OMR_FRNUFCNL_POP.ft')
#OMR_FRN_FIL.to_feather(caminho + 'bd/OMR_FRN_FIL_POP.ft')
#OMR_CODESTUNI.to_feather(caminho + 'bd/OMR_CODESTUNI_POP.ft')

############################################ SEGUNDO PASSO ##################

#Caluculo subcategoria = percentual de participação da subcategoria no cruzamento (Forn x UF x Filial x Canal) (soma de uma subcategoria no cruzamento(Forn x UF x Filial x Canal) = 1)
#'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'
medidas = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
DrillSubCategoria = BDCPL[['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR']].drop_duplicates()
for medida in medidas:
    DrillMedida = BDCPL.groupby(['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[[medida]].sum().reset_index()
    DrillMedida[f'PTC_{medida}'] = (np.float64(DrillMedida[medida]) / DrillMedida.groupby(['NOMMES', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[medida].transform('sum'))
    DrillMedida[f'PTC_{medida}'] = DrillMedida[f'PTC_{medida}'].fillna(1)
    del DrillMedida[medida]
    DrillSubCategoria = pd.merge(DrillSubCategoria, DrillMedida)

#Calculo Valor FAT, RL, MB, MC subcategoria na base OMR Compras (Quando a combinacao(Forn x UF x Filial x Canal) existir na base) -- Distribui para as categorias faturadas na combinacao (Forn x UF x Filial x Canal)
dfA = pd.merge(OMR_FRNUFCNL, DrillSubCategoria, how='inner', on=['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])
for medida in medidas: 
    dfA[medida] = dfA[medida] * dfA[f'PTC_{medida}']
dfA = dfA[['NOMMES', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']]
    
#Calculo Valor FAT, RL, MB, MC subcategoria na base OMR Compras (Quando a combinacao(Forn x UF x Filial x Canal) NAO existir na base) -- Distribui para todas as categorias do fornecedor
diff = pd.merge(OMR_FRNUFCNL, DrillSubCategoria[['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR']],  indicator='i', how='outer', on=['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR']).query('i == "left_only"').drop('i', 1)    

DrillSubCategoria2 = BDCPL[['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN']].drop_duplicates()
for medida in medidas:
    DrillMedida2 = BDCPL.groupby(['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN'])[[medida]].sum().reset_index()
    DrillMedida2[f'PTC_{medida}'] = (np.float64(DrillMedida2[medida]) / DrillMedida2.groupby(['NOMMES', 'CODDIVFRN'])[medida].transform('sum'))
    DrillMedida2[f'PTC_{medida}'] = DrillMedida2[f'PTC_{medida}'].fillna(1)
    del DrillMedida2[medida]
    DrillSubCategoria2 = pd.merge(DrillSubCategoria2, DrillMedida2)

dfB = pd.merge(diff, DrillSubCategoria2, how='inner', on=['CODDIVFRN'])
for medida in medidas: 
    dfB[medida] = dfB[medida] * dfB[f'PTC_{medida}']
dfB = dfB[['NOMMES', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']]

#Unifica dfA, dfB
dffim = pd.concat([dfA, dfB])

#Atribui -1=NA para as subcategorias que estão no arquivo de vendas e não há referencia na base completa do OMR_Compras
diff2 = pd.merge(OMR_FRNUFCNL, dffim[['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR']],  indicator='i', how='outer', on=['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR']).query('i == "left_only"').drop('i', 1)

#Incluir descricoes no dataset
dimcompras = BDCPL[['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'DESCTGPRD', 'DESDRTCLLATU', 'DESCLLCMPATU']].drop_duplicates()
dffim = pd.merge(dffim, dimcompras)
dffim = dffim[['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'NOMGRPECOFRN', 'DESDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'DESDRTCLLATU', 'DESCLLCMPATU', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']]

#Inclusao dos fornecedores sem referencia de categoria no OMR_Compras (Usa a primeira categoria relacionada ao fornecedor no cadastro de produtos)
DIMFRNCTG = DIMFRNCTG.query('CODSUBCTGPRD!=-1')
DIMFRNCTG = DIMFRNCTG.set_index(['CODDIVFRN'])
DIMFRNCTG = DIMFRNCTG.loc[~DIMFRNCTG.index.duplicated(keep='first')]
DIMFRNCTG = DIMFRNCTG.reset_index()
diff2 = pd.merge(diff2, DIMFRNCTG)
diff2.insert(0, 'NOMMES', list(BDCPL['NOMMES'])[0])
diff2 = diff2[['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'NOMGRPECOFRN', 'DESDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'DESDRTCLLATU', 'DESCLLCMPATU', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']]
dffim = pd.concat([dffim, diff2])
dffim.reset_index(drop=True, inplace=True)

#Confere
print('Confere meta total -- Segundo passo do cálculo -- Diferença deve ser zero')
confere = pd.DataFrame(OMR_FRNUFCNL[medidas].sum())
confere.columns = ['Arquivo_Vendas']
confere2 = pd.DataFrame(dffim[medidas].sum())
confere2.columns = ['OMR_Compras']
conferefim = confere.join(confere2)
conferefim.eval('Diferenca=OMR_Compras-Arquivo_Vendas', inplace=True)
print(conferefim.to_markdown(tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')

#Export dataset final
dffim.to_feather(caminho + 'bd/OMR_COMPRAS_POP.ft')