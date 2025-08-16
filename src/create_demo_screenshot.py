#!/usr/bin/env python3
"""
Script para gerar dados demo interessantes para screenshot
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

def gerar_dados_screenshot():
    """Gera dados interessantes para o dashboard demo"""
    
    # Configuração
    csv_path = Path(__file__).parent.parent / 'app' / 'sample_data.csv'
    
    # Produtos com nomes mais interessantes
    produtos = [
        "Smartphone Pro Max",
        "Notebook Gaming",
        "Tablet Ultra",
        "Smartwatch Elite",
        "Fones Bluetooth"
    ]
    
    # Hora atual como base
    agora = datetime.now()
    
    # Gerar dados das últimas 2 horas com intervalos de 5 minutos
    dados = []
    
    # Valores iniciais interessantes
    vendas_base = {"Smartphone Pro Max": 45, "Notebook Gaming": 28, "Tablet Ultra": 35, "Smartwatch Elite": 52, "Fones Bluetooth": 68}
    estoque_base = {"Smartphone Pro Max": 85, "Notebook Gaming": 42, "Tablet Ultra": 67, "Smartwatch Elite": 93, "Fones Bluetooth": 156}
    
    for i in range(25):  # 25 intervalos = 2 horas
        timestamp = agora - timedelta(minutes=5 * (24 - i))
        
        for produto in produtos:
            # Variação nas vendas (mais realista)
            variacao_vendas = random.randint(-3, 8)
            vendas_base[produto] = max(0, vendas_base[produto] + variacao_vendas)
            
            # Variação no estoque (decresce com vendas)
            variacao_estoque = random.randint(-2, 1)
            estoque_base[produto] = max(10, estoque_base[produto] + variacao_estoque - max(0, variacao_vendas))
            
            dados.append({
                'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M'),
                'produto': produto,
                'vendas': vendas_base[produto],
                'estoque': estoque_base[produto]
            })
    
    # Escrever CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'produto', 'vendas', 'estoque'])
        writer.writeheader()
        writer.writerows(dados)
    
    print(f"✅ Arquivo gerado: {csv_path} ({len(dados)} linhas)")
    print(f"📊 Produtos: {', '.join(produtos)}")
    print(f"⏰ Período: {dados[0]['timestamp']} até {dados[-1]['timestamp']}")
    
    # Mostrar resumo
    total_vendas = sum(row['vendas'] for row in dados[-5:])  # Últimas vendas
    print(f"💰 Total vendas atual: {total_vendas}")

if __name__ == "__main__":
    gerar_dados_screenshot()
