from flask import Flask, render_template, request, jsonify
from grafo import Grafo

app = Flask(__name__)

# Inicializar grafo con datos de ejemplo
mapa = Grafo()

# Agregar departamentos de Bolivia
departamentos_bolivia = [
    "La Paz", "Cochabamba", "Santa Cruz", "Oruro", "Potosí", 
    "Chuquisaca", "Tarija", "Beni", "Pando"
]

for departamento in departamentos_bolivia:
    mapa.agregar_ciudad(departamento)

# Agregar rutas con parámetros realistas (distancia en km, tiempo en minutos, peaje en Bs)
# Eje Troncal (La Paz - Santa Cruz)
mapa.agregar_arista("La Paz", "Oruro", 230, 180, 10)
mapa.agregar_arista("Oruro", "Cochabamba", 204, 240, 15)
mapa.agregar_arista("Cochabamba", "Santa Cruz", 473, 420, 20)

# Ruta La Paz - Beni - Pando (Norte)
mapa.agregar_arista("La Paz", "Beni", 525, 480, 5)
mapa.agregar_arista("Beni", "Pando", 598, 720, 0)

# Ruta Santa Cruz - Beni
mapa.agregar_arista("Santa Cruz", "Beni", 502, 540, 10)

# Ruta Sur (Potosí - Chuquisaca - Tarija)
mapa.agregar_arista("Oruro", "Potosí", 237, 240, 8)
mapa.agregar_arista("Potosí", "Chuquisaca", 165, 180, 5)
mapa.agregar_arista("Chuquisaca", "Tarija", 250, 300, 12)

# Conexiones adicionales
mapa.agregar_arista("Cochabamba", "Chuquisaca", 410, 480, 15)
mapa.agregar_arista("Santa Cruz", "Tarija", 650, 720, 25)
mapa.agregar_arista("Cochabamba", "Beni", 560, 600, 8)

@app.route('/')
def index():
    ciudades = mapa.obtener_ciudades()
    return render_template('index.html', ciudades=ciudades)

@app.route('/ruta', methods=['POST'])
def calcular_ruta():
    try:
        origen = request.form.get('origen', '').strip()
        destino = request.form.get('destino', '').strip()
        criterio = request.form.get('criterio', 'distancia')
        
        if not origen or not destino:
            return render_template('resultado.html', 
                                 error="Debe seleccionar origen y destino",
                                 camino=[], costo_total=0, criterio=criterio,
                                 origen=origen, destino=destino)
        
        if origen == destino:
            return render_template('resultado.html',
                                 error="El origen y destino no pueden ser iguales",
                                 camino=[], costo_total=0, criterio=criterio,
                                 origen=origen, destino=destino)
        
        camino, costo_total = mapa.dijkstra(origen, destino, criterio)
        
        if not camino:
            return render_template('resultado.html',
                                 origen=origen,
                                 destino=destino,
                                 camino=[], costo_total=0, criterio=criterio,
                                 error=f"No existe ruta entre {origen} y {destino}")
        
        return render_template('resultado.html', 
                             origen=origen, 
                             destino=destino,
                             camino=camino, 
                             costo_total=costo_total,
                             criterio=criterio,
                             error=None)
    except Exception as e:
        return render_template('resultado.html', 
                             error=f"Error al calcular la ruta: {str(e)}",
                             camino=[], costo_total=0, criterio='distancia',
                             origen='', destino='')

@app.route('/api/data')
def api_data():
    """Retorna las aristas del grafo para visualización"""
    edges = []
    edges_agregados = set()
    
    for ciudad1, conexiones in mapa.adyacencia.items():
        for conexion in conexiones:
            ciudad2, distancia, tiempo, peaje = conexion
            distancia = int(distancia)
            tiempo = int(tiempo)
            peaje = int(peaje)
            
            edge_id = tuple(sorted([ciudad1, ciudad2]))
            
            if edge_id not in edges_agregados:
                edges_agregados.add(edge_id)
                edges.append({
                    "from": ciudad1, 
                    "to": ciudad2, 
                    "label": f"{distancia}km",
                    "distancia": distancia,
                    "tiempo": tiempo,
                    "peaje": peaje,
                    "id": f"{ciudad1}-{ciudad2}"
                })
    return jsonify(edges)

