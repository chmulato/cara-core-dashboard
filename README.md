# Dashboard de Vendas & Estoque (Tempo Real)

<p align="center">
  <img src="article_43/media/article_43_03.png" alt="Dashboard de Vendas & Estoque em execução: gráfico pizza destacado, gráficos de linha e tabelas laterais" width="820" style="max-width:100%; border-radius:12px; box-shadow:0 4px 18px -4px rgba(0,0,0,0.25);" />
  <br>
  <em>Interface do dashboard em execução local (Chart.js v4.4.1)</em>
</p>

Este projeto fornece um sistema completo de dashboard web em Python (FastAPI) que monitora dados de um arquivo CSV exportado do Excel e atualiza a interface em tempo real usando WebSockets com fallback inteligente para polling. O dashboard apresenta layout responsivo profissional com foco em visualização de dados usando Chart.js v4.4.1.

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/chmulato/cara-core-dashboard.git
cd cara-core-dashboard

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o dashboard (detecção automática de porta)
python main.py
```

Acesse http://localhost:8000 (ou porta indicada no terminal se 8000 estiver ocupada).

## Funcionalidades Implementadas

- ✅ **Monitoramento Automático**: Watchdog + polling híbrido para detecção de mudanças no CSV
- ✅ **Comunicação Real-time**: WebSocket com reconnect automático e fallback para polling
- ✅ **Layout Responsivo**: Sistema dashboard-layout com CSS Grid e Flexbox
- ✅ **Gráfico Pizza Destacado**: Distribuição de vendas com design visual destacado
- ✅ **Gráficos Interativos**: Chart.js v4.4.1 com gráficos de linha para tendências
- ✅ **Sidebar Inteligente**: Tabelas organizadas na barra lateral
- ✅ **Detecção de Porta**: Sistema automático para evitar conflitos de porta
- ✅ **API REST Completa**: Endpoints para dados agregados e histórico
- ✅ **Logging Estruturado**: Sistema JSON com rotação de arquivos
- ✅ **Docker Ready**: Containerização para deploy em produção
- ✅ **CI/CD Pipeline**: GitHub Actions com testes e lint automatizados

## Estrutura do Projeto

```
├── main.py                     # Ponto de entrada principal (com detecção de porta)
├── app/                        # Aplicação web
│   ├── main.py                 # FastAPI app com WebSocket
│   ├── data_loader.py          # Gerencia leitura e difusão dos dados
│   ├── logging_setup.py        # Configuração de logging estruturado
│   ├── sample_data.csv         # Dados de exemplo (125 registros)
│   ├── templates/              # Templates HTML
│   │   └── index.html          # Interface com layout dashboard-layout
│   └── static/                 # Arquivos estáticos
│       ├── app_complete.js     # JavaScript com Chart.js integrado
│       └── styles.css          # CSS responsivo com Grid layout
├── src/                        # Scripts utilitários
│   ├── generate_batch_data.py  # Gera massa de dados
│   ├── update_simulator.py     # Simula atualizações em tempo real
│   └── quick_demo_data.py      # Dados demo para screenshots
├── tests/                      # Testes automatizados
├── requirements.txt            # Dependências
├── requirements-dev.txt        # Dependências de desenvolvimento
├── Dockerfile                  # Container Docker
└── README.md                   # Esta documentação
```

## Pré‑requisitos

- Python 3.10+ (testado e funcionando em Python 3.13)
- PowerShell (instruções Windows) ou bash (Linux/macOS)

**Observação sobre pandas**: O projeto funciona completamente mesmo sem pandas (usa fallback com `csv` nativo). Para funcionalidade completa com processamento avançado de datas:
```bash
pip install pandas==2.2.2
```

**Chart.js**: O sistema usa Chart.js v4.4.1 via CDN, sem necessidade de instalação local.

## Instalação

### Via Python (Recomendado)
```bash
# 1. Clone e entre no diretório
git clone https://github.com/chmulato/cara-core-dashboard.git
cd cara-core-dashboard

# 2. Crie ambiente virtual (opcional mas recomendado)
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute
python main.py
```

### Via Docker
```bash
# Build
docker build -t cara-core-dashboard .

