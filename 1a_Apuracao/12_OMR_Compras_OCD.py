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
          t5.CODFIL AS CODFILEPD, 
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
               t5.CODFIL,
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
          t5.CODFIL AS CODFILEPD,
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
        AND t7.CODESTUNI <> '-3'
        AND t2.NUMANOMES BETWEEN {ANOMES_ini} AND {ANOMES_atu}
      GROUP BY SUBCTGPRD.CODGRPPRD,
               SUBCTGPRD.CODCTGPRD,
               SUBCTGPRD.CODSUBCTGPRD,
               DIVFRN.CODDIVFRN,
               DIVFRN.DESDIVFRN,
               DIVFRN.NOMGRPECOFRN,
               t7.CODESTUNI,
               t5.CODFIL,
               t6.DESTIPCNLVND,
               SUBCTGPRD.DESCTGPRD,
               DIVFRN.CODDRTCLLATU,
               DIVFRN.DESDRTCLLATU,
               DIVFRN.DESCLLCMPATU,
               t4.CODCNOOCD
  """)
BSEINIRLZ = pd.read_sql(mysql, con=conn)

#Cadastro Fornecedor x Celula x Diretoria
mysql = ("""     
   SELECT CODDIVFRN, 
          DESDIVFRN, 
          NOMGRPECOFRN, 
          CODDRTCLLATU, 
          DESDRTCLLATU, 
          DESCLLCMPATU, 
          DATATURGT
      FROM DWH.DIMPRD
      WHERE CODSPRTIPPRD = 'DIVFRN'
      ORDER BY DATATURGT DESC
  """)
dimfrn = pd.read_sql(mysql, con=conn)
dimfrn = dimfrn.set_index('CODDIVFRN')
dimfrn = dimfrn.loc[~dimfrn.index.duplicated(keep='first')]
dimfrn = dimfrn.iloc[:,:-1].reset_index() #não pegar a última coluna

#Cadastro Fornecedor x Categoria x Celula x Diretoria 
mysql = ("""     
   SELECT distinct CODDIVFRN, 
          DESDIVFRN, 
          NOMGRPECOFRN, 
          CODDRTCLLATU, 
          DESDRTCLLATU, 
          DESCLLCMPATU,
          CODGRPPRD,
          CODCTGPRD,
          CODSUBCTGPRD,
          DESCTGPRD,
          DATATURGT
      FROM DWH.DIMPRD
      WHERE CODSPRTIPPRD = 'PRD'
      ORDER BY DATATURGT DESC
  """)
dimfrnctg = pd.read_sql(mysql, con=conn)
dimfrnctg = dimfrnctg.set_index(['CODDIVFRN', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD'])
dimfrnctg = dimfrnctg.loc[~dimfrnctg.index.duplicated(keep='first')]
dimfrnctg = dimfrnctg.iloc[:,:-1].reset_index() #não pegar a última coluna
conn.close()

key = 'CODDRTCLLATU CODGRPPRD CODCTGPRD CODDIVFRN CODFILEPD'.split()
CTGFRNPOP = BSEINIPOP.drop_duplicates(key)[key]
CTGFRNRLZ = BSEINIRLZ.drop_duplicates(key)[key]
CTGFRNRLZi = CTGFRNRLZ.merge(CTGFRNPOP, indicator='i', how='outer').query('i == "left_only"').drop('i', 1)
BSEINIRLZi = BSEINIRLZ.merge(CTGFRNRLZi, how='inner')
valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB']

for i in valores:
	BSEINIRLZi[i] = BSEINIRLZi[i].div(1000)

dic_DESTIPCNLVNDOMR = {'B2B':'OUTROS CANAIS', 'E-FÁCIL':'EFACIL'}
BSEINIRLZi['DESTIPCNLVNDOMR'] = BSEINIRLZi['DESTIPCNLVNDOMR'].map(dic_DESTIPCNLVNDOMR).fillna(BSEINIRLZi['DESTIPCNLVNDOMR'])

BASEINIPOP_MargemNegativa = BSEINIPOP.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT<0')
BASEINIPOP_MargemNegativa.eval('VLRCSTMC=VLRMRGCRB-VLRMRGBRT', inplace=True)
BASEINIPOP_MargemNegativa.eval('VLRMRGBRT=VLRRCTLIQAPU*0.2', inplace=True)
BASEINIPOP_MargemNegativa.eval('VLRMRGCRB=VLRMRGBRT+VLRCSTMC', inplace=True)
del BASEINIPOP_MargemNegativa['VLRCSTMC']
BSEINIPOP = BSEINIPOP.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0')
BSEINIPOP = pd.concat([BSEINIPOP, BASEINIPOP_MargemNegativa])

#Incluir registros com Margem Negativa, apos ajustar a Margem para 20% (Objetivo: ter referencia para orçamento desses fornecedores, sem gerar margem negativa)
BASEINIRLZ_MargemNegativa = BSEINIRLZi.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT<0')
BASEINIRLZ_MargemNegativa.eval('VLRCSTMC=VLRMRGCRB-VLRMRGBRT', inplace=True)
BASEINIRLZ_MargemNegativa.eval('VLRMRGBRT=VLRRCTLIQAPU*0.2', inplace=True)
BASEINIRLZ_MargemNegativa.eval('VLRMRGCRB=VLRMRGBRT+VLRCSTMC', inplace=True)
del BASEINIRLZ_MargemNegativa['VLRCSTMC']
BSEINIRLZi = BSEINIRLZi.query('VLRVNDFATLIQ>0 & VLRRCTLIQAPU>0 & VLRMRGBRT>0')
BSEINIRLZi = pd.concat([BSEINIRLZi, BASEINIRLZ_MargemNegativa])

#Inclui registros realizado no dataset do OMR_COMPRAS (Objetivo: ter referencia para orçar fornecedores e categorias novas)
OMR_COMPRAS_OCD = pd.concat([BSEINIPOP, BSEINIRLZi])

NOMMES = 'Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez'.split()
dic_NUMMES = dict(list(enumerate(NOMMES, start=1)))

OMR_COMPRAS_OCD['NOMMES'] = OMR_COMPRAS_OCD['NUMMESOCD'].map(dic_NUMMES)

OMR_COMPRAS_OCD = OMR_COMPRAS_OCD.groupby(['NOMMES', 'CODGRPPRD', 'CODCTGPRD', 'CODSUBCTGPRD', 'CODDIVFRN', 'DESDIVFRN', 'NOMGRPECOFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR','DESCTGPRD', 'CODDRTCLLATU', 'DESDRTCLLATU','DESCLLCMPATU','CODCNOOCD'])[valores].sum().reset_index()
OMR_COMPRAS_OCD['VLRCSTMC'] = OMR_COMPRAS_OCD['VLRMRGCRB'] - OMR_COMPRAS_OCD['VLRMRGBRT']

valores = ['VLRVNDFATLIQ', 'VLRRCTLIQAPU', 'VLRMRGBRT', 'VLRMRGCRB', 'VLRCSTMC']
DIVFRN_UF_FIL_CNL = OMR_COMPRAS_OCD.groupby(['DESDRTCLLATU', 'DESCLLCMPATU', 'CODDIVFRN', 'CODESTUNI', 'CODFILEPD', 'DESTIPCNLVNDOMR'])[valores].sum().reset_index()

print('NUMANOMES:', NUMANOMESOCD)
print(OMR_COMPRAS_OCD[valores].sum().to_markdown(tablefmt='plsql', floatfmt=',.2f'))
#print(DIVFRN_UF_CNL[valores].sum().to_markdown(tablefmt='plsql', floatfmt=',.2f'))

#Export datasets
OMR_COMPRAS_OCD.to_feather(caminho + 'bd/OMR_COMPRAS_OCD.ft')
DIVFRN_UF_FIL_CNL.to_feather(caminho + 'bd/DIVFRN_UF_FIL_CNL.ft')
dimfrn.to_feather(caminho + 'bd/DIMFRN.ft')
dimfrnctg.to_feather(caminho + 'bd/DIMFRNCTG.ft') #datset usado no processo "14_OMR_COMPRAS_POP.py"