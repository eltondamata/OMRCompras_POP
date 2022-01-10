'''
Envia email para Operação atualiza OMR COMPRAS DIARIO
Roda automaticamente todo dia 1º do mes, mas é necessário solicitar a atualização antes da virada do mês pois o processo que atualiza a meta do infodia roda as 18:00 do último dia útil do mês.

Informação: Período de referência da base histórica para abrir a meta por filial = Ano do parâmetro informado no email -1 (ano anterior completo)
Se for alterar esse periodo para pegar base mais recente, não deixar que o ano seja igual ao do parametro, pois isso dá erro na virada de ano que o parametro informado é do ano do orçamento e nesse caso não terá valor realizado. Caso tenha essa necessidade ajustar esse parametro para pegar uma referencia dos últimos meses independente do parametro informado.

Tempo Carga Fato: 50 minutos
Tempo total (atualiza Fato e cubo)
28/05/2020 - 01:46 (qui 08:58-10:44)
30/09/2020 - 03:03 (09:21-12:24)
30/03/2021 - 02:09 (Ter 18:54-21:03)
31/12/2021 - 01:16 (Sex 10:16-11:32)

Assunto:
Execução eventual - WADWH37A

Texto:
Solicito a execução eventual do grupo WADWH37A que está na aplicação E_WA
'''
import sys
sys.path.insert(0, r'C:\oracle\dwh')
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from envia_mail import server

address_book = ['operacao@martins.com.br']
address_bookCC = ['marcio.oliveira@martins.com.br']
sender = 'elton.mata@martins.com.br'
subject = "Execução eventual - WADWH37A"

body = f"""<html><body>
Solicito a execução eventual do grupo WADWH37A que está na aplicação E_WA

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