#Python 3.8.2
#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
from tabulate import tabulate
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn

#mes seguinte
import datetime
from dateutil.relativedelta import relativedelta
today = datetime.date.today()
today = today.replace(day=1)
today = today + relativedelta(months=+1)
#MESSEG = (today.year*100 + today.month)

with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    PNUMANOMES = f.read()
#PNUMANOMES = (today.year*100 + today.month)
#PNUMANOMES = 202201

#Parametro (default = mes seguinte)
#print("!!! Altere o NUMANOMES ou pressione ENTER pra continuar !!!")
#PNUMANOMES = input(f"NUMANOMES: [{MESSEG}] \n")
#if len(PNUMANOMES) == 0:
#    PNUMANOMES = MESSEG

print(f"executando {PNUMANOMES}...")

#Consulta
mysql = (f"""
SELECT  TO_DATE( TO_CHAR(SUBSTR(D7.NUMANOMESDIA,1,4)) || '-' ||
                 TO_CHAR(SUBSTR(D7.NUMANOMESDIA,5,7-5))  || '-' ||
                 TO_CHAR(SUBSTR(D7.NUMANOMESDIA,7)) ,'YYYY-MM-DD') AS DATREF
       ,DIMFIL.CODFIL AS CODFILEMPEPD
       ,SUM(F.VLRVNDFATLIQ) AS VLRTOTVNDPPS
       ,SUM(F.VLRMRGBRT) AS VLRMRGBRT
       ,SUM(F.VLRMRGCRB) AS VLRPPSMRGCRBVND
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
     AND D7.NUMANOMES = {PNUMANOMES}
GROUP BY D7.NUMANOMESDIA
 ,DIMFIL.CODFIL
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()

#Exportar dados para arquivo.csv
pvt = df.pivot_table(index=['DATREF'], columns=['CODFILEMPEPD'], values=['VLRTOTVNDPPS'])
pvt.columns = pvt.columns.get_level_values(1).rename('')
pvt.loc[:,'TOTAL'] = pvt.sum(axis=1)
last_date = pvt.iloc[[-1]].index
pvt = pvt.append(pd.DataFrame(index=last_date))
pvt.iloc[-1,:] = pvt.sum(axis=0)
pvt = pvt.reset_index()

weekdaydic = {1: 'dom', 2:'seg', 3:'ter', 4:'qua', 5:'qui', 6:'sex', 7:'sab'}
pvt['WeekDay'] = (pvt['DATREF'].dt.strftime('%w').astype(int)+1).map(weekdaydic)
pvt.iloc[-1:,-1] = 'TOTAL'
#pvt.to_csv(r'..\ConfereBaseCarga_SNC.csv', sep=";", encoding="iso-8859-1", decimal=",", float_format='%.2f', date_format='%d/%m/%Y', index=False)
print("Faturamento")
print(tabulate(pvt, headers='keys', tablefmt='psql', floatfmt=',.2f', showindex=False, numalign='right'),'\n')

#Confere Margem Bruta
pvtmb = df.pivot_table(index=['DATREF'], columns=['CODFILEMPEPD'], values=['VLRMRGBRT'])
pvtmb.columns = pvtmb.columns.get_level_values(1).rename('')
pvtmb.loc[:,'TOTAL'] = pvtmb.sum(axis=1)
last_date = pvtmb.iloc[[-1]].index
pvtmb = pvtmb.append(pd.DataFrame(index=last_date))
pvtmb.iloc[-1,:] = pvtmb.sum(axis=0)
pvtmb = pvtmb.reset_index()
pvtmb['WeekDay'] = (pvtmb['DATREF'].dt.strftime('%w').astype(int)+1).map(weekdaydic)
pvtmb.iloc[-1:,-1] = 'TOTAL'
print("Margem Bruta")
print(tabulate(pvtmb, headers='keys', tablefmt='psql', floatfmt=',.2f', showindex=False, numalign='right'),'\n')

#Confere Margem Contribuicao
pvtmb = df.pivot_table(index=['DATREF'], columns=['CODFILEMPEPD'], values=['VLRPPSMRGCRBVND'])
pvtmb.columns = pvtmb.columns.get_level_values(1).rename('')
pvtmb.loc[:,'TOTAL'] = pvtmb.sum(axis=1)
last_date = pvtmb.iloc[[-1]].index
pvtmb = pvtmb.append(pd.DataFrame(index=last_date))
pvtmb.iloc[-1,:] = pvtmb.sum(axis=0)
pvtmb = pvtmb.reset_index()
pvtmb['WeekDay'] = (pvtmb['DATREF'].dt.strftime('%w').astype(int)+1).map(weekdaydic)
pvtmb.iloc[-1:,-1] = 'TOTAL'
print("Margem Contribuicao")
print(tabulate(pvtmb, headers='keys', tablefmt='psql', floatfmt=',.2f', showindex=False, numalign='right'))