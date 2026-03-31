import pandas as pd

df = pd.read_csv('data/vendas.csv')

print("\n===== VISÃO GERAL =====")
print("Faturamento total:", df['faturamento'].sum())
print("Lucro total:", df['lucro'].sum())

print("\n===== TOP PRODUTOS =====")
print(df.groupby('produto')['faturamento'].sum().sort_values(ascending=False))

print("\n===== POR CATEGORIA =====")
print(df.groupby('categoria')['faturamento'].sum())

df['data'] = pd.to_datetime(df['data'])
df['mes'] = df['data'].dt.month

print("\n===== POR MÊS =====")
print(df.groupby('mes')['faturamento'].sum().sort_index())

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# agrupamento
faturamento_mes = df.groupby('mes')['faturamento'].sum().sort_index()

meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

plt.figure(figsize=(14, 6))  # mais espaço horizontal

# barras mais finas
bars = plt.bar(meses, faturamento_mes, width=0.5)

plt.title('Faturamento Mensal - Loja de Chocolates', fontsize=14)
plt.xlabel('Mês')
plt.ylabel('Faturamento (R$)')

# 💰 formatação brasileira com ,00
def formato_moeda(x, pos):
    return f'R$ {int(x):,}'.replace(',', '.') + ',00'

plt.gca().yaxis.set_major_formatter(FuncFormatter(formato_moeda))

# 🔥 destacar abril e dezembro
for i, bar in enumerate(bars):
    if i == 3 or i == 11:
        bar.set_alpha(1)
    else:
        bar.set_alpha(0.6)

# espaço no topo
plt.ylim(0, faturamento_mes.max() * 1.15)

# 💰 valores nas barras (melhor espaçamento)
for i, valor in enumerate(faturamento_mes):
    texto = f'R$ {int(valor):,}'.replace(',', '.') + ',00'
    plt.text(
        i,
        valor + faturamento_mes.max() * 0.03,
        texto,
        ha='center',
        fontsize=8,
        rotation=20
    )

plt.tight_layout()
plt.show()