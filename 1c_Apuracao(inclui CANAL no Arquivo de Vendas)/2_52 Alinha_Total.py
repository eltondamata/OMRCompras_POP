#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format
arquivo_pkl = r'..\RLCOMRCMPOCDOPE_CARGA.pkl'
frncel_pkl = r'..\frncel.pkl'

NUMANOMESOCD = int(open('../NUMANOMESOCD.txt','r').read())
NUMMESOCD = int(str(NUMANOMESOCD)[-2:])
NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
dic_NUMMES = dict(list(enumerate(NOMMES, start=1)))

#Consulta
mysql = (f"""     
SELECT    {NUMANOMESOCD} AS NUMANOMESOCD, 
          {NUMMESOCD} AS NUMMESOCD,
          SUBCTGPRD.CODGRPPRD as CODGRPPRD,
          SUBCTGPRD.CODCTGPRD,
          SUBCTGPRD.CODSUBCTGPRD,
          DIVFRN.CODDIVFRN as CODFRN,
          t7.CODESTUNI,
          t6.DESTIPCNLVNDOMR,
          SUM(t1.VLRVNDFATLIQ) AS VLRVNDFATLIQ,
          SUM(t1.VLRRCTLIQAPU) AS VLRRCTLIQAPU,
          SUM(t1.VLRMRGBRT) AS VLRMRGBRT,
          SUM(t1.VLRMRGCRB) AS VLRMRGCRB
      FROM DWH.FTOOCDMTZRCTCMP t1
         , DWH.DIMPOD t2
         , DWH.DIMTIP t3
         , DWH.DIMCNOOCD t4
         , DWH.DIMPRD DIVFRN
         , DWH.DIMPRD SUBCTGPRD
         , DWH.DIMCNLVND t6
         , DWH.DIMGEO t7
         , DWH.DIMFILFRN t8
         , DWH.DIMFIL t5
      WHERE t1.SRKPODREF = t2.SRKPOD 
        AND t1.SRKTIPOPEVND = t3.SRKTIP 
        AND t1.SRKCNOOCD = t4.SRKCNOOCD 
        AND t1.SRKDIVFRN = DIVFRN.SRKPRD 
        AND t1.SRKSUBCTGPRD = SUBCTGPRD.SRKPRD 
        AND t6.SRKCNLVND = t1.SRKTIPCNLVND 
        AND t1.SRKGEO = t7.SRKGEO 
        AND t1.SRKFILFRN = t8.SRKFILFRN 
        AND t1.SRKFIL = t5.SRKFIL
        AND t3.CODTIP = 'FAT' 
        AND t2.NUMANOMES = {NUMANOMESOCD}
        AND t4.CODCNOOCD = 'POP'
      GROUP BY SUBCTGPRD.CODGRPPRD,
          SUBCTGPRD.CODCTGPRD,
          SUBCTGPRD.CODSUBCTGPRD,
          DIVFRN.CODDIVFRN,
          t7.CODESTUNI,
          t6.DESTIPCNLVNDOMR
  """)
dffto = pd.read_sql(mysql, con=conn)
conn.close()
dffto['DESTIPCNLVNDOMR'] = dffto['DESTIPCNLVNDOMR'].replace({'E-FÁCIL': 'EFACIL'})
dffto['NOMMES'] = dffto['NUMMESOCD'].map(dic_NUMMES)

dfrlc = pd.read_pickle(arquivo_pkl)
frncel = pd.read_pickle(frncel_pkl)
frncel.columns = ['CODFRN', 'DESDRTCLLATU', 'DESCLLCMPATU']

dffto = dffto.merge(frncel, how='inner', on='CODFRN')
dfrlc = dfrlc.merge(frncel, how='inner', on='CODFRN')
dfrlcgrp = dfrlc.groupby(['NOMMES', 'CODESTUNI', 'DESTIPCNLVNDOMR', 'DESDRTCLLATU', 'DESCLLCMPATU'])[['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']].sum().reset_index()

valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']
BDCPL = pd.melt(
  dffto, id_vars=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR', 'DESDRTCLLATU', 'DESCLLCMPATU'],
  value_vars=valores,
  var_name='MEDIDA',
  value_name='DRIVER')

dfrlcgrp = pd.melt(
  dfrlcgrp, id_vars=['NOMMES','CODESTUNI', 'DESTIPCNLVNDOMR', 'DESDRTCLLATU', 'DESCLLCMPATU'],
  value_vars=valores,
  var_name='MEDIDA',
  value_name='VALOR')

dimensoes = ['NOMMES','CODESTUNI', 'DESTIPCNLVNDOMR', 'DESDRTCLLATU', 'DESCLLCMPATU', 'MEDIDA']
BDCPL['DRIVER'] = (BDCPL['DRIVER'] / BDCPL.groupby(dimensoes)['DRIVER'].transform('sum'))
BDCPL = BDCPL.merge(dfrlcgrp, how='inner', on=dimensoes)
BDCPL['DRIVER'] = BDCPL['DRIVER'] * BDCPL['VALOR']
del BDCPL['VALOR']

BDCPL = BDCPL.pivot_table(index=['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR', 'DESDRTCLLATU', 'DESCLLCMPATU', 'MEDIDA'], values='DRIVER', aggfunc=sum).unstack()
BDCPL.columns = BDCPL.columns.get_level_values(1).rename('')
BDCPL = BDCPL.reset_index()

dfcrg = BDCPL[['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR', 'VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']]
dfcrg.to_pickle(r'..\RLCOMRCMPOCDOPE_CARGA_AJT.pkl')

print('BASE CARGA ORIGINAL')
#print(dfrlc.groupby('DESDRTCLLATU')[valores].sum().reset_index().to_string(),'\n')
confere = dfrlc.groupby('DESDRTCLLATU')[valores].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index().to_string(index=False),'\n')

print('BASE CARGA ANTES AJUSTE -- DIRETORIA')
#print(dffto.groupby('DESDRTCLLATU')[valores].sum().reset_index().to_string())
confere = dffto.groupby('DESDRTCLLATU')[valores].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index().to_string(index=False),'\n')

print('BASE CARGA ANTES AJUSTE -- CELULA')
confere = dffto.groupby('DESCLLCMPATU')[valores].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index().to_string(index=False),'\n')

print('BASE CARGA AJUSTADA')
#print(BDCPL.groupby('DESDRTCLLATU')[valores].sum().reset_index().to_string())
confere = BDCPL.groupby('DESDRTCLLATU')[valores].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index().to_string(index=False),'\n')

print('BASE CARGA AJUSTADA -- CELULA')
confere = BDCPL.groupby('DESCLLCMPATU')[valores].sum()
confere.loc['TOTAL',:] = confere.sum()
print(confere.reset_index().to_string(index=False),'\n')