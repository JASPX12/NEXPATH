from graph.grafo import Grafo

def Bellman_Ford(grafo: Grafo, origen: str, destino:str, alpha: float, beta: float ):
    nodos = list(grafo.obtener_nodos())
    costos = {nodo: float('inf') for nodo in nodos}
    anteriores = {}
    costos[origen] = 0



    n = len(nodos)

    for _ in range(n - 1):
        hubo_mejora = False
        for nodo_acutal in nodos: 
            if nodo_acutal not in grafo.calles: #grafo.calles es un dict
                continue

            for arista in grafo.calles[nodo_acutal]:
                vecino = arista["para"]
                costo_arista = alpha * float(arista["dist"]) + beta * float(arista["peligro"])
                nuevo_costo = costos[nodo_acutal] + costo_arista
                
                if nuevo_costo < costos[vecino]:
                    costos[vecino] = nuevo_costo
                    anteriores[vecino] = (nodo_acutal, arista["nombre"])
                    hubo_mejora = True

        if not hubo_mejora: 
            break

    ciclo_negativo = False
    for nodo_actual in nodos:
        if nodo_actual not in grafo.calles:
            continue

        for arista in grafo.calles[nodo_actual]:
            vecino = arista["para"]
            costo_arista = alpha * float(arista["dist"]) + beta * float(arista["peligro"])
            if costos[nodo_actual] + costo_arista < costos[vecino]:
                ciclo_negativo = True
                break

    if ciclo_negativo:
        return {"error": "Ciclo negativo detectado", "algoritmo": "Bellman-Ford"}
    
    ruta_coordenadas = []
    ruta_nombres = []
    nodo = destino
    
    if destino in anteriores or destino == origen:
        while nodo in anteriores:
            ruta_coordenadas.append(nodo)
            nodo_anterior, nombre_calle = anteriores[nodo]
            ruta_nombres.append(nombre_calle)
            nodo = nodo_anterior
        
        ruta_coordenadas.append(origen)
        ruta_coordenadas.reverse()
        ruta_nombres.reverse()
    
    return {
        "ruta": ruta_coordenadas,
        "nombre_calles": ruta_nombres,
        "costos": costos,
        "algoritmo": "Bellman-Ford"
    }