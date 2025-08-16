console.log('🚀 JavaScript funcional carregado!');

// Estado global
const state = {
    ws: null,
    charts: {},
    lastData: null
};

// Utilitário para buscar elementos
function $(id) { 
    return document.getElementById(id); 
}

// Função principal para atualizar os dados na tela
function updateDashboard(data) {
    console.log('📊 Atualizando dashboard com dados:', data);
    
    // Atualizar métricas principais
    if ($('totalVendas')) $('totalVendas').textContent = data.total_vendas || '--';
    if ($('ultimaAtualizacao')) $('ultimaAtualizacao').textContent = data.ultimo_timestamp || '--';
    if ($('linhasCsv')) $('linhasCsv').textContent = data.linhas || '--';
    if ($('atualizadoEm')) $('atualizadoEm').textContent = data.atualizado_em || '--';
    
    // Atualizar status para mostrar que está conectado
    if ($('status')) {
        $('status').textContent = 'Dados carregados!';
        $('status').className = 'status ok';
    }
    
    // Atualizar tabelas
    updateTable('tabelaVendas', data.vendas_por_produto || {}, 'Vendas');
    updateTable('tabelaEstoque', data.estoque_por_produto || {}, 'Estoque');
    
    // Armazenar dados para uso posterior
    state.lastData = data;
    
    console.log('✅ Dashboard atualizado com sucesso!');
}

// Função para atualizar tabelas
function updateTable(tableId, dataObj, label) {
    const table = $(tableId);
    if (!table) {
        console.warn(`⚠️ Tabela ${tableId} não encontrada`);
        return;
    }
    
    const tbody = table.querySelector('tbody');
    if (!tbody) {
        console.warn(`⚠️ tbody não encontrado na tabela ${tableId}`);
        return;
    }
    
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
        const tdProduto = document.createElement('td');
        const tdValor = document.createElement('td');
        
        tdProduto.textContent = produto;
        tdValor.textContent = valor;
        
        tr.appendChild(tdProduto);
        tr.appendChild(tdValor);
        tbody.appendChild(tr);
    }
    
    console.log(`✅ Tabela ${tableId} atualizada com ${entries.length} itens`);
}

// Função para buscar dados da API
async function fetchData() {
    try {
        console.log('🔄 Buscando dados da API...');
        
        const response = await fetch('/api/data');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos da API:', data);
        
        updateDashboard(data);
        
        return data;
        
    } catch (error) {
        console.error('❌ Erro ao buscar dados:', error);
        
        if ($('status')) {
            $('status').textContent = 'Erro ao carregar dados';
            $('status').className = 'status err';
        }
        
        throw error;
    }
}

// Função para inicializar WebSocket (simplificada)
function initWebSocket() {
    try {
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${protocol}://${location.host}/ws`;
        
        console.log('🔗 Conectando WebSocket:', wsUrl);
        
        const ws = new WebSocket(wsUrl);
        state.ws = ws;
        
        ws.onopen = function() {
            console.log('✅ WebSocket conectado');
            if ($('status')) {
                $('status').textContent = 'Tempo real ativo';
                $('status').className = 'status ok';
            }
        };
        
        ws.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'snapshot' && message.data) {
                    console.log('📡 Dados recebidos via WebSocket:', message.data);
                    updateDashboard(message.data);
                }
            } catch (error) {
                console.error('❌ Erro ao processar mensagem WebSocket:', error);
            }
        };
        
        ws.onerror = function(error) {
            console.error('❌ Erro no WebSocket:', error);
        };
        
        ws.onclose = function() {
            console.log('🔌 WebSocket desconectado');
            if ($('status')) {
                $('status').textContent = 'Modo polling ativo';
                $('status').className = 'status err';
            }
        };
        
    } catch (error) {
        console.error('❌ Erro ao inicializar WebSocket:', error);
    }
}

// Inicialização quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - inicializando dashboard...');
    
    // Configurar status inicial
    if ($('status')) {
        $('status').textContent = 'Carregando...';
        $('status').className = 'status';
    }
    
    // Buscar dados iniciais
    fetchData().then(() => {
        console.log('✅ Dados iniciais carregados');
    }).catch((error) => {
        console.error('❌ Falha ao carregar dados iniciais:', error);
    });
    
    // Inicializar WebSocket
    initWebSocket();
    
    // Fallback: polling a cada 10 segundos
    setInterval(() => {
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
            console.log('🔄 Fazendo polling (WebSocket inativo)...');
            fetchData().catch(() => {
                // Ignorar erros do polling
            });
        }
    }, 10000);
    
    console.log('🎉 Dashboard inicializado com sucesso!');
});

// Logs de debug
console.log('📝 Funções JavaScript carregadas:', {
    updateDashboard: typeof updateDashboard,
    updateTable: typeof updateTable,
    fetchData: typeof fetchData,
    initWebSocket: typeof initWebSocket
});
