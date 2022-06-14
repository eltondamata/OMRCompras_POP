'''
Autor: elton.mata@martins.com.br
Objetivo: Distribuir a meta (FAT, RL, MB, MC) definida por "Fornecedor x UF x Filial x Canal" no processo anterior para todas as dimensoes do OMR Compras
Dimensoes adicionais no OMR Compras: Categoria > Sub-Categoria
distribuicao proporcional ao valor orcado original = OCD
quando não existe combinacao no OCD, distribui para todas as categorias do fornecedor que estão na base do OMR_COMPRAS_OCD.ft
quando não existe o fornecedor na base OMR_COMPRAS_OCD.ft, associa a meta para a primeira categoria do fornecedor no cadastro de produtos
'''

import pandas as pd
import numpy as np
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()
    
BDCPL = pd.read_feather(caminho + 'bd/OMR_COMPRAS_OCD.ft') #['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'DESCTGPRD', 'CODDRTCLLATU', 'DESDRTCLLATU', 'DESCLLCMPATU', 'CODCNOOCD', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
OMR_FRNUFCNL = pd.read_feather(caminho + 'bd/OMR_FRNUFCNL_POP.ft') #['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
OMR_FRN_FIL = pd.read_feather(caminho + 'bd/OMR_FRN_FIL_POP.ft')
OMR_CODESTUNI = pd.read_feather(caminho + 'bd/OMR_CODESTUNI_POP.ft')
DIMFRNCTG = pd.read_feather(caminho + 'bd/DIMFRNCTG.ft')

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

#confere = DrillSubCategoria.groupby(['CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[['PTC_VLRCSTMC']].sum()
#confere.describe()

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
print('Confere meta total -- Diferença deve ser zero')
confere = pd.DataFrame(OMR_FRNUFCNL[medidas].sum())
confere.columns = ['Arquivo_Vendas']
confere2 = pd.DataFrame(dffim[medidas].sum())
confere2.columns = ['OMR_Compras']
conferefim = confere.join(confere2)
conferefim.eval('Diferenca=OMR_Compras-Arquivo_Vendas', inplace=True)
print(conferefim.to_markdown(tablefmt='github', floatfmt=',.2f', numalign='right'), '\n')

#Export dataset final
dffim.to_feather(caminho + 'bd/OMR_COMPRAS_POP.ft')