/* Emendas parlamentares pagas à Prefeitura de Gravataí e ao Fundo Municipal de Saúde (CGU, API do Portal da Transparência).
   Rodar no navegador do app, numa aba aberta em https://api.portaldatransparencia.gov.br/swagger-ui/index.html
   1) defina window.K = '<chave-api-dados>' (a chave fica só no prompt da tarefa diária, nunca no repositório)
   2) cole este arquivo; ele roda em etapas curtas: chame await emd.passo() até retornar "pronto", depois emd.resumo()  */
window.emd={CNPJ:['87890992000158','12195662000143'],ANOS:[2023,2024,2025,2026],docs:{},det:{},
 async passo(){const t0=Date.now();
  for(const c of this.CNPJ)for(const a of this.ANOS){const k=c+'-'+a;if(this.docs[k])continue;const all=[];for(let p=1;p<200;p++){const j=await (await fetch(`/api-de-dados/despesas/documentos-por-favorecido?codigoPessoa=${c}&fase=3&ano=${a}&pagina=${p}`,{headers:{'chave-api-dados':K}})).json();if(!j.length)break;all.push(...j)}this.docs[k]=all;if(Date.now()-t0>30000)return 'continua'}
  const T=Object.values(this.docs).flat().filter(d=>/^4[01]/.test(d.modalidade));
  for(const d of T){if(this.det[d.documento])continue;this.det[d.documento]=await (await fetch('/api-de-dados/despesas/documentos/'+d.documento,{headers:{'chave-api-dados':K}})).json();if(Date.now()-t0>35000)return 'continua'}
  return 'pronto'},
 resumo(){const v=s=>+String(s).replace(/\./g,'').replace(',','.');const by={};let last='';
  Object.values(this.det).filter(d=>d.autor&&/^\d{4} - /.test(d.autor)&&!/^0000/.test(d.autor)).forEach(d=>{const [cod,...n]=d.autor.split(' - ');const k=n.join(' - ');
   const tipo=/0EC2/.test(d.acao)?'Pix':(+cod>=7000?'bancada':(+cod>=5000?'comissão':'individual'));by[k]=by[k]||{v:0,t:new Set()};by[k].v+=v(d.valor);by[k].t.add(tipo);
   const dt=d.data.split('/').reverse().join('-');if(dt>last)last=dt});
  const L=Object.entries(by).map(([k,o])=>[k,[...o.t].join(' + '),Math.round(o.v)]).sort((a,b)=>b[2]-a[2]);
  return JSON.stringify({ate:last,tot:L.reduce((a,x)=>a+x[2],0),autores:L})}};
'ok'
