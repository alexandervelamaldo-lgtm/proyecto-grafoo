from collections import defaultdict
import heapq

class Grafo:
    def __init__(self):
        self.adyacencia = defaultdict(list)
        self.tipos_ciudad = {}  # Almacena el tipo de cada ciudad

    def agregar_arista(self, ciudad1, ciudad2, distancia, tiempo=0, peaje=0):
        """
        Agrega una arista entre dos ciudades con múltiples costos
        """
        self.adyacencia[ciudad1].append((ciudad2, distancia, tiempo, peaje))
        self.adyacencia[ciudad2].append((ciudad1, distancia, tiempo, peaje))
        
        # Asegurar que las ciudades existan en tipos_ciudad
        if ciudad1 not in self.tipos_ciudad:
            self.tipos_ciudad[ciudad1] = "normal"
        if ciudad2 not in self.tipos_ciudad:
            self.tipos_ciudad[ciudad2] = "normal"

    def agregar_ciudad(self, nombre, tipo="normal"):
        """Agrega una nueva ciudad al grafo"""
        self.tipos_ciudad[nombre] = tipo
        if nombre not in self.adyacencia:
            self.adyacencia[nombre] = []

    def eliminar_ciudad(self, ciudad):
        """Elimina una ciudad y todas sus conexiones"""
        if ciudad in self.adyacencia:
            # Eliminar todas las conexiones de esta ciudad
            for conexion in self.adyacencia[ciudad]:
                ciudad_conectada = conexion[0]
                self.adyacencia[ciudad_conectada] = [
                    c for c in self.adyacencia[ciudad_conectada] 
                    if c[0] != ciudad
                ]
            del self.adyacencia[ciudad]
            if ciudad in self.tipos_ciudad:
                del self.tipos_ciudad[ciudad]

    def eliminar_arista(self, ciudad1, ciudad2):
        """Elimina la conexión entre dos ciudades"""
        if ciudad1 in self.adyacencia:
            self.adyacencia[ciudad1] = [
                c for c in self.adyacencia[ciudad1] if c[0] != ciudad2
            ]
        if ciudad2 in self.adyacencia:
            self.adyacencia[ciudad2] = [
                c for c in self.adyacencia[ciudad2] if c[0] != ciudad1
            ]

    def obtener_ciudades(self):
        """Retorna lista de todas las ciudades"""
        return list(self.adyacencia.keys())

    def obtener_ciudades_detalladas(self):
        """Retorna información detallada de las ciudades"""
        return [
            {"nombre": ciudad, "tipo": self.tipos_ciudad.get(ciudad, "normal")}
            for ciudad in self.obtener_ciudades()
        ]

    def dijkstra(self, inicio, destino, criterio='distancia'):
        """
        Algoritmo de Dijkstra para encontrar la ruta más corta
        """
        if inicio not in self.adyacencia or destino not in self.adyacencia:
            return [], float('inf')
            
        if inicio == destino:
            return [inicio], 0
            
        # Índices según el criterio (1: distancia, 2: tiempo, 3: peaje)
        indices = {'distancia': 1, 'tiempo': 2, 'peaje': 3}
        idx = indices.get(criterio, 1)
        
        # Inicializar distancias
        dist = {nodo: float('inf') for nodo in self.adyacencia}
        dist[inicio] = 0
        prev = {inicio: None}
        pq = [(0, inicio)]  # Cola de prioridad

        while pq:
            costo_actual, nodo_actual = heapq.heappop(pq)
            
            # Si encontramos una distancia mayor, saltar
            if costo_actual > dist[nodo_actual]:
                continue
                
            if nodo_actual == destino:
                break
                
            # Explorar vecinos
            for conexion in self.adyacencia[nodo_actual]:
                vecino = conexion[0]
                costos = conexion[1:]  # (distancia, tiempo, peaje)
                
                # Asegurar que los costos son números
                try:
                    costo_arista = float(costos[idx-1])
                except (ValueError, TypeError, IndexError):
                    costo_arista = float('inf')
                    
                nuevo_costo = costo_actual + costo_arista
                
                if nuevo_costo < dist[vecino]:
                    dist[vecino] = nuevo_costo
                    prev[vecino] = nodo_actual
                    heapq.heappush(pq, (nuevo_costo, vecino))

        # Reconstruir camino si existe
        if dist[destino] == float('inf'):
            return [], float('inf')

        camino = []
        nodo = destino
        while nodo is not None:
            camino.insert(0, nodo)
            nodo = prev.get(nodo)
            
        return camino, dist[destino]

    def obtener_info_arista(self, ciudad1, ciudad2):
        """Obtiene información de una arista específica"""
        for conexion in self.adyacencia[ciudad1]:
            if conexion[0] == ciudad2:
                return {
                    'distancia': conexion[1],
                    'tiempo': conexion[2],
                    'peaje': conexion[3]
                }
        return None