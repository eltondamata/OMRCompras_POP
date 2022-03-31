#elton.mata@matins.com.br
#Aplica mesmo %MB da Subcategoria x Fornecedor x Canal para todos os estados
#Essa regra foi incluida no processo para reduzir as variacoes da MB de uma mesma categoria entre os estados.
#Quando estava sendo usado o %MB por estado do orcado (ou mesmo do realizado), as categorias de MG ja estao com %MB menor que os demais e ao aplicar o Breakback para alinhar com a Margem do estado faz com que as categorias com margem menor fiquem ainda menor para alinhar os totais, partindo da base por categoria com a mesma margem havera queda na margem da catgoria em MG partindo da margem definida no total da categoria, o que reduz as variacoes nessas categorias de menor margem para estados com margem menor, e na situacao inversa nos estados de maior margem (PA) reduz a distorcao nas categorias de maior margem.
#O %MB nesse nivel de detalhe Subcategoria x UF e usado pela area de price para definir a margem objetiva de precificacao, e essa demanda para ter oscilacao menor da mesma categoria entre os estados veio de uma demanda de price (Reuniao com Vanessa e Jacqueline em 30/set/2021)

import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()

df = pd.read_feather(caminho + 'bd/OMR_COMPRAS_POP.ft')

#inserido para garantir que nao tenha valor negativo de fat rl mb (arquivo de vendas forn x filial x uf veio com fat negativo no pop de nov21)
df = df.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0')

#Calculo %MargemBruta e %CustoMC por Subcategoria x Fornecedor
df2 = df.groupby(['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRCSTMC', 'VLRMRGCRB']].sum().reset_index()
df2.eval('MB=VLRMRGBRT/VLRRCTLIQAPU', inplace=True)
#df2.eval('MB=VLRMRGBRT/VLRRCTLIQAPU + 0.05', inplace=True)
df2.eval('CST=VLRCSTMC/VLRRCTLIQAPU', inplace=True)

#Linhas de 25 a 34 icluídas no código para atender a demanda do email 30/03/2022 da Vanessa Price -- igualar a Margem Bruta da subcategoria do Leite Molico com a subcategoria do Leite Ninho)
#Ajusta a Margem Bruta das subcategorias 8=LEITE PO DESNATADO(Leite Molico) e 9=LEITE PO INTEGRAL/INSTANTANEO(Leite Ninho) para 16% apenas fornecedor Nestle
dfajt = df2.query('CODGRPPRD==43 & CODCTGPRD==22 & CODDIVFRN==96650 and DESTIPCNLVNDOMR=="OUTROS CANAIS" and CODSUBCTGPRD in [8,9]')
dfajt.eval('VLRMRGBRT=VLRRCTLIQAPU*0.16', inplace=True)
dfajt.eval('VLRMRGCRB=VLRRCTLIQAPU*CST+VLRMRGBRT', inplace=True)
dfajt.eval('MB=VLRMRGBRT/VLRRCTLIQAPU', inplace=True)
dfajt.eval('CST=VLRCSTMC/VLRRCTLIQAPU', inplace=True)

#df2 altera o dataset completo com ajuste da Margem no Leite em pó (passo anterior)
df2 = df2.query('~(CODGRPPRD==43 & CODCTGPRD==22 & CODDIVFRN==96650 and DESTIPCNLVNDOMR=="OUTROS CANAIS" and CODSUBCTGPRD in [8,9])', engine='python')
df2 = pd.concat([df2, dfajt])

#Aplica mesmo %MargemBruta e %CustoMC da SubcategoriaxFornecedor para todas as demais combninacoes
df = pd.merge(df, df2[['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESTIPCNLVNDOMR', 'MB', 'CST']])
df.eval('VLRMRGBRT=VLRRCTLIQAPU*MB', inplace=True)
df.eval('VLRCSTMC=VLRRCTLIQAPU*CST', inplace=True)
df.eval('VLRMRGCRB=VLRMRGBRT+VLRCSTMC', inplace=True)

print('Aplica mesmo %MB das Subcategorias x Fornecedor x Canal para todos os estados')
print('Novo dataset gerado: OMR_COMPRAS_POPAJT.ft')
df.iloc[:,:-2].to_feather(caminho + 'bd/OMR_COMPRAS_POPAJT.ft')
