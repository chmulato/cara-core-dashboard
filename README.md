# Dashboard de Vendas e Estoque (Tempo Quase Real)

Este projeto fornece um exemplo simples de dashboard web em Python (FastAPI) que lê dados de um arquivo CSV exportado do Excel e atualiza a interface em "tempo quase real" usando WebSockets (quando disponível) e fallback por polling.

## Funcionalidades
- Leitura periódica/reativa de um arquivo CSV (`sample_data.csv`).
- Detecção de alterações via watchdog (monitor de sistema de arquivos) + checagem de timestamp.
- API REST (`/api/data`) para obtenção do snapshot atual.
- Canal WebSocket (`/ws`) para empurrar atualizações aos navegadores conectados.
- Página HTML única em `index.html` com gráficos simples (renderização DOM) sem dependências pesadas.
- Script opcional `update_simulator.py` para gerar linhas de vendas aleatórias (útil para demonstração).
- Endpoint histórico `/api/historico?limit=100` e gráficos (Chart.js) de séries temporais de vendas e estoque.
- Dockerfile para containerizar a aplicação.
- Workflow CI (pytest + ruff) via GitHub Actions.

## Estrutura
```
app/
  main.py            # App FastAPI
  data_loader.py     # Gerencia leitura e difusão dos dados
  templates/index.html
  static/app.js
  static/styles.css
  sample_data.csv     # Dados iniciais
update_simulator.py   # Gera dados aleatórios (opcional)
requirements.txt
```

## Pré‑requisitos
- Python 3.10+
- PowerShell (instruções abaixo) no Windows.

## Instalação
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
### Variáveis de Ambiente (Logging)
```
$env:LOG_LEVEL="DEBUG"; $env:LOG_FORMAT="plain"; uvicorn app.main:app --reload --port 8000
```
LOG_LEVEL (INFO padrão), LOG_FORMAT (json/plain), LOG_DIR (pasta logs).

## Execução
```
uvicorn app.main:app --reload --port 8000
```
Acesse: http://127.0.0.1:8000

### Testes & Lint
```
pip install -r requirements-dev.txt
pytest -q
ruff check .
```

### Docker
```
docker build -t cara-core-dashboard .
docker run --rm -p 8000:8000 cara-core-dashboard
```

## Publicação no GitHub
Este projeto pode ser publicado no repositório `cara-core-dashboard`.

Passos (uma vez):
```
git init
git add .
git commit -m "feat: primeira versão do dashboard"
git branch -M main
git remote add origin https://github.com/chmulato/cara-core-dashboard.git
git push -u origin main
```
Se o repositório remoto já tiver commits, faça antes:
```
git remote add origin https://github.com/chmulato/cara-core-dashboard.git
git fetch origin
git merge origin/main --allow-unrelated-histories
git push -u origin main
```
Caso use token pessoal (PAT), substitua a URL por `https://<TOKEN>@github.com/chmulato/cara-core-dashboard.git` (atenção para não commitar o token).

## Simular Atualizações
Em outro terminal com o ambiente ativo:
```
python update_simulator.py
```
Cancelamento: Ctrl+C.

## Personalização do CSV
Mantenha cabeçalho com colunas mínimas: `timestamp,produto,vendas,estoque`.

## Próximos Passos (Sugestões)
- Persistir histórico em banco (SQLite/PostgreSQL).
- Adicionar agregações avançadas e gráficos via Chart.js ou ECharts.
- Autenticação básica.
- Exportação de relatórios (Excel/PDF).

## Licença
MIT - ver arquivo `LICENSE`.

## CI
Workflow em `.github/workflows/ci.yml` roda lint e testes em cada push/pull request.
