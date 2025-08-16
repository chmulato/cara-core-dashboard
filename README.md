# Dashboard de Vendas & Estoque (Tempo Quase Real)

Este projeto fornece um exemplo completo de dashboard web em Python (FastAPI) que lê dados de um arquivo CSV exportado do Excel e atualiza a interface em "tempo quase real" usando WebSockets (quando disponível) e fallback por polling.

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/chmulato/cara-core-dashboard.git
cd cara-core-dashboard

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o dashboard
python main.py
```

Abra http://localhost:8000 no navegador.

## Funcionalidades

- Leitura periódica/reativa de um arquivo CSV (`app/sample_data.csv`)
- Detecção de alterações via watchdog (monitor de sistema de arquivos) + checagem de timestamp
- API REST (`/api/data`) para obtenção do snapshot atual
- Canal WebSocket (`/ws`) para empurrar atualizações aos navegadores conectados
- Interface web com gráficos interativos (Chart.js):
  - Métricas principais (vendas totais, última atualização, linhas CSV)
  - Tabelas de vendas e estoque por produto
  - Gráficos de séries temporais de vendas e estoque
  - **Gráfico de pizza** com distribuição de vendas por produto
- Scripts utilitários para geração e simulação de dados
- Logging estruturado (JSON) com rotação de arquivos
- Dockerfile para containerização
- Workflow CI (pytest + ruff) via GitHub Actions

## Estrutura do Projeto

```
├── main.py                     # Ponto de entrada principal
├── app/                        # Aplicação web
│   ├── main.py                #    FastAPI app
│   ├── data_loader.py         #    Gerencia leitura e difusão dos dados
│   ├── logging_setup.py       #    Configuração de logging
│   ├── sample_data.csv        #    Dados de exemplo
│   ├── templates/             #    Templates HTML
│   │   └── index.html
│   └── static/                #    Arquivos estáticos
│       ├── app.js
│       └── styles.css
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

- Python 3.10+
- PowerShell (instruções Windows) ou bash (Linux/macOS)

**Observação sobre pandas**: Em alguns ambientes (ex.: Python 3.13 sem Visual Studio Build Tools) a instalação de `pandas` pode falhar por ausência de wheels. O projeto funciona mesmo sem `pandas` (usa um fallback com `csv`), porém sem algumas conversões de datas mais ricas. Para habilitar processamento completo:
```bash
pip install pandas==2.2.2
```
Recomenda-se usar Python 3.12 para obter wheel binário pronto.

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
- Verifica dependências automaticamente
- Gera dados de exemplo se não existirem
- Inicia o servidor otimizado
- Mostra informações úteis

### Método 2: Uvicorn Direto
```bash
uvicorn app.main:app --port 8000
```

### Método 3: Com Logs Customizados
```bash
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; $env:LOG_FORMAT="plain"; python main.py

# Linux/macOS
LOG_LEVEL=DEBUG LOG_FORMAT=plain python main.py
```

Acesse: http://localhost:8000

## Configuração

### Variáveis de Ambiente (Logging)
- `LOG_LEVEL` - Nível de log: DEBUG, INFO (padrão), WARNING, ERROR
- `LOG_FORMAT` - Formato: `json` (padrão), `plain`
- `LOG_DIR` - Pasta de logs (padrão: `logs/`)

### Personalização do CSV
Mantenha cabeçalho com colunas mínimas: `timestamp,produto,vendas,estoque`.

## Scripts Utilitários

### Gerar Massa de Dados (intervalos fixos)
```bash
# Gera série sintética (padrão: últimos 30 min em passos de 5 min)
python src/generate_batch_data.py

# Personalizar (60 min, passos de 2 min, 5 produtos)
python src/generate_batch_data.py --duracao-min 60 --intervalo-min 2 --produtos "Produto A,Produto B,Produto C,Produto D,Produto E" --estoque-inicial 120 --seed 42
```

### Simular Atualizações em Tempo Real
```bash
# Em outro terminal com o ambiente ativo
python src/update_simulator.py
```
Cancelamento: Ctrl+C.

### Dados Demo para Screenshots
```bash
# Gera pontos a cada 2 segundos por 20 segundos
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

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Interface principal do dashboard |
| `/api/data` | GET | Dados agregados (snapshot atual) |
| `/api/historico?limit=N` | GET | Últimas N linhas para gráficos |
| `/ws` | WebSocket | Canal de atualizações em tempo real |

### Exemplo de Resposta `/api/data`:
```json
{
  "total_vendas": 1250,
  "estoque_por_produto": {
    "Produto A": 45,
    "Produto B": 32
  },
  "vendas_por_produto": {
    "Produto A": 780,
    "Produto B": 470
  },
  "linhas": 150,
  "ultimo_timestamp": "2025-08-15T14:30:00",
  "atualizado_em": "2025-08-15T14:30:15"
}
```

## Docker

```bash
# Build local
docker build -t cara-core-dashboard .

# Run
docker run --rm -p 8000:8000 cara-core-dashboard

# Com dados customizados (mount volume)
docker run --rm -p 8000:8000 -v $(pwd)/data:/app/app cara-core-dashboard
```

## CI/CD

Workflow em `.github/workflows/ci.yml` executa automaticamente:
- Lint com Ruff
- Testes com Pytest
- Em cada push/pull request

## Próximos Passos (Sugestões)

- [ ] Persistir histórico em banco (SQLite/PostgreSQL)
- [ ] Adicionar agregações avançadas e dashboards específicos
- [ ] Autenticação básica (JWT)
- [ ] Exportação de relatórios (Excel/PDF)
- [ ] Métricas Prometheus para monitoramento
- [ ] Deploy automático (Heroku, Railway, Vercel)
- [ ] Notificações (email, Slack) para alertas
- [ ] Cache Redis para performance
- [ ] Websocket com rooms para múltiplos usuários

## Licença

MIT - ver arquivo `LICENSE`.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

- **Issues**: [GitHub Issues](https://github.com/chmulato/cara-core-dashboard/issues)
- **Email**: [Criar issue no GitHub]
- **Documentação**: Este README + comentários no código

---

**Se este projeto foi útil, considere dar uma estrela no GitHub!**
