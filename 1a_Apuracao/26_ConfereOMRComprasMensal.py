#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    NUMANOMESOCD = f.read()
#NUMANOMESOCD = 202112

#Consulta
mysql = (f"""     
SELECT t4.CODCNOOCD, 
          t2.NUMANOMES, 
          t5.CODFIL, 
          t5.DESFIL,
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
      GROUP BY t4.CODCNOOCD,
               t2.NUMANOMES,
               t5.CODFIL,
               t5.DESFIL
      ORDER BY t4.CODCNOOCD,
               t2.NUMANOMES
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

df.NUMANOMES = df.NUMANOMES.astype(str)
df.CODFIL = df.CODFIL.astype(str)
df.loc['TOTAL',:] = df[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum(axis=0)
df = df.fillna('')
df.loc['TOTAL','DESFIL'] = "TOTAL"

print('Confere FTOOCDMTZRCTCMP')
print(df.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'),'\n')
#print(df.to_string(float_format='%.2f', decimal=','))

print('!!! Em caso de divergencia executar os processos "31 a 36" para ajustar!!!')