#!/usr/bin/env python3
"""
Script rápido para gerar dados demo em tempo real para screenshots.
Adiciona pontos a cada 2 segundos para mostrar atualização ao vivo.
"""
import csv
import time
import random
from datetime import datetime, timedelta

def add_demo_point():
    """Adiciona um ponto de dados atual para simular tempo real."""
    produtos = ["Produto A", "Produto B", "Produto C", "Produto D", "Produto E"]
    
    # Lê dados existentes para manter continuidade do estoque
    estoque_atual = {"Produto A": 180, "Produto B": 190, "Produto C": 185, "Produto D": 195, "Produto E": 188}
    
    try:
        with open('app/sample_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                # Pega últimos estoques por produto
                for row in reversed(rows[-10:]):  # últimas 10 linhas
                    produto = row.get('produto')
                    if produto in estoque_atual:
                        try:
                            estoque_atual[produto] = int(row.get('estoque', estoque_atual[produto]))
                        except (ValueError, TypeError):
                            pass
    except Exception:
        pass  # usa valores padrão
    
    # Timestamp atual
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%dT%H:%M")
    
    # Gera novos pontos de venda
    with open('app/sample_data.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for produto in produtos:
            vendas = random.randint(0, 8)  # vendas moderadas
            estoque_atual[produto] = max(0, estoque_atual[produto] - vendas)  # deduz vendas
            writer.writerow([timestamp_str, produto, vendas, estoque_atual[produto]])
    
    print(f"✓ Adicionado ponto {timestamp_str} - Total vendas: {sum(random.randint(0,8) for _ in produtos)}")

if __name__ == "__main__":
    print("🚀 Gerando dados demo em tempo real...")
    print("Pressione Ctrl+C para parar")
    
    try:
        for i in range(10):  # 10 pontos = 20 segundos
            add_demo_point()
            time.sleep(2)  # aguarda 2 segundos
    except KeyboardInterrupt:
        print("\n⏹️ Parado pelo usuário")
    
    print("✅ Dados demo finalizados!")
