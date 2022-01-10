#definir o ANOMES no arquivo = NUMANOMESOCD.txt
import pandas as pd
from dateutil.relativedelta import relativedelta

MESREF = int((pd.to_datetime("today") + relativedelta(months=+1)).strftime("%Y%m")) #Definição POP mes seguinte

with open('../NUMANOMESOCD.txt', "w") as output:
    output.write(str(MESREF))
    
print('NUMANOMESOCD =', MESREF)