# Run
docker run --rm -p 8000:8000 cara-core-dashboard
```

## Execução

### Método 1: Script Principal (Recomendado)
```bash
python main.py
```
Este método:
- ✅ Verifica dependências automaticamente
- ✅ Gera dados de exemplo se não existirem (125 registros realistas)
- ✅ **Detecta conflitos de porta automaticamente** (8000 → 8001 → 8002...)
- ✅ Inicia o servidor otimizado com configuração robusta
- ✅ Mostra informações úteis e URL de acesso

### Método 2: Uvicorn Direto
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Método 3: Com Logs Customizados
```bash
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; $env:LOG_FORMAT="plain"; python main.py

# Linux/macOS
LOG_LEVEL=DEBUG LOG_FORMAT=plain python main.py
```

**Acesso**: O terminal mostrará a URL correta (ex: http://localhost:8001)

## Interface do Dashboard

### Layout Responsivo Profissional
- **Cards de Métricas**: Total de vendas, última atualização, linhas CSV
- **Gráfico Pizza Destacado**: Distribuição de vendas com design visual diferenciado
- **Gráficos de Linha**: Histórico de vendas e estoque lado a lado
- **Sidebar Inteligente**: Tabelas de dados organizadas na barra lateral
- **Status de Conexão**: Indicador visual WebSocket/Polling em tempo real

### Tecnologias Frontend
- **Chart.js v4.4.1**: Gráficos interativos com canvas HTML5
- **CSS Grid + Flexbox**: Layout dashboard-layout responsivo
- **WebSocket + Polling**: Sistema híbrido para atualizações em tempo real
- **JavaScript ES6+**: Modular com async/await e gerenciamento de estado

## Configuração

### Variáveis de Ambiente (Logging)
- `LOG_LEVEL` - Nível de log: DEBUG, INFO (padrão), WARNING, ERROR
- `LOG_FORMAT` - Formato: `json` (padrão), `plain`
- `LOG_DIR` - Pasta de logs (padrão: `logs/`)

### Personalização do CSV
Estrutura requerida: `timestamp,produto,vendas,estoque`

Exemplo de dados compatíveis:
```csv
timestamp,produto,vendas,estoque
2025-08-15 14:30:00,Produto A,120,45
2025-08-15 14:33:00,Produto B,85,32
2025-08-15 14:36:00,Produto C,95,28
```

## Scripts Utilitários

### Gerar Dados Realistas (intervalos fixos)
```bash
# Gera série sintética realista (125 registros, 5 produtos)
python src/generate_batch_data.py

# Personalizar (240 min, passos de 5 min, produtos específicos)
python src/generate_batch_data.py --duracao-min 240 --intervalo-min 5 --produtos "Produto A,Produto B,Produto C,Produto D,Produto E" --estoque-inicial 150 --seed 42
```

### Simular Atualizações em Tempo Real
```bash
# Em outro terminal (mantém dashboard rodando)
python src/update_simulator.py
```
**Resultado**: Verá atualizações automáticas no dashboard via WebSocket
**Cancelamento**: Ctrl+C

### Dados Demo para Screenshots
```bash
# Gera pontos otimizados para captura de tela
python src/quick_demo_data.py
```

## Testes & Qualidade de Código

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
pytest -q

# Lint/formatação
ruff check .
```

## API Endpoints

| Endpoint | Método | Descrição | Status |
|----------|--------|-----------|---------|
| `/` | GET | Interface principal do dashboard | ✅ Implementado |
| `/api/data` | GET | Dados agregados (snapshot atual) | ✅ Implementado |
| `/api/historico?limit=N` | GET | Últimas N linhas para gráficos | ✅ Implementado |
| `/ws` | WebSocket | Canal de atualizações em tempo real | ✅ Implementado |

### Exemplo de Resposta `/api/data`:
```json
{
  "total_vendas": "10005",
  "estoque_por_produto": {
    "Produto A": 45,
    "Produto B": 32,
    "Produto C": 28,
    "Produto D": 15,
    "Produto E": 22
  },
  "vendas_por_produto": {
    "Produto A": 2180,
    "Produto B": 1820,
    "Produto C": 2050,
    "Produto D": 2155,
    "Produto E": 1800
  },
  "linhas": 125,
  "ultimo_timestamp": "2025-08-15T22:42:00",
  "atualizado_em": "2025-08-15T23:16:55"
}
```

