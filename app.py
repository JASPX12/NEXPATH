from flask import Flask, request, render_template_string
from flask_cors import CORS
from graph.grafo import Grafo
from datos.cargar_datos import save_data
from algoritmos import dijkstra, bellman_ford
from visualizacion.mapa import generar_mapa
import time
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# ── Zonas disponibles (coordenadas exactas del dataset) ──────────────────────

ZONAS = {
    "El Poblado":      (-75.5696716, 6.2102203),
    "Laureles":        (-75.598206,  6.2451823),
    "Envigado":        (-75.5794522, 6.1836962),
    "Centro":          (-75.5630251, 6.2519453),
    "Belén":           (-75.615629,  6.2322545),
    "Itagüí":          (-75.5921617, 6.1969457),
    "El Estadio":      (-75.5930617, 6.2574122),
    "Arví (Nororiente)":     (-75.577335, 6.2833305),      
    "Sabaneta (Sur)":        (-75.644959, 6.1816863),      
    "Robledo (Noroccidente)": (-75.621713, 6.2564349),    
    "San Alejo (Noroccidente)": (-75.6211789, 6.2433438), 
    "Villa Hermosa (Norte)":  (-75.6125919, 6.2328901),   
    "Castilla (Occidente)":   (-75.6042832, 6.2613864),   
    "Buenvista (Noroccidente)": (-75.5966742, 6.2607663), 
    "San Javier (Nororiente)": (-75.5832441, 6.2936879),  
    "Manrique (Nororiente)":   (-75.5820654, 6.2995547),  
    "Doce de Octubre (Noroccidente)": (-75.5757241, 6.2936987), 
}
PREFERENCIA_LABELS = {
    "balanced": "Balanceado",
    "fast":     "Más Rápido",
    "safe":     "Más Seguro",
}

# ── Cargar grafo una sola vez ────────────────────────────────────────────────
def coord_a_tupla(coord_str):
    coord_str = coord_str.strip("()")
    lon, lat = coord_str.split(",")
    return (float(lon), float(lat))

def crear_grafo_con_datos(datos):
    grafo = Grafo()
    for _, fila in datos.iterrows():
        origen  = coord_a_tupla(fila["origin"])
        destino = coord_a_tupla(fila["destination"])
        grafo.crear_interseccion(
            fila["name"], origen, destino,
            float(fila["length"]), bool(fila["oneway"]),
            float(fila["harassmentRisk"]), fila["geometry"]
        )
    return grafo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "datos", "calles_de_medellin_con_acoso.csv")
datos = save_data(CSV_PATH)
grafo = crear_grafo_con_datos(datos)
print("✅ Grafo cargado correctamente")

