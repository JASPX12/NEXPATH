import folium
from folium import plugins
from algoritmos import dijkstra, bellman_ford

def visualizar_ruta_dijkstra(dijkstra_res: dict, inicio: tuple, nombre_archivo="index.html"):
    
    centro_mapa = [inicio[1], inicio[0]]
    m = folium.Map(location=centro_mapa, zoom_start=14)

    ruta_original = dijkstra_res["ruta"]


    ruta_folium = [[coord[1], coord[0]] for coord in ruta_original]


    if ruta_folium:
        folium.Marker(
            location=ruta_folium[0],
            popup="Inicio de la ruta",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)
        
        folium.Marker(
            location=ruta_folium[-1],
            popup="Destino final",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

    plugins.AntPath(
        locations=ruta_folium,
        color = "blue", 
        dash_array = [50,10]
    ).add_to(m)

    m.fit_bounds(m.get_bounds())
    
    m.save(nombre_archivo)
    return m

def visualizar_ruta_bellman(bellman_res: dict, inicio: tuple, nombre_archivo="index.html"):
    
    centro_mapa = [inicio[1], inicio[0]]
    m = folium.Map(location=centro_mapa, zoom_start=14)

    ruta_original = bellman_res["ruta"]


    ruta_folium = [[coord[1], coord[0]] for coord in ruta_original]


    if ruta_folium:
        folium.Marker(
            location=ruta_folium[0],
            popup="Inicio de la ruta",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)
        
        folium.Marker(
            location=ruta_folium[-1],
            popup="Destino final",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

    plugins.AntPath(
        locations=ruta_folium,
        color = "blue", 
        dash_array = [50,10]
    ).add_to(m)

    m.fit_bounds(m.get_bounds())
    
    m.save(nombre_archivo)
    return m
