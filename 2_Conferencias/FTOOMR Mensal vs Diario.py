#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format


#Consulta FATO MENSAL
mysql = (f"""     
SELECT  DIVFRN.CODDIVFRN,
          t5.CODFIL, 
          SUM(t1.VLRVNDFATLIQ) AS FATMES
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
        AND t2.NUMANOMES = 202203
        AND t4.CODCNOOCD = 'POP'
      GROUP BY DIVFRN.CODDIVFRN,
          t5.CODFIL
  """)
dfmes = pd.read_sql(mysql, con=conn)

#consulta FATO Diaria
mysql = (f"""
SELECT  D8.CODDIVFRN
       ,DIMFIL.CODFIL
       ,SUM(F.VLRVNDFATLIQ) AS FATDIA

From
      DWH.FTOOMRCMPDIA F
     ,DWH.DIMCNOOCD D1
     ,DWH.DIMPOD D7
     ,DWH.DIMPRD D8
     ,DWH.DIMGEO DIMGEO
     ,DWH.DIMFIL DIMFIL
     ,DWH.DIMTIP DIMTIP
Where
         D1.SRKCNOOCD = F.SRKCNOOCD
     AND D1.CODCNOOCD  = 'OCD'
     AND DIMTIP.SRKTIP = F.SRKTIPOPEVND
     AND DIMTIP.CODTIP = 'VND'
     And D7.SRKPOD = F.SRKPODREF
     AND D8.SRKPRD = F.SRKDIVFRN
     AND F.SRKFIL = DIMFIL.SRKFIL
     AND F.SRKGEO = DIMGEO.SRKGEO
     AND D7.NUMANOMES = 202203
GROUP BY D8.CODDIVFRN
       ,DIMFIL.CODFIL
  """)
dfdia = pd.read_sql(mysql, con=conn)

conn.close()

df = pd.merge(dfdia, dfmes, how='outer')
df.fillna(0, inplace=True)
df['DIF'] = df['FATDIA'] - df['FATMES']

print(df.query('DIF<-0.1 or DIF>0.1'))

'''
      CODDIVFRN  CODFIL  FATDIA     FATMES         DIF
2049      97948      99    0.00 146,378.96 -146,378.96
2050      98164      41    0.00 122,811.75 -122,811.75
'''