import pandas as pd
import numpy as np

np.random.seed(42)

datas = pd.date_range(start="2024-01-01", end="2024-12-31")

produtos = [
    ("Trufa", "Premium", 8, 3),
    ("Barra 100g", "Tradicional", 12, 5),
    ("Caixa de Bombom", "Presente", 35, 18),
    ("Ovo de Páscoa", "Sazonal", 80, 40),
    ("Chocolate Amargo", "Premium", 15, 7)
]

dados = []

for data in datas:
    for produto, categoria, preco, custo in produtos:

        fator = 1

        if data.month == 4:
            fator = 3
        elif data.month == 12:
            fator = 2

        quantidade = int(np.random.randint(20, 100) * fator)

        dados.append([
            data,
            produto,
            categoria,
            preco,
            custo,
            quantidade
        ])

df = pd.DataFrame(dados, columns=[
    "data", "produto", "categoria", "preco", "custo", "quantidade"
])

df["faturamento"] = df["preco"] * df["quantidade"]
df["custo_total"] = df["custo"] * df["quantidade"]
df["lucro"] = df["faturamento"] - df["custo_total"]

df.insert(0, 'nota_fiscal', ['NF' + str(i).zfill(5) for i in range(1, len(df)+1)])

df.to_csv("data/vendas.csv", index=False)

print("Dataset gerado com sucesso!")