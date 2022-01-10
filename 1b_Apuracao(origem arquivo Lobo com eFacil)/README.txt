Versão criada como alternativa mais rápida para gerar o arquivo para o Josimar ajustar a Margem (sem necessidade de aguardar o arquivo da Larissa com a abertura por UF)
Usa o realizado das ultimas 8 semanas para distribuir a meta recebida do Lobo (Fornecedor x Filial) para abrir por UF (Fonte do realizado = Fato OMR Diaria ; Operação=VND)

1) Atualiza o aruqivo excel (Plan_Operacional.xlsx) com UF calculada pela regra acima
2) Quando o Josimar retornar o arquivo com a margem ajustada, basta ajustar também o faturamento por UF recebido da Larissa e executar as próximas etapdas do processo de carga.


Alterações versus o processo principal (Pythia):
0_0 Atualizar Mes POP.py (exatamente igual)
1_0 Backup RLC.py (exatamente igual)
1_1a FaturamentoComprasPOP_pkl.py (não existe no processo principal, usado para gerar a base historica das ultimas semanas na combinação FORNECEDOR x FILIAL x UF) e calcular UF com base nos dados recebidos do arquivo do Lobo)
1_1b OMR_Compras_OCD.py (exatamente igual -- usado para gerar o orçado original + realizado para complementar a base)
1_2 OMR_FRNUF_POP.py (semelhante ao processo principal, alterado a fonte do faturamento (FORNECEDOR X FILIAL X UF) -- Processo principal usa o arquivo xlsx recebido da Larissa, e esse aqui usa o "FaturamentoComprasPOP.pkl" gerado no processo anterior)
1_3 OMR_COMPRAS_POP.py (exatamente igual)
1_4a Atualiza Excel.py (exatamente igual -- atualiza o arquivo "Plan_Operacional.xlsx)
1_4b OMR_CategoriaFornecedorEstadoCanal_xlsx.py (Atualiza arquivo com detalhe Categoria x Fornec x Canal x Estado) -- em conversa com Josimar em 23dez2021 esse nível de detalhe não é necessário no Planejamento Operacional.

após receber arquivo detalhado da Larissa (Fornecedor x Filial x UF) executar os processos a partir do "1_2 OMR_FRNUF_POP.py" para respeitar a combinação Forn x UF.
