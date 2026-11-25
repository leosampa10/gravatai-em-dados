# Emendas, obras federais e trajetória nas urnas

Três blocos do site vêm de fontes federais. A nuvem não alcança esses domínios: rode os trechos abaixo no **navegador do app** (javascript_tool), como já é feito com o Siconfi.

## 1. Obras com dinheiro federal (`DATA.obf`) — toda segunda-feira

Fonte oficial: API aberta do Obrasgov (sem chave). Domínio liberado no navegador do app: `api.obrasgov.gestao.gov.br`.

1. Abra uma aba em `https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento?idUnico=71337.43-06`.
2. Para cada `idUnico` em `DATA.obf.it[].id`, rode (uma por vez; listas grandes da API demoram):

```js
const r=await (await fetch('/obrasgov/api/projeto-investimento?idUnico=ID')).json();const o=r.content[0];
[o.nome,o.situacao,o.dataInicialPrevista,o.dataFinalPrevista,o.dataFinalEfetiva,(o.fontesDeRecurso||[]).map(f=>f.valorInvestimentoPrevisto)]
```

3. Atualize em cada item: `s` (`exec` = "Em execução", `par` = "Paralisada", `ina` = "Inacabada", `conc` = "Concluída"), `a`/`b` (dd/mm/aaaa) e `v` (R$ milhões; `null` se o valor vier 0,01 ou vazio). Obra concluída sai da lista e vira nota no resumo.
4. Obras novas: abra `https://www.politicometro.org/br?uf=rs&cidade=4309209&assunto=obras`, leia a lista (`get_page_text`) e, se aparecer obra que não está em `DATA.obf`, pegue o número no "Ver o registro oficial" e confira na API antes de incluir.
5. Grave `DATA.obf.src` com a data da consulta.

## 2. Emendas federais pagas à Prefeitura (`DATA.emd`) — toda segunda-feira

Fonte oficial: CGU, Portal da Transparência (emendas parlamentares, pagamentos por favorecido). A API da CGU exige chave pessoal (gov.br); até o Sergio cadastrar uma, use o levantamento do Politicômetro, que lê a mesma base:

1. Abra `https://www.politicometro.org/br?uf=rs&cidade=4309209&assunto=dinheiro`, clique em "Ver todos" na lista "Quem mandou" e leia o texto.
2. Atualize `per` (período), `tot` (R$ mil), `pc` (R$ por morador), `pm` (Gravataí, média do RS, média do Brasil), `q` ([nome, partido-UF ou casa, tipo, R$ mil]) e `out` ([nº de autores, R$ mil]).
3. Em `src`, diga a data do levantamento e que a base é a CGU.
4. Valores da época, sem correção: o bloco compara médias do mesmo período, como explica a nota do card.

## 3. Trajetória nas urnas (`DATA.traj`) — só depois de eleição ou troca de vereador

Fonte: TSE (candidaturas e votação por candidato). Muda só quando há eleição nova ou suplente que assume. Para um vereador novo, abra `https://www.politicometro.org/p/<slug>` e rode o extrator usado na versão 7 (lista `[ano, votos, resultado, cargo, lugar fora de Gravataí, partido]`, ordem crescente). Confira o homônimo: só vale candidatura em Gravataí ou no RS.

Base/oposição de cada mandato vem de `DATA.met[id][L1|L2].opo` (classificação do próprio painel).
