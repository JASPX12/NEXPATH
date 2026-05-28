from graph.grafo import Grafo
import time
from datos.cargar_datos import save_data
from algoritmos import bellman_ford, dijkstra
from visualizacion.mapa import visualizar_ruta

def coord_a_tupla(coord_str):
    coord_str = coord_str.strip("()")
    lon, lat = coord_str.split(",")
    return (float(lon), float(lat))


def crear_grafo_con_datos(datos):
    grafo = Grafo()
    for _, dat in datos.iterrows():    
        fila = dat
        
        origen = coord_a_tupla(fila["origin"])
        destino = coord_a_tupla(fila["destination"])
        
        grafo.crear_interseccion(
            fila["name"],
            origen,
            destino,
            float(fila["length"]),
            bool(fila["oneway"]),
            float(fila["harassmentRisk"]),
            fila["geometry"]
        )
    
    return grafo


datos = save_data("datos\calles_de_medellin_con_acoso.csv")
g = crear_grafo_con_datos(datos)

inicio = (-75.598766, 6.2320727)
fin = (-75.5705202, 6.2106275)

inicio_dijkstra = time.time()
resultado_dijkstra = dijkstra.dijkstra(g, inicio, fin, alpha=1, beta=1)
print("Calculando la ruta óptima...")
#
fin_dijkstra = time.time()
print(f"tiempo de ejecucion dijkstra, {fin_dijkstra - inicio_dijkstra} segundos" )

#print("\nResultado de la búsqueda:")
#print(resultado_dijkstra)
#
#print("\nGenerando mapa en Folium...")
#visualizar_ruta(resultado_dijkstra, inicio, nombre_archivo="index.html")

inicio_bellman = time.time()
print("Calculando la ruta óptima...")
resultado_bellman_ford = bellman_ford.Bellman_Ford(g, inicio, fin, alpha=1, beta=1)
fin_bellman = time.time()
#print("\nResultado de la búsqueda:")
#print(resultado_bellman_ford)

print(f"tiempo de ejecucion bell, {fin_bellman - inicio_bellman} segundos" )


print("\nGenerando mapa en Folium...")
visualizar_ruta(resultado_bellman_ford, inicio, nombre_archivo="index.html")