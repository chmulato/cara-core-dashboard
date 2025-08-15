# Dashboard de Vendas e Estoque (Tempo Quase Real)

Este projeto fornece um exemplo simples de dashboard web em Python (FastAPI) que lê dados de um arquivo CSV exportado do Excel e atualiza a interface em "tempo quase real" usando WebSockets (quando disponível) e fallback por polling.

## Funcionalidades
- Leitura periódica/reativa de um arquivo CSV (`sample_data.csv`).
- Detecção de alterações via watchdog (monitor de sistema de arquivos) + checagem de timestamp.
- API REST (`/api/data`) para obtenção do snapshot atual.
- Canal WebSocket (`/ws`) para empurrar atualizações aos navegadores conectados.
- Página HTML única em `index.html` com gráficos simples (renderização DOM) sem dependências pesadas.
- Script opcional `update_simulator.py` para gerar linhas de vendas aleatórias (útil para demonstração).

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

## Execução
```
uvicorn app.main:app --reload --port 8000
```
Acesse: http://127.0.0.1:8000

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
Uso livre para fins educacionais/demonstração.