## Docker

```bash
# Build local
docker build -t cara-core-dashboard .

# Run (mapeamento de porta flexível)
docker run --rm -p 8001:8000 cara-core-dashboard

# Com dados customizados (mount volume)
docker run --rm -p 8001:8000 -v $(pwd)/data:/app/app cara-core-dashboard
```

**Nota**: O container expõe porta 8000 internamente, mas você pode mapear para qualquer porta externa.

## Performance e Escalabilidade

### Otimizações Implementadas
- ✅ **WebSocket com Reconnect**: Sistema inteligente de reconexão automática
- ✅ **Fallback Polling**: Degradação graceful quando WebSocket falha  
- ✅ **Cache de Estado**: Snapshot em memória para respostas rápidas da API
- ✅ **Logging Assíncrono**: Sistema não-bloqueante com rotação de arquivos
- ✅ **Detecção de Porta**: Evita conflitos automaticamente
- ✅ **Layout Responsivo**: Adaptação automática a diferentes telas

### Métricas de Performance
- **Tempo de resposta API**: < 50ms para `/api/data`
- **Atualização WebSocket**: < 100ms após mudança no CSV
- **Renderização Chart.js**: Suporta até 1000 pontos fluido
- **Memória**: ~50MB para 10.000 registros CSV

## CI/CD

Workflow em `.github/workflows/ci.yml` executa automaticamente:
- Lint com Ruff
- Testes com Pytest
- Em cada push/pull request

## Próximos Passos (Roadmap)

### Funcionalidades Planejadas
- [ ] **Persistir histórico em banco** (SQLite/PostgreSQL) para dados históricos
- [ ] **Dashboards específicos** por produto/categoria com drill-down
- [ ] **Autenticação JWT** para acesso seguro e multi-usuário
- [ ] **Exportação de relatórios** (Excel/PDF) com agendamento
- [ ] **Métricas Prometheus** para monitoramento de infraestrutura
- [ ] **Deploy automático** (Heroku, Railway, Vercel) via GitHub Actions
- [ ] **Notificações push** (email, Slack, webhook) para alertas críticos
- [ ] **Cache Redis** para performance em alta escala
- [ ] **WebSocket rooms** para múltiplos usuários/departamentos
- [ ] **API GraphQL** para consultas flexíveis de dados

### Melhorias de UX/UI
- [ ] **Temas personalizáveis** (claro/escuro) com persistência
- [ ] **Filtros avançados** por data, produto, vendedor
- [ ] **Comparação de períodos** (mês vs mês anterior)
- [ ] **Alertas visuais** para metas e thresholds
- [ ] **Mobile-first responsive** design otimizado

## Licença

MIT - ver arquivo `LICENSE`.

## Contribuição

1. Fork o projeto no GitHub
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request com descrição detalhada

### Diretrizes para Contribuição
- ✅ Siga o padrão de código existente (ruff/black)
- ✅ Adicione testes para novas funcionalidades  
- ✅ Atualize a documentação quando necessário
- ✅ Teste em diferentes sistemas operacionais
- ✅ Use commits descritivos e organizados

## Suporte

- **Issues**: [GitHub Issues](https://github.com/chmulato/cara-core-dashboard/issues)
- **Discussões**: [GitHub Discussions](https://github.com/chmulato/cara-core-dashboard/discussions)
- **Documentação**: Este README + comentários no código
- **Wiki**: [Guias detalhados](https://github.com/chmulato/cara-core-dashboard/wiki)

### Como Reportar Bugs
1. Verifique se o issue já existe
2. Inclua informações do sistema (OS, Python version)
3. Descreva passos para reproduzir
4. Anexe logs relevantes (remova dados sensíveis)

---

**🌟 Se este projeto foi útil, considere dar uma estrela no GitHub!**

**📧 Para projetos comerciais ou consultorias, entre em contato via Issues.**
