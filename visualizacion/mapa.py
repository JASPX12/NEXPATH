import folium
from folium import plugins

def generar_mapa(res_dijkstra: dict, res_bellman: dict, origen: tuple) -> str:
    centro = [origen[1], origen[0]]
    m = folium.Map(location=centro, zoom_start=14, tiles="CartoDB dark_matter")

    ruta_dijk = [[c[1], c[0]] for c in res_dijkstra.get("ruta", []) if len(c) == 2]
    if ruta_dijk:
        plugins.AntPath(
            locations=ruta_dijk,
            color="#4cd7f6",
            weight=5,
            dash_array=[20, 10],
            delay=800,
            popup="Dijkstra"
        ).add_to(m)

    ruta_bell = [[c[1], c[0]] for c in res_bellman.get("ruta", []) if len(c) == 2]
    if ruta_bell:
        plugins.AntPath(
            locations=ruta_bell,
            color="#ffb786",
            weight=5,
            dash_array=[20, 10],
            delay=800,
            popup="Bellman-Ford"
        ).add_to(m)

    if ruta_dijk:
        folium.Marker(location=ruta_dijk[0], popup="Origen",
            icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(location=ruta_dijk[-1], popup="Destino",
            icon=folium.Icon(color="red", icon="stop")).add_to(m)
    if ruta_bell:
        folium.Marker(location=ruta_bell[0], popup="Origen",
            icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(location=ruta_bell[-1], popup="Destino",
            icon=folium.Icon(color="red", icon="stop")).add_to(m)

    if ruta_dijk or ruta_bell:
        m.fit_bounds(m.get_bounds())

    return m._repr_html_()