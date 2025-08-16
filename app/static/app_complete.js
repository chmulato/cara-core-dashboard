console.log('🚀 Dashboard JavaScript carregado!');

const state = {
    ws: null,
    reconnectAttempts: 0,
    maxReconnect: 10,
    reconnectDelay: 2000,
    charts: {}
};

function $(id) { return document.getElementById(id); }

function setStatus(text, cls) {
    const el = $("status");
    if (el) {
        el.textContent = text;
        el.className = `status ${cls || ''}`;
    }
}

function renderTable(tableId, dataObj, label) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;
    
    tbody.innerHTML = '';
    if (!dataObj || Object.keys(dataObj).length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 2;
        td.textContent = 'Sem dados';
        td.style.textAlign = 'center';
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
    }
    
    const entries = Object.entries(dataObj).sort((a, b) => a[0].localeCompare(b[0]));
    for (const [produto, valor] of entries) {
        const tr = document.createElement('tr');
        const tdP = document.createElement('td');
        tdP.textContent = produto;
        const tdV = document.createElement('td');
        tdV.textContent = valor;
        tr.appendChild(tdP);
        tr.appendChild(tdV);
        tbody.appendChild(tr);
    }
}

function ensureChart(id, label, yTitle) {
    console.log(`🎨 Criando/verificando chart: ${id}`);
    
    if (state.charts[id]) {
        console.log(`♻️ Chart ${id} já existe`);
        return state.charts[id];
    }
    
    const canvas = document.getElementById(id);
    if (!canvas) {
        console.error(`❌ Canvas ${id} não encontrado!`);
        return null;
    }
    
    console.log(`✅ Canvas ${id} encontrado, criando chart...`);
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error(`❌ Não foi possível obter contexto 2D para ${id}`);
        return null;
    }
    
    try {
        if (id === 'chartPizza') {
            console.log('🥧 Criando gráfico de pizza...');
            state.charts[id] = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                            '#FF9F40', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    animation: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        } else {
            console.log(`📈 Criando gráfico de linha para ${id}...`);
            state.charts[id] = new Chart(ctx, {
                type: 'line',
                data: { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    animation: false,
                    interaction: { intersect: false, mode: 'index' },
                    plugins: { legend: { position: 'bottom' } },
                    scales: {
                        y: { title: { display: true, text: yTitle } },
                        x: { ticks: { maxRotation: 45, minRotation: 0 } }
                    }
                }
            });
        }
        
        console.log(`🎉 Chart ${id} criado com sucesso!`);
        return state.charts[id];
        
    } catch (error) {
        console.error(`❌ Erro ao criar chart ${id}:`, error);
        return null;
    }
}

function buildPieChart(vendas_por_produto) {
    console.log('🥧 Construindo gráfico de pizza:', vendas_por_produto);
    
    if (!vendas_por_produto || Object.keys(vendas_por_produto).length === 0) {
        console.log('❌ Não há dados para o gráfico de pizza');
        return;
    }
    
    const chartPie = ensureChart('chartPizza', 'Distribuição de Vendas', '');
    if (!chartPie) {
        console.error('❌ Não foi possível criar o gráfico de pizza');
        return;
    }
    
    const entries = Object.entries(vendas_por_produto);
    const labels = entries.map(([produto]) => produto);
    const data = entries.map(([, vendas]) => vendas);
    
    console.log('📊 Dados do gráfico de pizza:', { labels, data });
    
    chartPie.data.labels = labels;
    chartPie.data.datasets[0].data = data;
    chartPie.update();
    
    console.log('✅ Gráfico de pizza atualizado!');
}

