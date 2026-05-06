import json
from datetime import datetime, timedelta, timezone

print("--------------------------")
num_reais = {"impares": [], "pares": []}

n = 0

for n in range(10):
    if n % 2 == 0:
        num_reais["pares"].append(n)
    else:
        num_reais["impares"].append(n)

contador_impares = len(num_reais.get("impares", []))
contador_pares = len(num_reais.get("pares", []))
contador_por_chave = {k: len(v) for k, v in num_reais.items()}
contador_total = sum(len(v) for v in num_reais.values())


print("numeros reais: ", num_reais)
print("contador de impares: ", contador_impares)
print("contador de pares: ", contador_pares)
print("contador por chave: ", contador_por_chave)
print("contador total: ", contador_total)
print("--------------------------")
