#elton.mata@martins.com.br
'''
Confere a carga da Meta POP no InfoDia e SNC
Tabela InfoDia é atualizada todo último dia útil do mês às 18:00
Tabela SNC é atualizada todo dia 1º
'''

import pandas as pd
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from OracleMRT import conn
from datetime import date, timedelta
pd.options.display.float_format = '{:,.2f}'.format

MESREF = (date.today().replace(day=1) - timedelta(days=0)).strftime("%Y%m") #Mes Atual
#MESREF = 202203

#Consulta Infodia ['ANOMESREF', 'CODFILEMPEPD', 'VLRTOTFAT' AS 'RLZ', 'VLRPRVFAT' AS 'OMR']
mysql = (f"""     
select * from MRT.T0160623 WHERE ANOMESREF = {MESREF} 
--FETCH FIRST 5 ROWS ONLY
  """)
infodia = pd.read_sql(mysql, con=conn)
print(f'InfoDia: {MESREF}')
print(pd.DataFrame(infodia.agg({'VLRTOTFAT':'sum', 'VLRPRVFAT': 'sum'}) \
                          .rename({'VLRTOTFAT':'FAT_RLZ', 'VLRPRVFAT': 'FAT_POP'})) \
                          .transpose().to_markdown(tablefmt='github', floatfmt=',.2f', index=False), '\n')

#Consulta SNC ['DATREF', 'CODFILEMPEPD', 'CODFRN', 'CODGRPMER', 'CODFMLMER', 'CODCLSMER', 'VLRTOTVNDPPS', 'VLRPPSMRGCRBVND', 'VLRRCTLIQAPUOCD', 'VLRMRGBRTOCD']
#Valor meta entre essas duas tabelas é a mesma, muda apenas as dimensões (MRT.HSTDIRPPSFRNCTG frnctg) (MRT.HSTDIRPPSFRNEST  frnest)
#Tabela base de dados do SNC (mesmo valor da meta também) MRT.T0151039 (Valor Meta Faturamento POP = VLRPPSFATFCHPOD)
mysql = (f"""
select * from MRT.HSTDIRPPSFRNCTG 
WHERE TO_CHAR(DATREF, 'YYYYMM') = {MESREF}
--FETCH FIRST 5 ROWS ONLY
  """)
df = pd.read_sql(mysql, con=conn)
conn.close()
print(f'META SNC: {MESREF}')
print(pd.DataFrame(df.agg({'VLRTOTVNDPPS':'sum', 'VLRRCTLIQAPUOCD': 'sum', 'VLRMRGBRTOCD': 'sum', 'VLRPPSMRGCRBVND': 'sum'}) \
                     .rename({'VLRTOTVNDPPS':'FATURAMENTO', 'VLRRCTLIQAPUOCD': 'REC_LIQUIDA', 'VLRMRGBRTOCD': 'MARGEM BRUTA', 'VLRPPSMRGCRBVND': 'MARGEM CONTRIBUICAO'})) \
                     .transpose().to_markdown(tablefmt='github', floatfmt=',.2f', index=False))

infodiatot = pd.DataFrame(infodia.agg({'VLRTOTFAT':'sum', 'VLRPRVFAT': 'sum'}) \
                          .rename({'VLRTOTFAT':'FAT_RLZ', 'VLRPRVFAT': 'FAT_POP'})) \
                          .transpose()
dftot = pd.DataFrame(df.agg({'VLRTOTVNDPPS':'sum', 'VLRRCTLIQAPUOCD': 'sum', 'VLRMRGBRTOCD': 'sum', 'VLRPPSMRGCRBVND': 'sum'}) \
                     .rename({'VLRTOTVNDPPS':'FATURAMENTO', 'VLRRCTLIQAPUOCD': 'REC_LIQUIDA', 'VLRMRGBRTOCD': 'MARGEM BRUTA', 'VLRPPSMRGCRBVND': 'MARGEM CONTRIBUICAO'})) \
                     .transpose()



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
subject = "Meta SNC e InfoDia"
tabelaA = build_table(infodiatot, 'blue_light', text_align='right')
tabelaB = build_table(dftot, 'blue_light', text_align='right')

body = f"""<html><body>
<p>Meta  Infodia: {MESREF}
{tabelaA}</p>
<p>Meta  SNC: {MESREF}
{tabelaB}</p>
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