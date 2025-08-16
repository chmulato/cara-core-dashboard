"""Gera massa de dados em intervalos de 5 minutos cobrindo uma janela de tempo (default 30 minutos).

Uso básico:
  python generate_batch_data.py

Opções:
  --duracao-min 30        (duração total em minutos)
  --intervalo-min 5       (intervalo entre registros)
  --produtos "Produto A,Produto B,Produto C"  (lista de produtos)
  --estoque-inicial 100   (estoque inicial por produto)
  --saida app/sample_data.csv
  --seed 42               (semente para reprodutibilidade)

O script sobrescreve o arquivo de saída.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import csv
import random
from pathlib import Path


def gerar_dados(
    saida: Path,
    duracao_min: int = 30,
    intervalo_min: int = 5,
    produtos: list[str] | None = None,
    estoque_inicial: int = 100,
    seed: int | None = None,
):
    if seed is not None:
        random.seed(seed)
    if produtos is None:
        produtos = ["Produto A", "Produto B", "Produto C"]
    agora = datetime.now(timezone.utc)
    inicio = agora - timedelta(minutes=duracao_min)
    passos = int(duracao_min / intervalo_min) + 1
    estoque = {p: estoque_inicial for p in produtos}
    rows: list[dict[str, str | int]] = []
    for i in range(passos):
        ts = inicio + timedelta(minutes=i * intervalo_min)
        # Para cada produto, gerar vendas aleatórias (podem ser zero)
        for p in produtos:
            vendas = random.randint(0, 10)
            estoque[p] = max(0, estoque[p] - vendas)
            rows.append(
                {
                    'timestamp': ts.replace(tzinfo=None).isoformat(timespec='minutes'),
                    'produto': p,
                    'vendas': vendas,
                    'estoque': estoque[p],
                }
            )
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'produto', 'vendas', 'estoque'])
        writer.writeheader()
        writer.writerows(rows)
    return saida, len(rows)


def main():
    parser = argparse.ArgumentParser(description="Gerar massa de dados de vendas/estoque.")
    parser.add_argument('--duracao-min', type=int, default=30)
    parser.add_argument('--intervalo-min', type=int, default=5)
    parser.add_argument('--produtos', type=str, default="Produto A,Produto B,Produto C")
    parser.add_argument('--estoque-inicial', type=int, default=100)
    parser.add_argument('--saida', type=str, default="app/sample_data.csv")
    parser.add_argument('--seed', type=int, default=None)
    args = parser.parse_args()
    produtos = [p.strip() for p in args.produtos.split(',') if p.strip()]
    saida, total = gerar_dados(
        Path(args.saida),
        duracao_min=args.duracao_min,
        intervalo_min=args.intervalo_min,
        produtos=produtos,
        estoque_inicial=args.estoque_inicial,
        seed=args.seed,
    )
    print(f"Arquivo gerado: {saida} ({total} linhas)")


if __name__ == '__main__':
    main()
