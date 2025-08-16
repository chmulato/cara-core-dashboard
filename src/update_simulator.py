"""Gera linhas aleatórias no CSV para demonstrar atualização em tempo quase real.

Uso:
  python update_simulator.py
Parar com Ctrl+C.
"""
from __future__ import annotations
import random
import time
from pathlib import Path
from datetime import datetime
import csv

CSV_PATH = Path(__file__).parent / 'app' / 'sample_data.csv'
PRODUTOS = ["Produto A", "Produto B", "Produto C", "Produto D"]


def ler_estoques_existentes():
    estoque = {p: 100 for p in PRODUTOS}
    if not CSV_PATH.exists():
        return estoque
    try:
        with CSV_PATH.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                p = row.get('produto')
                try:
                    est = int(row.get('estoque', '') or 0)
                except ValueError:
                    continue
                if p:
                    estoque[p] = est
    except Exception:
        pass
    return estoque


def append_linha(produto: str, vendas: int, estoque: int):
    header = ['timestamp', 'produto', 'vendas', 'estoque']
    file_exists = CSV_PATH.exists()
    with CSV_PATH.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.utcnow().isoformat(timespec='seconds'),
            'produto': produto,
            'vendas': vendas,
            'estoque': estoque,
        })


def main():
    estoque = ler_estoques_existentes()
    print(f"Simulador escrevendo em {CSV_PATH}")
    while True:
        produto = random.choice(PRODUTOS)
        vendas = random.randint(1, 8)
        estoque[produto] = max(0, estoque.get(produto, 100) - vendas)
        append_linha(produto, vendas, estoque[produto])
        print(f"Linha adicionada: {produto} vendas={vendas} estoque={estoque[produto]}")
        time.sleep(random.uniform(3, 8))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