function buildCharts(rows) {
    console.log('📈 Construindo gráficos de linha:', rows);
    
    if (!Array.isArray(rows) || rows.length === 0) {
        console.log('❌ Não há dados históricos para gráficos de linha');
        return;
    }
    
    const vendasSeries = {};
    const estoqueSeries = {};
    const labels = [];
    
    rows.forEach(row => {
        const ts = row.timestamp || row.timestamp_str;
        labels.push(ts);
    });
    
    const uniqueLabels = Array.from(new Set(labels));
    const rowByLabel = {};
    rows.forEach(r => {
        const ts = r.timestamp;
        rowByLabel[ts] = rowByLabel[ts] || [];
        rowByLabel[ts].push(r);
    });
    
    const produtos = new Set(rows.map(r => r.produto));
    console.log('📊 Produtos encontrados:', Array.from(produtos));
    console.log('🏷️ Labels únicos:', uniqueLabels.length);
    
    produtos.forEach(p => {
        vendasSeries[p] = uniqueLabels.map(l => {
            const arr = rowByLabel[l] || [];
            const found = arr.filter(x => x.produto === p);
            return found.reduce((s, x) => s + (Number(x.vendas) || 0), 0) || 0;
        });
        
        estoqueSeries[p] = uniqueLabels.map(l => {
            const arr = rowByLabel[l] || [];
            const found = arr.filter(x => x.produto === p);
            if (found.length === 0) return null;
            return found[found.length - 1].estoque ?? null;
        });
    });
    
    const chartV = ensureChart('chartVendas', 'Vendas', 'Vendas');
    const chartE = ensureChart('chartEstoque', 'Estoque', 'Estoque');
    
    if (!chartV || !chartE) {
        console.error('❌ Não foi possível criar gráficos de linha');
        return;
    }
    
    chartV.data.labels = uniqueLabels;
    chartE.data.labels = uniqueLabels;
    chartV.data.datasets = Object.entries(vendasSeries).map(([p, data]) => ({
        label: p,
        data,
        tension: 0.2,
        fill: false
    }));
    chartE.data.datasets = Object.entries(estoqueSeries).map(([p, data]) => ({
        label: p,
        data,
        tension: 0.2,
        fill: false
    }));
    
    chartV.update();
    chartE.update();
    
    console.log('✅ Gráficos de linha atualizados!');
}

async function loadHistorico() {
    try {
        console.log('📊 Carregando dados históricos...');
        const r = await fetch('/api/historico?limit=120');
        if (!r.ok) return;
        const rows = await r.json();
        buildCharts(rows);
    } catch (e) {
        console.error('❌ Erro ao carregar histórico:', e);
    }
}

function updateSnapshot(snap) {
    if (!snap) {
        console.error('❌ Snapshot vazio recebido');
        return;
    }
    
    console.log('📊 Atualizando snapshot:', snap);
    
    $("totalVendas").textContent = snap.total_vendas ?? '--';
    $("ultimaAtualizacao").textContent = snap.ultimo_timestamp ?? '--';
    $("linhasCsv").textContent = snap.linhas ?? '--';
    $("atualizadoEm").textContent = snap.atualizado_em ?? '--';
    
    renderTable("tabelaVendas", snap.vendas_por_produto, 'Vendas');
    renderTable("tabelaEstoque", snap.estoque_por_produto, 'Estoque');
    
    buildPieChart(snap.vendas_por_produto);
    loadHistorico();
}

async function fetchSnapshot() {
    try {
        console.log('🔄 Buscando dados...');
        const r = await fetch('/api/data');
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const data = await r.json();
        updateSnapshot(data);
        setStatus('Polling', 'ok');
    } catch (e) {
        console.error('❌ Erro ao buscar dados:', e);
        setStatus('Falha polling', 'err');
    }
}

function initWS() {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${location.host}/ws`;
    const ws = new WebSocket(url);
    state.ws = ws;
    
    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        setStatus('Tempo real', 'ok');
        state.reconnectAttempts = 0;
        ws.send('ping');
    };
    
    ws.onmessage = (ev) => {
        try {
            const msg = JSON.parse(ev.data);
            if (msg.type === 'snapshot') updateSnapshot(msg.data);
        } catch {}
        
        if (ws.readyState === WebSocket.OPEN) {
            setTimeout(() => {
                try { ws.send('ping'); } catch {}
            }, 15000);
        }
    };
    
    ws.onerror = () => {
        console.log('❌ Erro no WebSocket');
        ws.close();
    };
    
    ws.onclose = () => {
        console.log('🔄 WebSocket desconectado, tentando reconectar...');
        setStatus('Reconectando...', 'err');
        if (state.reconnectAttempts < state.maxReconnect) {
            state.reconnectAttempts++;
            setTimeout(initWS, state.reconnectDelay * state.reconnectAttempts);
        } else {
            setStatus('Sem WebSocket (fallback)', 'err');
        }
    };
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM carregado, iniciando dashboard...');
    
    // Verificar se Chart.js foi carregado
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js não foi carregado!');
        return;
    } else {
        console.log('✅ Chart.js carregado, versão:', Chart.version);
    }
    
    // Verificar se os canvas existem
    const canvases = ['chartPizza', 'chartVendas', 'chartEstoque'];
    canvases.forEach(id => {
        const canvas = document.getElementById(id);
        console.log(`🎯 Canvas ${id}:`, !!canvas);
    });
    
    // Inicializar conexões
    initWS();
    
    // Fallback: polling a cada 10s
    setInterval(() => {
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
            fetchSnapshot();
        }
    }, 10000);
    
    // Carregar dados iniciais
    fetchSnapshot();
    
    // Atualizar histórico periodicamente
    setInterval(loadHistorico, 15000);
});
