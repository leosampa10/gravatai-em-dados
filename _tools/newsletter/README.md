# Newsletter "Gravataí em dados"

- Inscrição: formulário Tally **GeR76O** (https://tally.so/r/GeR76O). Campos: e-mail, nome (opcional), frequência (diário/semanal), temas, vereadores, bairro, "Prefeitura e contas", consentimento.
- Cancelamento: formulário Tally **q5RNa5** (https://tally.so/r/q5RNa5?email=...). Quem aparece aqui sai da lista.
- Lista de envio = respostas de GeR76O (vale a mais recente de cada e-mail) menos os e-mails de q5RNa5 posteriores à inscrição.
- `montar.py inscritos.json --desde AAAA-MM-DD` gera um HTML por inscrito com novidades (votações, notícias, contas, correções) desde a data. Quem não tem novidade não recebe nada.
- Diário: desde o último envio. Semanal (segunda): últimos 7 dias.
- Envio pelo Gmail do projeto. Nunca salvar e-mails de inscritos no repositório (ele é público).

## Bloco "Em destaque"
O topo de cada e-mail traz cartões em imagem (os mesmos da prévia de link do site, em `d/<id>/card.png`): as votações mais disputadas do período entre as que interessam ao inscrito e um cartão de dado (dois no resumo semanal), escolhido pelos temas dele (educação/saúde → pisos; servidores → salários; habitação/impostos → calendário do gasto; obras → contratos) ou em rodízio diário. Os cartões vêm de `d/destaques.json`, gerado por `python3 _tools/previas/dados.py`; rode-o antes do montar.py.
