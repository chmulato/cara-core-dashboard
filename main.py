#!/usr/bin/env python3
"""
Dashboard de Vendas & Estoque - Aplicação Principal
===================================================

Este é o ponto de entrada principal para o dashboard em tempo quase real.
Executa o servidor FastAPI/Uvicorn na porta 8000.

Uso:
    python main.py

Endpoints disponíveis:
    http://localhost:8000/         - Interface principal do dashboard
    http://localhost:8000/api/data - API com dados agregados
    http://localhost:8000/api/historico - API com histórico para gráficos
    ws://localhost:8000/ws         - WebSocket para atualizações em tempo real

Estrutura do projeto:
    main.py              - Este arquivo (entrada principal)
    app/                 - Código da aplicação web
    ├── main.py         - Aplicação FastAPI
    ├── data_loader.py  - Gerenciamento de dados CSV
    ├── logging_setup.py - Configuração de logs
    ├── sample_data.csv - Dados de exemplo
    ├── templates/      - Templates HTML
    └── static/         - Arquivos CSS/JS
    src/                - Scripts utilitários
    ├── generate_batch_data.py - Geração de massa de dados
    ├── update_simulator.py    - Simulação de atualizações
    └── quick_demo_data.py     - Dados demo para screenshots

Configuração via variáveis de ambiente:
    LOG_LEVEL   - Nível de log (DEBUG, INFO, WARNING, ERROR)
    LOG_FORMAT  - Formato dos logs (json, plain)
    LOG_DIR     - Diretório para arquivos de log
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    try:
        import fastapi
        import uvicorn
        import jinja2
        import watchdog
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("\n📦 Instale as dependências com:")
        print("   pip install -r requirements.txt")
        return False

def main():
    """Função principal - inicia o servidor do dashboard."""
    print("🚀 Dashboard de Vendas & Estoque")
    print("=" * 40)
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verifica se arquivo de dados existe
    data_file = Path("app/sample_data.csv")
    if not data_file.exists():
        print("⚠️  Arquivo de dados não encontrado!")
        print("📊 Gerando dados de exemplo...")
        
        # Executa script de geração de dados
        try:
            subprocess.run([
                sys.executable, "src/generate_batch_data.py",
                "--duracao-min", "120",
                "--intervalo-min", "5",
                "--produtos", "Produto A,Produto B,Produto C",
                "--estoque-inicial", "150"
            ], check=True)
            print("✅ Dados de exemplo gerados!")
        except subprocess.CalledProcessError:
            print("❌ Erro ao gerar dados de exemplo")
            sys.exit(1)
    
    print(f"📁 Arquivo de dados: {data_file}")
    print(f"📊 Linhas de dados: {len(data_file.read_text().splitlines()) - 1}")
    
    print("\n🌐 Iniciando servidor...")
    print("   URL: http://localhost:8000")
    print("   Ctrl+C para parar\n")
    
    try:
        # Inicia o servidor uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
