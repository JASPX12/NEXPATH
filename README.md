
# 🧭 NEXPATH — Rutas Óptimas y Seguras en Medellín

Sistema que calcula y visualiza rutas óptimas entre zonas de Medellín considerando **distancia** y **riesgo de acoso**, implementando los algoritmos **Dijkstra** y **Bellman-Ford** desde cero.

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## ▶️ Uso

```bash
python app.py
```

Luego abre **http://localhost:5000** en el navegador.

## ⚙️ Parámetros configurables

| Parámetro | Descripción |
|---|---|
| **Alpha (α)** | Peso de la distancia (0 = ignora distancia, 1 = solo distancia) |
| **Beta (β)** | Peso del riesgo de acoso (0 = ignora riesgo, 1 = solo seguridad) |
| **Preferencia** | Balanceado (α=0.5, β=0.5) / Más Rápido (α=1, β=0) / Más Seguro (α=0, β=1) |
| **Modo** | Ambos algoritmos / Solo Dijkstra / Solo Bellman-Ford |

## 📊 Fórmula de costo

**C(e) \= α×length(e) \+ β×harassmentRisk(e)**

donde:

* `α` y `β` son pesos ajustables definidos por el usuario según su preferencia entre **rapidez** y **seguridad**.

## 🗂️ Estructura del proyecto

NEXPATH/
├── app.py                  # Servidor Flask y lógica principal
├── algoritmos/
│   ├── dijkstra.py         # Implementación de Dijkstra
│   └── bellman_ford.py     # Implementación de Bellman-Ford
├── graph/
│   └── grafo.py            # Estructura del grafo (lista de adyacencia)
├── datos/
│   ├── cargar_datos.py     # Carga del CSV
│   └── calles_de_medellin_con_acoso.csv
├── visualizacion/
│   └── mapa.py             # Generación del mapa con Folium
└── requirements.txt
