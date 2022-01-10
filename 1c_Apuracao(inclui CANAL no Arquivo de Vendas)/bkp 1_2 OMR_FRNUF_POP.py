#elton.mata@martins.com.br
#Objetivo: Calcular RL, MB, MC para o POP por Fornecedor x UF (Referencia = orcado original OCD)
#Dataset final POP DIVFRN x UF com FAT, RL, MB, MC, CSTMC = OMR_FRNUF (Exportado para OMR_FRNUF_POP.pkl)
#Pega a descricao da Diretoria e da Celula da base orcado original (OMR_COMPRAS_OCD.pkl), quando ha meta POP definida para fornecedor que nao tem orcado entao pega a descricao do arquivo (Faturamento Compras POP.xlsx)

#Glossario:
#OCD=Meta do Orcado original (Planejamento Anual)
#POP=Meta do Planejamento Operacional
#FAT=Faturamento, RL=Receita Liquida, MB=Margem Bruta, MC=Margem de Contribuicao, CSTMC=Custos na Margem de Contribuicao (MB-MC)

import pandas as pd
import agate
import agateexcel 

#Import arquivo com meta definida por Fornecedor, Filial e UF. Salva dados no dataset = FRNFILUF_POP
arquivo = r'..\Faturamento Compras POP.xlsx'
table = agate.Table.from_xlsx(arquivo, sheet='FILIAL UF').select(["DESDRTCLLATU", "DESCLLCMPATU","CODDIVFRN", "CODUNDREG", "CODESTCLI", "POP"])
table.to_csv(r'..\FRNFILUF_POP.csv')
FRNFILUF_POP = pd.read_csv(r'..\FRNFILUF_POP.csv', encoding="iso-8859-1")

#Confere valor total
df = pd.DataFrame(table)
confere = df.groupby(0)[[5]].sum()
confere.loc['TOTAL'] = confere.sum(axis=0)
print("Fat. POP -- Fonte Arquivo de Vendas")
print(confere.to_markdown(headers=('DIRETORIA','FAT'), tablefmt='github', floatfmt=',.2f'), '\n')

#Import Fornecedor x UF (FAT, RL, MB, MC) da base orcamento original (OCD). Salva no dataset = DIVFRN_UF
DIVFRN_UF = pd.read_pickle(r'..\DIVFRN_UF.pkl')

#Agrupa meta POP fornecedor x UF e salva no dataset = AJT_FRNUF
AJT_FRNUF = FRNFILUF_POP.groupby(['CODDIVFRN','CODESTCLI'])[['POP']].sum().reset_index()
#Pega descricao de Diretoria e Celula do arquivo
DescricaoPOP = FRNFILUF_POP.drop_duplicates(['DESDRTCLLATU', 'DESCLLCMPATU','CODDIVFRN'])[['DESDRTCLLATU', 'DESCLLCMPATU','CODDIVFRN']]
AJT_FRNUF.columns = ['CODDIVFRN', 'CODESTUNI', 'FAT']

#junta registros do POP com OCD (Planejamento Operacional com Orcado Original) e salva no dataset = OMR_FRNUF_A
OMR_FRNUF_A = pd.merge(AJT_FRNUF, DIVFRN_UF, how='left', on=['CODDIVFRN', 'CODESTUNI'], indicator='i')

#filtra registros POP sem OCD (Fornecedor x UF). Salva no Dataset = OMR_FRNUF_null
OMR_FRNUF_null = OMR_FRNUF_A[['CODDIVFRN', 'CODESTUNI', 'FAT', 'i']].query('i=="left_only"')
#Inclui despcricao da Diretoria e da Celula quando nao existe registro no OCD
OMR_FRNUF_null = pd.merge(DescricaoPOP, OMR_FRNUF_null, how='inner', on='CODDIVFRN')

#filtra registros comuns POP com OCD (Fornecedor x UF) e salva no dataset = OMR_FRNUF_A
OMR_FRNUF_A = OMR_FRNUF_A.query('i!="left_only"')

#OMR_FRNUF_A = Base que contem os registros comuns POP com OMR Original na combinacao DIVFRN x UF
#OMR_FRNUF_B = Base que contem os registros comuns POP com OMR Original na DIVFRN (e nao estao no OMR_FRNUF_A)
#OMR_FRNUF_C = Base que contem os registros POP que nao tem no OMR Original

