console.log('🧪 JavaScript de teste carregado!');

// Função simples para testar
function testarAPI() {
    console.log('🔍 Testando API...');
    
    fetch('/api/data')
        .then(response => {
            console.log('✅ Resposta recebida:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📊 Dados:', data);
            document.getElementById('totalVendas').textContent = data.total_vendas || 'Erro';
            document.getElementById('status').textContent = 'API OK';
            document.getElementById('status').className = 'status ok';
        })
        .catch(error => {
            console.error('❌ Erro:', error);
            document.getElementById('status').textContent = 'Erro API';
            document.getElementById('status').className = 'status err';
        });
}

// Testar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - iniciando teste...');
    
    // Testar imediatamente
    setTimeout(testarAPI, 1000);
    
    // Testar a cada 5 segundos
    setInterval(testarAPI, 5000);
});