# ── Template HTML ─────────────────────────────────────────────────────────────
TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>NEXPATH</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; background: #131313; color: #e5e2e1; font-family: 'Inter', sans-serif; }
    .layout { display: flex; height: 100vh; overflow: hidden; }

    .sidebar {
      width: 280px; min-width: 280px; background: #202020;
      border-right: 1px solid #424754; display: flex; flex-direction: column;
      height: 100vh; overflow-y: auto;
    }
    .sidebar-header { padding: 20px 24px 16px; border-bottom: 1px solid #424754; }
    .sidebar-header h1 { font-family: 'Geist', sans-serif; font-size: 22px; font-weight: 700; color: #adc6ff; }
    .sidebar-header p  { font-size: 11px; color: #8c909f; margin-top: 2px; }
    .sidebar-body { padding: 20px 20px; display: flex; flex-direction: column; gap: 18px; flex: 1; }

    label { font-size: 11px; font-weight: 600; color: #8c909f; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 6px; }

    select {
      width: 100%; background: #2a2a2a; border: 1px solid #424754;
      border-radius: 8px; color: #e5e2e1; font-size: 13px;
      height: 38px; padding: 0 12px; outline: none;
    }
    select:focus { border-color: #adc6ff; }

    input[type=range] { width: 100%; height: 4px; padding: 0; border: none; border-radius: 2px; cursor: pointer; accent-color: #adc6ff; }

    .slider-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .slider-val { font-size: 13px; font-family: 'Geist', sans-serif; font-weight: 600; }

    .btn {
      width: 100%; background: #adc6ff; color: #002e6a;
      border: none; border-radius: 8px; padding: 12px;
      font-size: 14px; font-weight: 700; cursor: pointer;
      font-family: 'Geist', sans-serif; transition: background 0.2s;
      display: flex; align-items: center; justify-content: center; gap: 8px;
    }
    .btn:hover { background: #d8e2ff; }

    .leyenda { background: #2a2a2a; border: 1px solid #424754; border-radius: 8px; padding: 12px; }
    .leyenda p { font-size: 11px; font-weight: 600; color: #8c909f; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .leyenda-item { display: flex; align-items: center; gap: 8px; font-size: 12px; margin-bottom: 4px; }
    .dot { width: 12px; height: 4px; border-radius: 2px; display: inline-block; }

    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .topbar {
      height: 52px; border-bottom: 1px solid #424754; background: #131313;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 24px; flex-shrink: 0;
    }
    .topbar h2 { font-family: 'Geist', sans-serif; font-size: 15px; font-weight: 600; }
    .topbar span { font-size: 13px; color: #8c909f; margin-left: 8px; font-weight: 400; }

    .content { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 12px; gap: 12px; }

    .map-container {
      flex: 1; border-radius: 12px; border: 1px solid #424754;
      overflow: hidden; background: #1b1b1c; position: relative; min-height: 0;
    }
    .map-container iframe { width: 100%; height: 100%; border: none; display: block; }
    .map-placeholder {
      display: flex; align-items: center; justify-content: center;
      height: 100%; color: #424754; font-size: 14px; flex-direction: column; gap: 8px;
    }

    .metricas { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; flex-shrink: 0; }
    .metrica-card { background: #202020; border: 1px solid #424754; border-radius: 10px; padding: 12px 14px; }
    .metrica-card .titulo { font-size: 10px; color: #8c909f; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .metrica-card .valores { display: flex; flex-direction: column; gap: 3px; }
    .metrica-card .fila { display: flex; justify-content: space-between; align-items: center; }
    .metrica-card .algo { font-size: 11px; }
    .metrica-card .val { font-size: 13px; font-weight: 600; font-family: 'Geist', sans-serif; }
    .cyan    { color: #4cd7f6; }
    .naranja { color: #ffb786; }

    .tabla-section { background: #1b1b1c; border: 1px solid #424754; border-radius: 10px; overflow: hidden; flex-shrink: 0; }
    .tabla-header { padding: 10px 16px; border-bottom: 1px solid #424754; font-size: 12px; font-weight: 600; font-family: 'Geist', sans-serif; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; }
    th { padding: 8px 14px; text-align: left; background: #2a2a2a; color: #8c909f; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    td { padding: 10px 14px; border-top: 1px solid #424754; }
    tr:hover td { background: #2a2a2a; }
    .bar-wrap { width: 80px; height: 5px; background: #424754; border-radius: 3px; overflow: hidden; }
    .bar { height: 100%; border-radius: 3px; }
  </style>
</head>
<body>
<div class="layout">

  <nav class="sidebar">
    <div class="sidebar-header">
      <h1>NEXPATH</h1>
      <p>Motor de Optimización de Rutas</p>
    </div>
    <div class="sidebar-body">
      <form method="POST" action="/" id="form">

        <div>
          <label>Origen</label>
          <select name="origen">
            {% for zona in zonas %}
            <option value="{{ zona }}" {% if zona == origen_sel %}selected{% endif %}>{{ zona }}</option>
            {% endfor %}
          </select>
        </div>

        <div>
          <label>Destino</label>
          <select name="destino">
            {% for zona in zonas %}
            <option value="{{ zona }}" {% if zona == destino_sel %}selected{% endif %}>{{ zona }}</option>
            {% endfor %}
          </select>
        </div>

        <div>
          <label>Preferencia de Ruta</label>
          <select name="preferencia" onchange="aplicarPreferencia(this.value)">
            <option value="balanced" {% if preferencia == 'balanced' %}selected{% endif %}>Balanceado (α=0.5, β=0.5)</option>
            <option value="fast"     {% if preferencia == 'fast'     %}selected{% endif %}>Más Rápido (α=1.0, β=0.0)</option>
            <option value="safe"     {% if preferencia == 'safe'     %}selected{% endif %}>Más Seguro (α=0.0, β=1.0)</option>
          </select>
        </div>

        <div>
          <label>Alpha (Distancia)</label>
          <div class="slider-row">
            <span style="font-size:11px;color:#8c909f">Seguridad</span>
            <span class="slider-val cyan" id="alpha-val">{{ alpha }}</span>
          </div>
          <input type="range" name="alpha" id="alpha" min="0" max="1" step="0.1" value="{{ alpha }}"
            oninput="document.getElementById('alpha-val').textContent = parseFloat(this.value).toFixed(1)"/>
          <div style="display:flex;justify-content:space-between;margin-top:3px">
            <span style="font-size:10px;color:#424754">0</span>
            <span style="font-size:10px;color:#424754">1</span>
          </div>
        </div>

        <div>
          <label>Beta (Riesgo)</label>
          <div class="slider-row">
            <span style="font-size:11px;color:#8c909f">Sin peso</span>
            <span class="slider-val naranja" id="beta-val">{{ beta }}</span>
          </div>
          <input type="range" name="beta" id="beta" min="0" max="1" step="0.1" value="{{ beta }}"
            oninput="document.getElementById('beta-val').textContent = parseFloat(this.value).toFixed(1)"/>
          <div style="display:flex;justify-content:space-between;margin-top:3px">
            <span style="font-size:10px;color:#424754">0</span>
            <span style="font-size:10px;color:#424754">1</span>
          </div>
        </div>

        <div>
          <label>Modo de Cálculo</label>
          <select name="modo">
            <option value="ambos"    {% if modo == 'ambos'    %}selected{% endif %}>Ambos algoritmos</option>
            <option value="dijkstra" {% if modo == 'dijkstra' %}selected{% endif %}>Solo Dijkstra</option>
            <option value="bellman"  {% if modo == 'bellman'  %}selected{% endif %}>Solo Bellman-Ford</option>
          </select>
        </div>

        <div class="leyenda">
          <p>Leyenda</p>
          <div class="leyenda-item"><span class="dot" style="background:#4cd7f6"></span> Dijkstra</div>
          <div class="leyenda-item"><span class="dot" style="background:#ffb786"></span> Bellman-Ford</div>
        </div>

        <button type="submit" class="btn">
          <span class="material-symbols-outlined" style="font-size:18px">route</span>
          Calcular Rutas
        </button>

      </form>

      {% if error %}
      <p style="color:#ffb4ab;font-size:12px;text-align:center;margin-top:8px">⚠️ {{ error }}</p>
      {% endif %}

    </div>
  </nav>

  <main class="main">
    <div class="topbar">
      <h2>Analysis Hub <span>Medellín</span></h2>
      {% if calculado %}
      <span style="font-size:12px;color:#4cd7f6">✓ {{ origen_sel }} → {{ destino_sel }} — {{ preferencia_label }}</span>
      {% endif %}
    </div>

    <div class="content">

      <div class="map-container">
        {% if mapa_html %}
          <iframe srcdoc="{{ mapa_html | e }}" allowfullscreen></iframe>
        {% else %}
          <div class="map-placeholder">
            <span class="material-symbols-outlined" style="font-size:48px;color:#424754">map</span>
            <p>Seleccioná origen y destino para calcular la ruta</p>
          </div>
        {% endif %}
      </div>

      {% if calculado %}
      <div class="metricas">
        <div class="metrica-card">
          <div class="titulo">⏱ Tiempo de Ejecución</div>
          <div class="valores">
            <div class="fila"><span class="algo cyan">Dijkstra</span><span class="val cyan">{{ tiempo_dijk }} ms</span></div>
            <div class="fila"><span class="algo naranja">Bellman</span><span class="val naranja">{{ tiempo_bell }} ms</span></div>
          </div>
        </div>
        <div class="metrica-card">
          <div class="titulo">🔵 Nodos Explorados</div>
          <div class="valores">
            <div class="fila"><span class="algo cyan">Dijkstra</span><span class="val cyan">{{ nodos_dijk }}</span></div>
            <div class="fila"><span class="algo naranja">Bellman</span><span class="val naranja">{{ nodos_bell }}</span></div>
          </div>
        </div>
        <div class="metrica-card">
          <div class="titulo">💰 Costo Total</div>
          <div class="valores">
            <div class="fila"><span class="algo cyan">Dijkstra</span><span class="val cyan">{{ costo_dijk }}</span></div>
            <div class="fila"><span class="algo naranja">Bellman</span><span class="val naranja">{{ costo_bell }}</span></div>
          </div>
        </div>
        <div class="metrica-card">
          <div class="titulo">⚙️ Parámetros</div>
          <div class="valores">
            <div class="fila"><span class="algo" style="color:#8c909f">Alpha (α)</span><span class="val">{{ alpha }}</span></div>
            <div class="fila"><span class="algo" style="color:#8c909f">Beta (β)</span><span class="val">{{ beta }}</span></div>
          </div>
        </div>
      </div>

      <div class="tabla-section">
        <div class="tabla-header">↔ Comparación de Algoritmos</div>
        <table>
          <thead>
            <tr>
              <th>Algoritmo</th>
              <th>Tiempo</th>
              <th>Costo Total</th>
              <th>Nodos Explorados</th>
              <th>α / β</th>
              <th>Preferencia</th>
              <th>Eficiencia</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="cyan" style="font-weight:600">● Dijkstra</td>
              <td>{{ tiempo_dijk }} ms</td>
              <td>{{ costo_dijk }}</td>
              <td>{{ nodos_dijk }}</td>
              <td>{{ alpha }} / {{ beta }}</td>
              <td>{{ preferencia_label }}</td>
              <td>
                <div class="bar-wrap">
                  <div class="bar" style="background:#4cd7f6;width:{{ ef_dijk }}%"></div>
                </div>
              </td>
            </tr>
            <tr>
              <td class="naranja" style="font-weight:600">● Bellman-Ford</td>
              <td>{{ tiempo_bell }} ms</td>
              <td>{{ costo_bell }}</td>
              <td>{{ nodos_bell }}</td>
              <td>{{ alpha }} / {{ beta }}</td>
              <td>{{ preferencia_label }}</td>
              <td>
                <div class="bar-wrap">
                  <div class="bar" style="background:#ffb786;width:{{ ef_bell }}%"></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      {% endif %}

    </div>
  </main>
</div>

<script>
function aplicarPreferencia(val) {
    const alpha = document.getElementById('alpha');
    const beta  = document.getElementById('beta');
    if (val === 'fast')      { alpha.value = 1.0; beta.value = 0.0; }
    else if (val === 'safe') { alpha.value = 0.0; beta.value = 1.0; }
    else                     { alpha.value = 0.5; beta.value = 0.5; }
    document.getElementById('alpha-val').textContent = parseFloat(alpha.value).toFixed(1);
    document.getElementById('beta-val').textContent  = parseFloat(beta.value).toFixed(1);
}
</script>
</body>
</html>
"""

# ── Rutas Flask ───────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    zonas = list(ZONAS.keys())
    ctx = {
        "zonas":             zonas,
        "origen_sel":        zonas[0],
        "destino_sel":       zonas[1],
        "alpha":             0.5,
        "beta":              0.5,
        "modo":              "ambos",
        "preferencia":       "balanced",
        "preferencia_label": "Balanceado",
        "calculado":         False,
        "mapa_html":         None,
        "error":             None,
        "tiempo_dijk":       "—", "tiempo_bell": "—",
        "nodos_dijk":        "—", "nodos_bell":  "—",
        "costo_dijk":        "—", "costo_bell":  "—",
        "ef_dijk":           0,   "ef_bell":     0,
    }

    if request.method == "POST":
        origen_nombre  = request.form.get("origen")
        destino_nombre = request.form.get("destino")
        alpha       = float(request.form.get("alpha", 0.5))
        beta        = float(request.form.get("beta",  0.5))
        modo        = request.form.get("modo", "ambos")
        preferencia = request.form.get("preferencia", "balanced")

        ctx["origen_sel"]        = origen_nombre
        ctx["destino_sel"]       = destino_nombre
        ctx["alpha"]             = round(alpha, 1)
        ctx["beta"]              = round(beta,  1)
        ctx["modo"]              = modo
        ctx["preferencia"]       = preferencia
        ctx["preferencia_label"] = PREFERENCIA_LABELS.get(preferencia, "Balanceado")

        if origen_nombre == destino_nombre:
            ctx["error"] = "Origen y destino deben ser distintos"
            return render_template_string(TEMPLATE, **ctx)

        origen  = ZONAS[origen_nombre]
        destino = ZONAS[destino_nombre]

        # ── Dijkstra ──────────────────────────────────────────────────────────
        if modo in ("ambos", "dijkstra"):
            t0 = time.perf_counter()
            res_dijk = dijkstra.dijkstra(grafo, origen, destino, alpha, beta)
            t1 = time.perf_counter()
            tiempo_dijk  = round((t1 - t0) * 1000, 2)
            nodos_dijk   = len(res_dijk.get("visitados", set()))
            costo_dijk_v = res_dijk["costos"].get(destino, None)
            costo_dijk   = round(costo_dijk_v, 2) if costo_dijk_v and costo_dijk_v != float("inf") else "—"
        else:
            res_dijk    = {"ruta": [], "costos": {}}
            tiempo_dijk = "—"
            nodos_dijk  = 0
            costo_dijk  = "—"

        # ── Bellman-Ford ──────────────────────────────────────────────────────
        if modo in ("ambos", "bellman"):
            t0 = time.perf_counter()
            res_bell = bellman_ford.Bellman_Ford(grafo, origen, destino, alpha, beta)
            t1 = time.perf_counter()
            tiempo_bell  = round((t1 - t0) * 1000, 2)
            nodos_bell   = len([c for c in res_bell["costos"].values() if c < float("inf")])
            costo_bell_v = res_bell["costos"].get(destino, None)
            costo_bell   = round(costo_bell_v, 2) if costo_bell_v and costo_bell_v != float("inf") else "—"
        else:
            res_bell    = {"ruta": [], "costos": {}}
            tiempo_bell = "—"
            nodos_bell  = 0
            costo_bell  = "—"

        # ── Eficiencia relativa ───────────────────────────────────────────────
        max_nodos = max(nodos_dijk, nodos_bell) or 1
        ef_dijk = max(10, round((1 - nodos_dijk / max_nodos) * 90 + 10)) if nodos_dijk else 0
        ef_bell = max(10, round((1 - nodos_bell / max_nodos) * 90 + 10)) if nodos_bell else 0

        # ── Mapa Folium ───────────────────────────────────────────────────────
        mapa_html = generar_mapa(res_dijk, res_bell, origen)

        ctx.update({
            "calculado":   True,
            "mapa_html":   mapa_html,
            "tiempo_dijk": tiempo_dijk,
            "tiempo_bell": tiempo_bell,
            "nodos_dijk":  f"{nodos_dijk:,}" if isinstance(nodos_dijk, int) else nodos_dijk,
            "nodos_bell":  f"{nodos_bell:,}" if isinstance(nodos_bell, int) else nodos_bell,
            "costo_dijk":  costo_dijk,
            "costo_bell":  costo_bell,
            "ef_dijk":     ef_dijk,
            "ef_bell":     ef_bell,
        })

    return render_template_string(TEMPLATE, **ctx)


if __name__ == "__main__":
    app.run(debug=True)