@app.route('/api/ciudades', methods=['GET', 'POST', 'DELETE'])
def gestionar_ciudades():
    """CRUD de ciudades"""
    if request.method == 'POST':
        try:
            data = request.json
            nombre = data.get('nombre', '').strip()
            
            if not nombre:
                return jsonify({"error": "El nombre de la ciudad es requerido"}), 400
            
            if nombre in mapa.obtener_ciudades():
                return jsonify({"error": "La ciudad ya existe"}), 400
            
            tipo = data.get('tipo', 'normal')
            mapa.agregar_ciudad(nombre, tipo)
            return jsonify({
                "mensaje": "Ciudad agregada correctamente",
                "ciudad": nombre,
                "total_ciudades": len(mapa.obtener_ciudades())
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.json
            nombre = data.get('nombre', '').strip()
            
            if not nombre:
                return jsonify({"error": "El nombre de la ciudad es requerido"}), 400
            
            if nombre not in mapa.obtener_ciudades():
                return jsonify({"error": "La ciudad no existe"}), 404
            
            # Contar conexiones antes de eliminar
            conexiones_eliminadas = len(mapa.adyacencia.get(nombre, []))
            
            mapa.eliminar_ciudad(nombre)
            return jsonify({
                "mensaje": f"Ciudad {nombre} eliminada correctamente",
                "conexiones_eliminadas": conexiones_eliminadas,
                "ciudades_restantes": len(mapa.obtener_ciudades())
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # GET - Retornar lista de ciudades con detalles
    try:
        ciudades_detalle = []
        for ciudad in mapa.obtener_ciudades():
            ciudades_detalle.append({
                "nombre": ciudad,
                "tipo": mapa.tipos_ciudad.get(ciudad, "normal"),
                "conexiones": len(mapa.adyacencia.get(ciudad, []))
            })
        
        return jsonify(ciudades_detalle)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rutas', methods=['GET', 'POST', 'DELETE'])
def gestionar_rutas():
    """CRUD de rutas/carreteras"""
    if request.method == 'GET':
        try:
            rutas = []
            rutas_agregadas = set()
            
            for ciudad1, conexiones in mapa.adyacencia.items():
                for conexion in conexiones:
                    ciudad2, distancia, tiempo, peaje = conexion
                    ruta_id = tuple(sorted([ciudad1, ciudad2]))
                    
                    if ruta_id not in rutas_agregadas:
                        rutas_agregadas.add(ruta_id)
                        rutas.append({
                            "origen": ciudad1,
                            "destino": ciudad2,
                            "distancia": int(distancia),
                            "tiempo": int(tiempo),
                            "peaje": int(peaje),
                            "costo_total": int(distancia) + int(tiempo) + int(peaje)
                        })
            
            return jsonify({
                "total_rutas": len(rutas),
                "rutas": sorted(rutas, key=lambda x: x['origen'])
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            origen = data.get('origen', '').strip()
            destino = data.get('destino', '').strip()
            
            if not origen or not destino:
                return jsonify({"error": "Se requiere origen y destino"}), 400
            
            if origen not in mapa.obtener_ciudades():
                return jsonify({"error": f"La ciudad {origen} no existe"}), 400
            
            if destino not in mapa.obtener_ciudades():
                return jsonify({"error": f"La ciudad {destino} no existe"}), 400
            
            if origen == destino:
                return jsonify({"error": "No se puede crear una ruta entre la misma ciudad"}), 400
            
            # Convertir a números
            try:
                distancia = int(data.get('distancia', 0))
                tiempo = int(data.get('tiempo', 0))
                peaje = int(data.get('peaje', 0))
            except (ValueError, TypeError):
                return jsonify({"error": "Los valores deben ser números válidos"}), 400
            
            # Verificar si la ruta ya existe
            ruta_existente = False
            for conexion in mapa.adyacencia.get(origen, []):
                if conexion[0] == destino:
                    ruta_existente = True
                    break
            
            if ruta_existente:
                return jsonify({"error": "Esta ruta ya existe"}), 400
            
            mapa.agregar_arista(origen, destino, distancia, tiempo, peaje)
            return jsonify({"mensaje": "Ruta agregada correctamente"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.json
            origen = data.get('origen', '').strip()
            destino = data.get('destino', '').strip()
            
            if not origen or not destino:
                return jsonify({"error": "Se requiere origen y destino"}), 400
            
            # Verificar que la ruta existe
            ruta_existe = False
            for conexion in mapa.adyacencia.get(origen, []):
                if conexion[0] == destino:
                    ruta_existe = True
                    break
            
            if not ruta_existe:
                return jsonify({"error": "La ruta no existe"}), 400
            
            mapa.eliminar_arista(origen, destino)
            return jsonify({"mensaje": "Ruta eliminada correctamente"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/ciudad/<nombre>')
def obtener_ciudad(nombre):
    if nombre in mapa.adyacencia:
        conexiones = []
        for conexion in mapa.adyacencia[nombre]:
            ciudad_destino, distancia, tiempo, peaje = conexion
            conexiones.append({
                'destino': ciudad_destino,
                'distancia': int(distancia),
                'tiempo': int(tiempo),
                'peaje': int(peaje)
            })
        
        return jsonify({
            "nombre": nombre,
            "tipo": mapa.tipos_ciudad.get(nombre, "normal"),
            "conexiones": len(mapa.adyacencia[nombre]),
            "rutas": conexiones
        })
    return jsonify({"error": "Ciudad no encontrada"}), 404

@app.route('/api/todas-rutas-posibles')
def todas_rutas_posibles():
    """Calcula todas las rutas posibles entre todos los pares de ciudades"""
    try:
        ciudades = mapa.obtener_ciudades()
        todas_las_rutas = []
        
        for origen in ciudades:
            for destino in ciudades:
                if origen != destino:
                    for criterio in ['distancia', 'tiempo', 'peaje']:
                        camino, costo = mapa.dijkstra(origen, destino, criterio)
                        
                        if camino:
                            todas_las_rutas.append({
                                "origen": origen,
                                "destino": destino,
                                "criterio": criterio,
                                "camino": camino,
                                "costo": costo,
                                "paradas": len(camino) - 2
                            })
        
        return jsonify({
            "total_rutas_calculadas": len(todas_las_rutas),
            "ciudades_totales": len(ciudades),
            "rutas_por_criterio": {
                "distancia": len([r for r in todas_las_rutas if r['criterio'] == 'distancia']),
                "tiempo": len([r for r in todas_las_rutas if r['criterio'] == 'tiempo']),
                "peaje": len([r for r in todas_las_rutas if r['criterio'] == 'peaje'])
            },
            "rutas": todas_las_rutas
        })
    except Exception as e:
        return jsonify({"error": f"Error al calcular rutas: {str(e)}"}), 500

@app.route('/api/eliminar-ciudad', methods=['POST'])
def eliminar_ciudad():
    """Elimina una ciudad y todas sus rutas conectadas"""
    try:
        data = request.json
        ciudad = data.get('nombre', '').strip()
        
        if not ciudad:
            return jsonify({"error": "Se requiere el nombre de la ciudad"}), 400
        
        if ciudad not in mapa.obtener_ciudades():
            return jsonify({"error": f"La ciudad {ciudad} no existe"}), 400
        
        conexiones_eliminadas = len(mapa.adyacencia.get(ciudad, []))
        mapa.eliminar_ciudad(ciudad)
        
        return jsonify({
            "mensaje": f"Ciudad {ciudad} eliminada correctamente",
            "conexiones_eliminadas": conexiones_eliminadas,
            "ciudades_restantes": len(mapa.obtener_ciudades())
        })
    except Exception as e:
        return jsonify({"error": f"Error al eliminar ciudad: {str(e)}"}), 500

@app.route('/api/eliminar-carretera', methods=['POST'])
def eliminar_carretera():
    """Elimina una carretera específica entre dos ciudades"""
    try:
        data = request.json
        origen = data.get('origen', '').strip()
        destino = data.get('destino', '').strip()
        
        if not origen or not destino:
            return jsonify({"error": "Se requieren origen y destino"}), 400
        
        ruta_existe = False
        info_carretera = None
        for conexion in mapa.adyacencia.get(origen, []):
            if conexion[0] == destino:
                ruta_existe = True
                info_carretera = {
                    "distancia": int(conexion[1]),
                    "tiempo": int(conexion[2]),
                    "peaje": int(conexion[3])
                }
                break
        
        if not ruta_existe:
            return jsonify({"error": f"No existe carretera entre {origen} y {destino}"}), 400
        
        mapa.eliminar_arista(origen, destino)
        
        return jsonify({
            "mensaje": f"Carretera entre {origen} y {destino} eliminada correctamente",
            "carretera_eliminada": info_carretera,
            "total_rutas_restantes": sum(len(conexiones) for conexiones in mapa.adyacencia.values()) // 2
        })
    except Exception as e:
        return jsonify({"error": f"Error al eliminar carretera: {str(e)}"}), 500

@app.route('/api/estadisticas')
def obtener_estadisticas():
    """Retorna estadísticas del grafo"""
    try:
        total_ciudades = len(mapa.adyacencia)
        total_rutas = sum(len(conexiones) for conexiones in mapa.adyacencia.values()) // 2
        
        distancias = []
        tiempos = []
        peajes = []
        
        for conexiones in mapa.adyacencia.values():
            for conexion in conexiones:
                _, dist, tiempo, peaje = conexion
                distancias.append(int(dist))
                tiempos.append(int(tiempo))
                peajes.append(int(peaje))
        
        return jsonify({
            "total_ciudades": total_ciudades,
            "total_rutas": total_rutas,
            "distancia_promedio": sum(distancias) // len(distancias) if distancias else 0,
            "tiempo_promedio": sum(tiempos) // len(tiempos) if tiempos else 0,
            "peaje_promedio": sum(peajes) // len(peajes) if peajes else 0,
            "ciudades": mapa.obtener_ciudades()
        })
    except Exception as e:
        return jsonify({"error": f"Error al calcular estadísticas: {str(e)}"}), 500

@app.route('/api/reset', methods=['POST'])
def reset_grafo():
    """Reinicia el grafo a su estado inicial"""
    try:
        mapa.adyacencia.clear()
        mapa.tipos_ciudad.clear()
        
        ciudades_iniciales = [
            "Santa Cruz", "Montero", "Cotoca", "Warnes", "Buena Vista", "San José"
        ]

        for ciudad in ciudades_iniciales:
            mapa.agregar_ciudad(ciudad)

        mapa.agregar_arista("Santa Cruz", "Montero", 50, 45, 5)
        mapa.agregar_arista("Santa Cruz", "Cotoca", 25, 30, 0)
        mapa.agregar_arista("Montero", "Warnes", 20, 25, 3)
        mapa.agregar_arista("Warnes", "Cotoca", 40, 50, 8)
        mapa.agregar_arista("Montero", "Buena Vista", 35, 40, 6)
        mapa.agregar_arista("Cotoca", "San José", 80, 90, 15)
        
        return jsonify({
            "mensaje": "Grafo reiniciado correctamente",
            "ciudades": len(ciudades_iniciales),
            "rutas": 6
        })
    except Exception as e:
        return jsonify({"error": f"Error al reiniciar: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)