'''
Envia email Operação executar JOB Carga -- OMR Compras Mensal (Planejamento Operacional)
Fato: dwh.FTOOCDMTZRCTCMP (CODCNOOCD = 'POP')
Cubo: Orcamento Matricial > Orçamento Matricial de Receita - OMR > OMR Compras > OMR Compras Mensal

Carga da Fato: 30 minutos
Tempo total (Fato e Cubo):
29/09/2020 02:29 (ter 18:30-20:59)
30/04/2021 01:27 (sex 14:50-16:17)
31/12/2021 01:31 (sex 12:51-14:22)

Assunto: 
Execução eventual -- WADWH31B

Texto:
Favor executar novamente o eventual do grupo WADWH31B que está na aplicação E_WA
Parâmetro a ser informado ANO = 2022

Grato,
'''
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from envia_mail import server

address_book = ['operacao@martins.com.br']
address_bookCC = ['marcio.oliveira@martins.com.br']
sender = 'elton.mata@martins.com.br'
subject = "Execução eventual -- WADWH31B"

body = f"""<html><body>
Favor executar novamente o eventual do grupo WADWH31B que está na aplicação E_WA<br />
Parâmetro a ser informado <b>ANO = 2022</b>

<p>
    Att, Elton<br />
    Planejamento, Controle e Gestão<br />
    Ramal 1246
</p>

</body></html>
"""
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = ','.join(address_book)
msg['Cc'] = ','.join(address_bookCC)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))
text=msg.as_string()
server.sendmail(sender, address_book, text)
server.quit()