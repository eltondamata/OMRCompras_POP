#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format

dfOCD = pd.read_pickle(r'X:\PLANEJAMENTO\2022\07 Alinha MC DRE\RLCOMRCMPOCDOPE_CARGA.pkl')
dfPOP = pd.read_pickle(r'X:\PLANEJAMENTO\2022\PLAN_OPERACIONAL\202201\OMRCompras_POP\RLCOMRCMPOCDOPE_CARGA.pkl')

#Consulta
mysql = (f"""     
SELECT t4.CODCNOOCD, 
          t2.NUMANOMES, 
          t5.CODFIL, 
          t5.DESFIL,
          DIVFRN.CODDIVFRN,
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
        AND t2.NUMANOMES = 202201
        AND t4.CODCNOOCD in ('POP', 'OCD')
      GROUP BY t4.CODCNOOCD,
               t2.NUMANOMES,
               t5.CODFIL,
               t5.DESFIL,
               DIVFRN.CODDIVFRN
      ORDER BY t4.CODCNOOCD,
               t2.NUMANOMES
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

print("FTOOMR MENSAL")
print(df.query('CODDIVFRN==97310').groupby('CODCNOOCD')[['VLRVNDFATLIQ']].sum(), '\n')
print("Arquivo.pkl de carga OCD")
print(dfOCD.query('CODFRN==97310 and NOMMES=="Jan"')[['VLRVNDFATLIQ']].sum(), '\n')
print("Arquivo.pkl de carga POP")
print(dfPOP.query('CODFRN==97310 and NOMMES=="Jan"')[['VLRVNDFATLIQ']].sum(), '\n')


#df.NUMANOMES = df.NUMANOMES.astype(str)
#df.CODFIL = df.CODFIL.astype(str)
#df.loc['TOTAL',:] = df[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum(axis=0)
#df = df.fillna('')
#df.loc['TOTAL','DESFIL'] = "TOTAL"
#
#print('Confere FTOOCDMTZRCTCMP')
#print(df.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'))
#print(df.to_string(float_format='{:,.2f}'.format, index=False))
#print(df.to_string(float_format='%.2f', decimal=','))