#Calcula RL, MB, MC, CSTMC para o POP que possuem registro no OCD por DIVFRN x UF
vlrajt = dict({'RL':'VLRRCTLIQAPU', 'MB':'VLRMRGBRT', 'MC':'VLRMRGCRB', 'CSTMC':'VLRCSTMC'})
for key, value in vlrajt.items():
	OMR_FRNUF_A[key] = OMR_FRNUF_A[value].div(OMR_FRNUF_A['VLRVNDFATLIQ']).mul(OMR_FRNUF_A['FAT'])

#Calcula RL, MB, MC, CSTMC para o POP que possuem registro no OCD por DIVFRN. Nao possuem OCD na combinacao DIVFRN x UF.
valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT','VLRMRGCRB','VLRCSTMC']
DIVFRN = DIVFRN_UF.groupby('CODDIVFRN')[valores].sum().reset_index()
OMR_FRNUF_B = pd.merge(OMR_FRNUF_null, DIVFRN, how='inner', on='CODDIVFRN')
for key, value in vlrajt.items():
	OMR_FRNUF_B[key] = OMR_FRNUF_B[value].div(OMR_FRNUF_B['VLRVNDFATLIQ']).mul(OMR_FRNUF_B['FAT'])

#Calcula RL, MB, MC, CSTMC para o POP que não tem OCD por DIVFRN. Usa os percentuais (RL, MB, MC / Fat) do valor total OCD
OMR_FRNUF_C = pd.merge(OMR_FRNUF_null, DIVFRN, how='left', on='CODDIVFRN', indicator='i2')
OMR_FRNUF_C.drop(['i', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC'], axis=1, inplace=True)
OMR_FRNUF_C = OMR_FRNUF_C.query('i2=="left_only"')
DIVFRN_UF['TOT'] = 'TOT'
OMR_FRNUF_C['TOT'] = 'TOT'
TOTOMR = DIVFRN_UF.groupby('TOT')[valores].sum().reset_index()
OMR_FRNUF_C = pd.merge(OMR_FRNUF_C, TOTOMR, how='inner', on='TOT')
for key, value in vlrajt.items():
	OMR_FRNUF_C[key] = OMR_FRNUF_C[value].div(OMR_FRNUF_C['VLRVNDFATLIQ']).mul(OMR_FRNUF_C['FAT'])

#Junta os dataset's usados para calcular a RL, MB, MC, CSTMC do POP (OMR_FRNUF_A + OMR_FRNUF_B + OMR_FRNUF_C)
#Dataset final com RL, MB, MC calculada para POP. Dataset = OMR_FRNUF
OMR_FRNUF = pd.concat([OMR_FRNUF_A, OMR_FRNUF_B, OMR_FRNUF_C])
OMR_FRNUF = OMR_FRNUF[['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'FAT', 'RL', 'MB', 'MC', 'CSTMC']]
OMR_FRNUF.columns = ['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT','VLRMRGCRB','VLRCSTMC']

#Gera dataset's POP agrupado por fornecedor e estado (OMR_FRN = Total por Fornecedor, OMR_CODESTUNI = total por Estado)
#OMR_FRN = POP total por fornecedor
#OMR_CODESTUNI = POP total por fornecedor
#OMR_FRNUF =  POP combinacao FORNECEDOR X UF
OMR_FRN = OMR_FRNUF.groupby('CODDIVFRN')[valores].sum().reset_index()
OMR_CODESTUNI = OMR_FRNUF.groupby('CODESTUNI')[valores].sum().reset_index()

#Conferencia valor por diretoria
OMR_DESDRTCLLATU = OMR_FRNUF.groupby('DESDRTCLLATU')[valores].sum().reset_index()
print('Fat. RL MB MC POP -- Proposta de Vendas com abertura até MC')
print(OMR_DESDRTCLLATU.to_markdown(tablefmt='github', floatfmt=',.2f', index=False),'\n')
print(pd.DataFrame(OMR_DESDRTCLLATU[valores].sum()).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'),'\n')
print('Valor Orcado -- Base de Referência')
print(pd.DataFrame(DIVFRN_UF[valores].sum()).transpose().to_markdown(tablefmt='github', floatfmt=',.2f'))

#Exporta dataset's para arquivo .pkl
OMR_FRNUF.to_pickle(r'..\OMR_FRNUF_POP.pkl')
OMR_FRN.to_pickle(r'..\OMR_FRN_POP.pkl')
OMR_CODESTUNI.to_pickle(r'..\OMR_CODESTUNI_POP.pkl')
#OMR_DESDRTCLLATU.to_pickle(r'..\OMR_DESDRTCLLATU.pkl')