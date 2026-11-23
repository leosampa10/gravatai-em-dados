# Aba Prefeitura › Contratos (DATA.ctr)

Origem: resposta ao pedido LAI 7978/2026 (planilha do sistema de contratos, 9.798 linhas, 2017–2026). `prep_planilha_lai.py` limpa a planilha (corrige acentos, descarta linhas com colunas trocadas) e gera os contratos agrupados.

Formato de DATA.ctr:
- forn: [[nome, CNPJ], ...]
- c: um contrato por linha, colunas em `cols` = [n (número), u (índice em U: Prefeitura, ISSEG, IPG, Câmara, FMMA...), f (índice em forn), o (objeto, até 100 caracteres), ano (assinatura), v (valor original, null se assinado antes de 2017), ad (soma dos aditivos), adp (parte de prorrogações), t (nº de termos depois), s (índice em S: Encerrado, Vigente, Rescindido, Indeterminado), fim ("AAAA-MM" do vencimento)]
- m: [[ano, índice do fornecedor, valor movimentado no ano]] — valor do contrato no ano da assinatura + valor de cada aditivo no ano dele. É a base do ranking por mandato e do "valor contratado por ano".
- meta: {linhas, desc, ger (data da base), prot, ate (última assinatura incluída, dd/mm/aaaa)}

Atualização diária (contratos novos): Portal da Transparência › "Contratos Gerais – Suprimentos" (https://gravatai.atende.net/transparencia), filtro do ano corrente; para cada contrato ou aditivo assinado depois de meta.ate: novo fornecedor em forn (se não existir), nova linha em c (ou soma em ad/adp/t e atualiza s/fim do contrato existente, mesmo número e CNPJ), soma em m [ano, f, valor]. Atualize meta.ate e meta.ger. Valores sempre conferidos no documento do contrato.
