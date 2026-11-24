// Roda dentro do site (Playwright). Devolve a lista de cartões de prévia: um por gráfico, mais as votações recentes.
(() => {
  const T = e => (e ? (e.innerText ?? e.textContent ?? '').replace(/\s+/g, ' ').trim() : '');
  const nf = (n, d = 0) => n.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const mi = n => 'R$ ' + nf(n, n >= 100 ? 1 : 1).replace(/,0$/, '') + ' mi';
  const MES = ['fevereiro', 'abril', 'junho', 'agosto', 'outubro', 'dezembro'];
  const out = [];
  const crumbOf = el => {
    const pg = el.closest('.page'); const sb = el.closest('.sub');
    const g = pg ? pg.id.replace('g-', '') : '';
    const gn = { inicio: 'Início', camara: 'Câmara', prefeitura: 'Prefeitura', noticias: 'Notícias', fontes: 'Fontes', plano: 'Prefeitura' }[g] || '';
    let sn = '';
    if (sb) { const b = document.querySelector(`[data-s="${sb.id}"]`); sn = b ? T(b) : ''; }
    return [gn, sn].filter(Boolean).join(' · ');
  };
  const fonteOf = el => { const f = [...el.querySelectorAll('.src, p, small')].map(T).find(t => /^Fonte/i.test(t)); return f ? f.slice(0, 150) : ''; };
  const leadOf = el => { const p = el.querySelector('.lead, .sec-l, p'); return p ? T(p).replace(/(\w)\?(\s)/g, '$1$2').slice(0, 220) : ''; };
  const titleOf = el => T(el.querySelector('h2, h3'));

  // destaques calculados
  const D = {};
  try { // calendário do gasto
    const C = DATA.cal; const yr = Object.keys(C.v['Total']).sort().pop(); const bim = +(C.asof.match(/(\d)º/) || [0, 0])[1];
    const pct = k => { const v = C.v[k][yr]; if (!v) return null; const e = (v[1] || [])[bim - 1] || 0; return { dot: v[0], emp: e, p: v[0] ? e / v[0] : 0 }; };
    const areas = C.K.filter(k => k !== 'Total').map(k => [k, pct(k)]).filter(([k, x]) => x && x.dot >= 5);
    const low = areas.sort((a, b) => a[1].p - b[1].p)[0]; const tot = pct('Total');
    const big = low[1].emp ? Math.round(low[1].p * 100) + '%' : 'R$ 0';
    const txt = low[1].emp ? `do previsto para <i>${low[0]}</i> em ${yr} foi empenhado até ${MES[bim - 1]} (${mi(low[1].emp)} de ${mi(low[1].dot)}).` : `empenhado em <i>${low[0]}</i> até ${MES[bim - 1]}, de ${mi(low[1].dot)} previstos para ${yr}.`;
    const bars = ['Saúde', 'Educação'].map(k => [k, pct(k)]).filter(x => x[1]).map(([k, x]) => ({ l: k, v: Math.round(x.p * 100) + '%', w: x.p, hl: 0 }));
    bars.push({ l: 'Prefeitura toda', v: Math.round(tot.p * 100) + '%', w: tot.p, hl: 2 });
    bars.push({ l: low[0], v: Math.round(low[1].p * 100) + '%', w: low[1].p, hl: 1 });
    D['c-cal'] = { t: 'dest', tag: `Prefeitura · Orçamento ${yr}`, big, txt, bt: 'Quanto do previsto já foi empenhado', bars, fonte: `Fonte: Siconfi, RREO do ${C.asof}`, desc: `${big} ${txt.replace(/<[^>]+>/g, '')}` };
  } catch (e) { }
  try { // pisos
    const M = DATA.piso.mde, S = DATA.piso.asps; const y = Object.keys(M).sort().pop();
    const ys = Object.keys(M).sort().slice(-6);
    const sv = S && S[y] ? S[y][2] : null;
    D['c-piso'] = { t: 'dest', tag: 'Prefeitura · Educação e saúde', big: nf(M[y][2], 2) + '%', txt: `da receita de impostos foi aplicada em <i>educação</i> em ${y}. O mínimo da Constituição é 25%.` + (sv ? ` Saúde: ${nf(sv, 2)}% (mínimo: 15%).` : ''),
      bt: 'Educação, % da receita de impostos', bars: ys.map(k => ({ l: k, v: nf(M[k][2], 2) + '%', w: M[k][2] / 30, hl: M[k][2] < 25 ? 1 : 0 })), fonte: 'Fonte: TCE-RS, dados abertos', desc: `${nf(M[y][2], 2)}% da receita de impostos em educação em ${y} (mínimo 25%).` };
  } catch (e) { }
  try { // salários
    const S = DATA.sal.s; const y = Math.max(...DATA.sal.yrs); const p = S['Prefeito'], a = 2021;
    const g = p[y] / p[a] - 1, inf = ipcaAc(a, y);
    D['s-quanto-ganham'] = { t: 'dest', tag: `Salários · ${y}`, big: 'R$ ' + nf(p[y]), txt: `é o salário do <i>prefeito</i> em ${y}. Desde ${a}, subiu ${nf(g * 100)}%; a inflação do período foi de ${nf(inf * 100)}%.`,
      bt: `Salário mensal em ${y}`, bars: ['Prefeito', 'Vice-prefeito', 'Vereador'].filter(k => S[k]).map((k, i) => ({ l: k, v: 'R$ ' + nf(S[k][y]), w: S[k][y] / p[y], hl: i ? 0 : 2 })), fonte: 'Fonte: leis de subsídio de Gravataí; IPCA (IBGE)', desc: `Prefeito: R$ ${nf(p[y])} por mês em ${y}; +${nf(g * 100)}% desde ${a}, contra ${nf(inf * 100)}% de inflação.` };
  } catch (e) { }
  try { // contratos
    goto('prefeitura:p-ctr');
    const rows = [...document.querySelectorAll('#ctr-top-rows .r')].slice(0, 4).map(r => ({ n: T(r.querySelector('button')).split(' ').slice(0, 0).join(''), name: (r.querySelector('button').childNodes[0].textContent || '').trim(), v: T(r.querySelector('.v')), w: parseFloat((r.querySelector('.t i') || {}).style?.width || '0') / 100 }));
    const lead = T(document.getElementById('ctr-top-lead'));
    const short = s => s.replace(/ LTDA.*$| S\/?A$| - ME$/i, '').replace(/IRMANDADE DA SANTA CASA DE MISERICORDIA DE PORTO ALEGRE/i, 'SANTA CASA DE PORTO ALEGRE');
    const per = (lead.match(/De (\d{4}) a (\d{4})/) || []).slice(1).join('–');
    D['ctr-top'] = { t: 'dest', tag: 'Prefeitura · Contratos', big: rows[0].v, txt: `em contratos e aditivos com <i>${short(rows[0].name).toLowerCase().replace(/(^|\s)\S/g, c => c.toUpperCase()).replace(/ (De|Da|Do|Dos|Das|E) /g, m => m.toLowerCase())}</i> (${per}), o maior valor entre os fornecedores da Prefeitura.`,
      bt: 'Maiores fornecedores', bars: rows.map((r, i) => ({ l: short(r.name).slice(0, 30), v: r.v, w: r.w, hl: i ? 0 : 2 })), fonte: 'Fonte: Portal da Transparência de Gravataí', desc: lead };
    goto('inicio');
  } catch (e) { }
  try { // mapa
    const V = DATA.vmap; const el = V.k.map((n, i) => i).filter(i => V.c[V.k[i]][3] === 's'); const cnt = {};
    Object.values(V.bz).forEach(o => { const sum = V.k.map((_, i) => o.k.reduce((a, kk) => a + (V.L[kk] ? V.L[kk][2][i] : 0), 0)); const lead = el.slice().sort((a, b) => sum[b] - sum[a])[0]; cnt[lead] = (cnt[lead] || 0) + 1; });
    const ord = Object.entries(cnt).sort((a, b) => b[1] - a[1]); const c0 = V.c[V.k[ord[0][0]]];
    D['s-onde-cada-vereador-teve-votos'] = { t: 'dest', tag: 'Eleição de 2024 · Mapa de votos', big: ord[0][1] + ' bairros', txt: `em que <i>${c0[0]}</i> (${c0[1]}) foi o eleito mais votado. Veja no mapa onde cada vereador teve votos.`,
      bt: 'Mais votado em quantos bairros', bars: ord.slice(0, 4).map(([i, n], j) => ({ l: V.c[V.k[i]][0], v: String(n), w: n / ord[0][1], hl: j ? 0 : 2 })), fonte: 'Fonte: boletins de urna (TSE)', desc: `${c0[0]} foi o eleito mais votado em ${ord[0][1]} bairros na eleição de 2024.` };
  } catch (e) { }
  const kpiOf = el => { const ks = []; el.querySelectorAll('*').forEach(e => { if (e.children.length || ks.length >= 4) return; const t = T(e); if (!t || t.length > 12 || !/\d/.test(t)) return; if (parseFloat(getComputedStyle(e).fontSize) < 26) return; let lab = e.nextElementSibling ? T(e.nextElementSibling) : ''; if (!lab && e.parentElement.nextElementSibling) lab = T(e.parentElement.nextElementSibling); ks.push({ b: t, l: lab.slice(0, 70) }); }); return ks; };

  // todos os cards
  document.querySelectorAll('.page .card[id], #g-inicio .sec[id]').forEach(el => {
    const id = el.id; if (/^c-card|^opina$|^ficha$|^sal-box$|^pat-m$/.test(id) || el.parentElement.closest('.card')) return;
    const pg = el.closest('.page'); const sb = el.closest('.sub'); const g = pg ? pg.id.replace('g-', '') : '';
    goto(sb ? g + ':' + sb.id : g);
    const base = { id, title: titleOf(el) || id, crumb: crumbOf(el), lead: leadOf(el) };
    let x = D[id];
    if (!x) { const ks = kpiOf(el); if (ks.length >= 3) x = { t: 'kpi', kpis: ks, fonte: fonteOf(el), desc: ks.map(k => k.b + ' ' + k.l).join(' · ') }; }
    out.push(Object.assign(base, x || { t: 'gen', fonte: '' }, { feat: !!D[id] }));
  });
  goto('inicio');
  // votações recentes
  const it = (DATA.vts && DATA.vts.it || []).map((x, i) => [x, i]).sort((a, b) => b[0][0].localeCompare(a[0][0])).slice(0, 30);
  it.forEach(([x]) => {
    const o = vtsObj(x); const key = x[6].split('-').pop() + '-' + x[0].replace(/-/g, '');
    const d = x[0].split('-').reverse().join('/');
    out.push({ id: 'vt-' + key, key, t: 'vot', feat: true, date: x[0], title: o.em || o.sg, crumb: 'Câmara · Votação nominal', sg: o.sg, d, res: o.res, S: o.fav.length, N: o.con.length, B: o.abs.length, A: o.nv.length, aut: o.au || '',
      desc: `${o.sg} · ${o.res} por ${o.fav.length} a ${o.con.length} em ${d}.`, fonte: 'Fonte: votação nominal no site da Câmara' });
  });
  return out;
})()
