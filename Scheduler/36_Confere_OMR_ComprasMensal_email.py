#elton.mata@martins.com.br

#Importa as bibliotecas e conecta no Oracle dwh01
import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleDWH import conn
pd.options.display.float_format = '{:,.2f}'.format

with open('../Parametros/NUMANOMESOCD.txt','r') as f:
    NUMANOMESOCD = f.read()

#Consulta
mysql = (f"""     
SELECT t4.CODCNOOCD AS CODCNO, 
          t2.NUMANOMES AS ANOMES, 
          t5.CODFIL, 
          TRIM(SUBSTR(t5.DESFIL,9,17)) AS DESFIL,
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
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()
df = df.sort_values(by='VLRVNDFATLIQ', ascending=False)

df.ANOMES = df.ANOMES.astype(str)
df.CODFIL = df.CODFIL.astype(str)
df.loc['TOTAL',:] = df[['VLRVNDFATLIQ','VLRRCTLIQAPU','VLRMRGBRT','VLRMRGCRB']].sum(axis=0)
df = df.fillna('')
df.loc['TOTAL','DESFIL'] = "TOTAL"

print('Confere FTOOCDMTZRCTCMP')
print(df.to_markdown(index=False, tablefmt='github', floatfmt=',.2f', numalign='right'))
#print(df.to_string(float_format='{:,.2f}'.format, index=False))
#print(df.to_string(float_format='%.2f', decimal=','))

import sys
sys.path.insert(0, r'C:\oracle\dwh')
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from pretty_html_table import build_table
from envia_mail import server
from email import encoders

address_book = ['elton.mata@martins.com.br']
sender = 'elton.mata@martins.com.br'
subject = "Carga Meta POP Fato OMR"
tabela = build_table(df, 'blue_light', text_align='right')

body = f"""<html><body>
<p>Meta POP Fato OMR: {NUMANOMESOCD}</p>
{tabela}
<p>FTOOCDMTZRCTCMP</p>
</body></html>
"""
#anexar arquivo
#file = "InflacaoInterna_Mensal.csv"
#attachment = open(file,'rb')
#obj = MIMEBase('application','octet-stream')
#obj.set_payload((attachment).read())
#encoders.encode_base64(obj)
#obj.add_header('Content-Disposition',"attachment; filename= "+file)

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = ','.join(address_book)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))
#msg.attach(obj)
text=msg.as_string()
server.sendmail(sender,address_book, text)
server.quit()