#elton.mata@matins.com.br
#Aplica mesmo %MB da Subcategoria x Fornecedor x Canal para todos os estados
#Essa regra foi incluida no processo para reduzir as variacoes da MB de uma mesma categoria entre os estados.
#Quando estava sendo usado o %MB por estado do orcado (ou mesmo do realizado), as categorias de MG ja estao com %MB menor que os demais e ao aplicar o Breakback para alinhar com a Margem do estado faz com que as categorias com margem menor fiquem ainda menor para alinhar os totais, partindo da base por categoria com a mesma margem havera queda na margem da catgoria em MG partindo da margem definida no total da categoria, o que reduz as variacoes nessas categorias de menor margem para estados com margem menor, e na situacao inversa nos estados de maior margem (PA) reduz a distorcao nas categorias de maior margem.
#O %MB nesse nivel de detalhe Subcategoria x UF e usado pela area de price para definir a margem objetiva de precificacao, e essa demanda para ter oscilacao menor da mesma categoria entre os estados veio de uma demanda de price (Reuniao com Vanessa e Jacqueline em 30/set/2021)

import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

df = pd.read_pickle(r'..\OMR_COMPRAS_POP.pkl')

#inserido para garantir que nao tenha valor negativo de fat rl mb (arquivo de vendas forn x filial x uf veio com fat negativo no pop de nov21)
df = df.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0')

#Calculo %MargemBruta e %CustoMC por Subcategoria x Fornecedor
df2 = df.groupby(['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESTIPCNLVNDOMR'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRCSTMC', 'VLRMRGCRB']].sum().reset_index()
df2.eval('MB=VLRMRGBRT/VLRRCTLIQAPU', inplace=True)
#df2.eval('MB=VLRMRGBRT/VLRRCTLIQAPU + 0.05', inplace=True)
df2.eval('CST=VLRCSTMC/VLRRCTLIQAPU', inplace=True)

#Aplica mesmo %MargemBruta e %CustoMC da SubcategoriaxFornecedor para todas as demais combninacoes
df = pd.merge(df, df2[['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESTIPCNLVNDOMR', 'MB', 'CST']])
df.eval('VLRMRGBRT=VLRRCTLIQAPU*MB', inplace=True)
df.eval('VLRCSTMC=VLRRCTLIQAPU*CST', inplace=True)
df.eval('VLRMRGCRB=VLRMRGBRT+VLRCSTMC', inplace=True)

print('Aplica mesmo %MB das Subcategorias x Fornecedor x Canal para todos os estados')
print('Novo dataset gerado: OMR_COMPRAS_POPAJT.pkl')
df.iloc[:,:-2].to_pickle(r'..\OMR_COMPRAS_POPAJT.pkl')
