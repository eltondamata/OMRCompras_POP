#elton.mata@martins.com.br

from datetime import date
from dateutil.relativedelta import relativedelta

ANOREF = int((date.today() + relativedelta(months=+1)).strftime("%Y"))
MESREF = int((date.today() + relativedelta(months=+1)).strftime("%Y%m"))

caminho = 'X:/PLANEJAMENTO/' + str(ANOREF) + '/PLAN_OPERACIONAL/' + str(MESREF) + '/OMRCompras_POP/'

with open('../Parametros/caminho.txt', "w") as output:
    output.write(str(caminho))
    
with open('../Parametros/NUMANOMESOCD.txt', "w") as output:
    output.write(str(MESREF))
    
print('NUMANOMESOCD =', MESREF)
