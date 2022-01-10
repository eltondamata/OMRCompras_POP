#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format
NUMANOMESOCD = int(open('../NUMANOMESOCD.txt','r').read())

#Consulta
mysql = (f"""     
SELECT SUBCTGPRD.CODGRPPRD 
     , SUBCTGPRD.CODCTGPRD
     , SUBCTGPRD.CODSUBCTGPRD
     , DIVFRN.CODDIVFRN
     , DIVFRN.NOMGRPECOFRN
     , DIVFRN.DESDIVFRN
     , t7.CODESTUNI
     , t6.DESTIPCNLVNDOMR
     , SUBCTGPRD.DESCTGPRD
     , DIVFRN.DESDRTCLLATU
     , DIVFRN.DESCLLCMPATU
     , SUM(t1.VLRVNDFATLIQ) AS VLRVNDFATLIQ
     , SUM(t1.VLRRCTLIQAPU) AS VLRRCTLIQAPU
     , SUM(t1.VLRMRGBRT) AS VLRMRGBRT
     , SUM(t1.VLRMRGCRB) AS VLRMRGCRB
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
GROUP BY SUBCTGPRD.CODGRPPRD 
       , SUBCTGPRD.CODCTGPRD
       , SUBCTGPRD.CODSUBCTGPRD
       , DIVFRN.CODDIVFRN
       , DIVFRN.NOMGRPECOFRN
       , DIVFRN.DESDIVFRN
       , t7.CODESTUNI
       , t6.DESTIPCNLVNDOMR
       , SUBCTGPRD.DESCTGPRD
       , DIVFRN.DESDRTCLLATU
       , DIVFRN.DESCLLCMPATU
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

df['DESTIPCNLVNDOMR'].replace('E-FÁCIL', 'EFACIL', inplace=True)

#carga = pd.read_pickle(r'..\OMR_COMPRAS_POP.pkl')
carga = pd.read_pickle(r'..\RLCOMRCMPOCDOPE_CARGA.pkl')
carga = carga.query('VLRVNDFATLIQ>0')
carga.rename(columns={'CODFRN':'CODDIVFRN'}, inplace=True)

dfdif = pd.merge(carga, df[['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR']],  indicator='i', how='outer', on=['CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR']).query('i == "left_only"').drop('i', 1)

dfdif.to_csv(r'..\Registros_RLC nao carregados.csv', sep=";", encoding="iso-8859-1", decimal=",", float_format='%.2f', date_format='%d/%m/%Y', index=False)
