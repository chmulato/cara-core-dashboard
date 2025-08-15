const state = {
  ws: null,
  reconnectAttempts: 0,
  maxReconnect: 10,
  reconnectDelay: 2000,
};

function $(id){ return document.getElementById(id); }

function updateSnapshot(snap){
  if(!snap) return;
  $("totalVendas").textContent = snap.total_vendas ?? '--';
  $("ultimaAtualizacao").textContent = snap.ultimo_timestamp ?? '--';
  $("linhasCsv").textContent = snap.linhas ?? '--';
  $("atualizadoEm").textContent = snap.atualizado_em ?? '--';
  renderTable("tabelaVendas", snap.vendas_por_produto, 'Vendas');
  renderTable("tabelaEstoque", snap.estoque_por_produto, 'Estoque');
}

function renderTable(tableId, dataObj, label){
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = '';
  if(!dataObj || Object.keys(dataObj).length === 0){
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 2;
    td.textContent = 'Sem dados';
    td.style.textAlign = 'center';
    tr.appendChild(td); tbody.appendChild(tr); return;
  }
  const entries = Object.entries(dataObj).sort((a,b)=> a[0].localeCompare(b[0]));
  for(const [produto, valor] of entries){
    const tr = document.createElement('tr');
    const tdP = document.createElement('td'); tdP.textContent = produto;
    const tdV = document.createElement('td'); tdV.textContent = valor;
    tr.appendChild(tdP); tr.appendChild(tdV); tbody.appendChild(tr);
  }
}

async function fetchSnapshot(){
  try{
    const r = await fetch('/api/data');
    if(!r.ok) throw new Error('HTTP '+r.status);
    const data = await r.json();
    updateSnapshot(data);
    setStatus('Polling', 'ok');
  }catch(e){
    setStatus('Falha polling', 'err');
  }
}

function setStatus(text, cls){
  const el = $("status");
  el.textContent = text;
  el.className = `status ${cls||''}`;
}

function initWS(){
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const url = `${protocol}://${location.host}/ws`;
  const ws = new WebSocket(url);
  state.ws = ws;
  ws.onopen = () => { setStatus('Tempo real', 'ok'); state.reconnectAttempts = 0; ws.send('ping'); };
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      if(msg.type === 'snapshot') updateSnapshot(msg.data);
    }catch{}
    // Mantém viva
    if(ws.readyState === WebSocket.OPEN){
      setTimeout(()=> { try{ ws.send('ping'); }catch{} }, 15000);
    }
  };
  ws.onerror = () => { ws.close(); };
  ws.onclose = () => {
    setStatus('Reconectando...', 'err');
    if(state.reconnectAttempts < state.maxReconnect){
      state.reconnectAttempts++;
      setTimeout(initWS, state.reconnectDelay * state.reconnectAttempts);
    } else {
      setStatus('Sem WebSocket (fallback)', 'err');
    }
  };
}

document.addEventListener('DOMContentLoaded', () => {
  initWS();
  // Fallback: polling a cada 10s
  setInterval(()=>{ if(!state.ws || state.ws.readyState !== WebSocket.OPEN) fetchSnapshot(); }, 10000);
  fetchSnapshot();
});
