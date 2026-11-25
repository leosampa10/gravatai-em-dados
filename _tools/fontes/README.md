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

Fonte oficial: CGU, API do Portal da Transparência. Exige a chave pessoal do Sergio (cabeçalho `chave-api-dados`), que está só no prompt da tarefa diária. **Nunca grave a chave no repositório nem no site.** Domínio liberado no navegador do app: `api.portaldatransparencia.gov.br`.

1. Abra uma aba em `https://api.portaldatransparencia.gov.br/swagger-ui/index.html`.
2. Rode `window.K='<chave>'` e cole o conteúdo de `_tools/fontes/emendas_cgu.js`.
3. Chame `await emd.passo()` até retornar `"pronto"` (cada chamada dura até ~35 s) e depois `emd.resumo()`.
   O script lê os pagamentos de 2023 em diante aos CNPJs 87.890.992/0001-58 (Município de Gravataí) e 12.195.662/0001-43 (Fundo Municipal de Saúde), abre o detalhe de cada transferência e soma por autor de emenda. Tipo: ação 0EC2 = "Pix" (transferência especial); autor com código 7xxx = bancada; 5xxx/6xxx = comissão; demais = individual.
4. Atualize `DATA.emd`: `per`, `tot` (R$ mil), `pc` (tot ÷ população IBGE do ano), `q` ([nome, partido-UF ou casa, tipo, R$ mil]); para autor novo, confira o partido atual na Câmara/Senado. Mantenha `pm` (médias do RS e do Brasil, do Politicômetro) e atualize-as quando o Politicômetro publicar números novos.
5. Grave a data da consulta em `src`.

## 3. Trajetória nas urnas (`DATA.traj`) — só depois de eleição ou troca de vereador

Fonte: TSE (candidaturas e votação por candidato). Muda só quando há eleição nova ou suplente que assume. Para um vereador novo, abra `https://www.politicometro.org/p/<slug>` e rode o extrator usado na versão 7 (lista `[ano, votos, resultado, cargo, lugar fora de Gravataí, partido]`, ordem crescente). Confira o homônimo: só vale candidatura em Gravataí ou no RS.

Base/oposição de cada mandato vem de `DATA.met[id][L1|L2].opo` (classificação do próprio painel).
