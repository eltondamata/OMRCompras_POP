#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
from datetime import date, timedelta
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn

with open('../Parametros/caminho.txt','r') as f:
    caminho = f.read()
with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    NUMANOMESOCD = f.read()
NUMANOMESOCD = int(NUMANOMESOCD)
NUMMESOCD = int(str(NUMANOMESOCD)[-2:])
ANOMES_ini = (date.today().replace(day=1) - timedelta(days=1)).strftime("%Y%m") #Mes Anterior
ANOMES_atu = (date.today().replace(day=1)).strftime("%Y%m") #Mes Atual

#Consulta Orçado (CODCNOOCD = 'OCD')
mysql = (f"""
   SELECT {NUMANOMESOCD} AS NUMANOMESOCD,
          {NUMMESOCD} AS NUMMESOCD,
          SUBCTGPRD.CODGRPPRD, 
          SUBCTGPRD.CODCTGPRD, 
          SUBCTGPRD.CODSUBCTGPRD, 
          DIVFRN.CODDIVFRN, 
          DIVFRN.DESDIVFRN, 
          DIVFRN.NOMGRPECOFRN, 
          t7.CODESTUNI, 
          t6.DESTIPCNLVND AS DESTIPCNLVNDOMR,
          SUBCTGPRD.DESCTGPRD, 
          DIVFRN.CODDRTCLLATU, 
          DIVFRN.DESDRTCLLATU, 
          DIVFRN.DESCLLCMPATU, 
          t4.CODCNOOCD, 
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
        AND t4.CODCNOOCD = 'POP' 
        AND t2.NUMANOMES = {NUMANOMESOCD}
      GROUP BY SUBCTGPRD.CODGRPPRD,
               SUBCTGPRD.CODCTGPRD,
               SUBCTGPRD.CODSUBCTGPRD,
               DIVFRN.CODDIVFRN,
               DIVFRN.DESDIVFRN,
               DIVFRN.NOMGRPECOFRN,
               t7.CODESTUNI,
               t6.DESTIPCNLVND,
               SUBCTGPRD.DESCTGPRD,
               DIVFRN.CODDRTCLLATU,
               DIVFRN.DESDRTCLLATU,
               DIVFRN.DESCLLCMPATU,
               t4.CODCNOOCD
  """)
BSEINIPOP = pd.read_sql(mysql, con=conn)

#Consulta Realizado (CODCNOOCD = 'RLZ')
mysql = (f"""
SELECT {NUMANOMESOCD} AS NUMANOMESOCD, 
          {NUMMESOCD} AS NUMMESOCD,
          SUBCTGPRD.CODGRPPRD, 
          SUBCTGPRD.CODCTGPRD, 
          SUBCTGPRD.CODSUBCTGPRD, 
          DIVFRN.CODDIVFRN, 
          DIVFRN.DESDIVFRN, 
          DIVFRN.NOMGRPECOFRN, 
          t7.CODESTUNI, 
          t6.DESTIPCNLVND AS DESTIPCNLVNDOMR, 
          SUBCTGPRD.DESCTGPRD, 
          DIVFRN.CODDRTCLLATU, 
          DIVFRN.DESDRTCLLATU, 
          DIVFRN.DESCLLCMPATU, 
          t4.CODCNOOCD, 
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
        AND t4.CODCNOOCD = 'RLZ' 
        AND t2.NUMANOMES BETWEEN {ANOMES_ini} AND {ANOMES_atu}
      GROUP BY SUBCTGPRD.CODGRPPRD,
               SUBCTGPRD.CODCTGPRD,
               SUBCTGPRD.CODSUBCTGPRD,
               DIVFRN.CODDIVFRN,
               DIVFRN.DESDIVFRN,
               DIVFRN.NOMGRPECOFRN,
               t7.CODESTUNI,
               t6.DESTIPCNLVND,
               SUBCTGPRD.DESCTGPRD,
               DIVFRN.CODDRTCLLATU,
               DIVFRN.DESDRTCLLATU,
               DIVFRN.DESCLLCMPATU,
               t4.CODCNOOCD
  """)
BSEINIRLZ = pd.read_sql(mysql, con=conn)
conn.close()

key = 'CODDRTCLLATU CODGRPPRD CODCTGPRD CODDIVFRN'.split()
CTGFRNPOP = BSEINIPOP.drop_duplicates(key)[key]
CTGFRNRLZ = BSEINIRLZ.drop_duplicates(key)[key]
CTGFRNRLZi = CTGFRNRLZ.merge(CTGFRNPOP, indicator='i', how='outer').query('i == "left_only"').drop('i', 1)
BSEINIRLZi = BSEINIRLZ.merge(CTGFRNRLZi, how='inner')
valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']

for i in valores:
	BSEINIRLZi[i] = BSEINIRLZi[i].div(1000)

dic_DESTIPCNLVNDOMR = {'B2B':'OUTROS CANAIS', 'E-FÁCIL':'EFACIL'}
BSEINIRLZi['DESTIPCNLVNDOMR'] = BSEINIRLZi['DESTIPCNLVNDOMR'].map(dic_DESTIPCNLVNDOMR).fillna(BSEINIRLZi['DESTIPCNLVNDOMR'])

BASECOMPLETA = pd.concat([BSEINIPOP.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0'), BSEINIRLZi.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0')])

NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
dic_NUMMES = dict(list(enumerate(NOMMES, start=1)))

BASECOMPLETA['NOMMES'] = BASECOMPLETA['NUMMESOCD'].map(dic_NUMMES)

BASECOMPLETA = BASECOMPLETA.groupby(['NOMMES','CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN','DESDIVFRN', 'NOMGRPECOFRN', 'CODESTUNI', 'DESTIPCNLVNDOMR','DESCTGPRD', 'CODDRTCLLATU', 'DESDRTCLLATU','DESCLLCMPATU','CODCNOOCD'])[valores].sum().reset_index()
BASECOMPLETA['VLRCSTMC'] = BASECOMPLETA['VLRMRGCRB'] - BASECOMPLETA['VLRMRGBRT']

valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
DIVFRN_UF = BASECOMPLETA.groupby(['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI'])[valores].sum().reset_index()

print('NUMANOMES:', NUMANOMESOCD)
print(BASECOMPLETA[valores].sum().to_markdown(tablefmt='plsql', floatfmt=',.2f'))
#print(DIVFRN_UF[valores].sum().to_markdown(tablefmt='plsql', floatfmt=',.2f'))

BASECOMPLETA.to_feather(caminho + 'bd/OMR_COMPRAS_OCD.ft')
DIVFRN_UF.to_feather(caminho + 'bd/DIVFRN_UF.ft')