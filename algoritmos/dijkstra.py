import heapq

def dijkstra(grafo, inicio, fin, alpha, beta):

    nodos = grafo.obtener_nodos()
    costos = {nodo: float("inf") for nodo in nodos}
    anteriores = {}
    visitados = set()
    costos[inicio] = 0

    heap = [(0, inicio)]  # (costo, nodo)

    while heap:
        costo_actual, nodo_actual = heapq.heappop(heap)
        
        if nodo_actual in visitados:
            continue

        visitados.add(nodo_actual)

        if nodo_actual == fin:
            break

        for arista in grafo.calles[nodo_actual]:

            vecino = arista["para"]
            nombre_calle = arista["nombre"]
            costo_arista = (alpha * float(arista["dist"])) + (beta * float(arista["peligro"]))
            nuevo_costo = costo_actual + costo_arista

            if nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                anteriores[vecino] = (nodo_actual, nombre_calle)
                heapq.heappush(heap, (nuevo_costo, vecino))

    ruta_coordenadas = []
    ruta_nombres = []
    nodo = fin

    if fin in anteriores or fin == inicio:
        while nodo in anteriores:
            ruta_coordenadas.append(nodo) 
            
            nodo_anterior, nombre_calle = anteriores[nodo]
            ruta_nombres.append(nombre_calle) 
            nodo = nodo_anterior
            
        ruta_coordenadas.append(inicio) 
        
        ruta_coordenadas.reverse()
        ruta_nombres.reverse()

    return {
        "ruta": ruta_coordenadas,      
        "nombre_calles": ruta_nombres,  
        "costos": costos,
        "visitados": visitados
    }