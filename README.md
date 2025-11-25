# Sistema de Rutas de Bolivia

Aplicación web Flask para calcular rutas óptimas entre departamentos de Bolivia usando el algoritmo de Dijkstra.

## Características

- Cálculo de rutas óptimas por distancia, tiempo o peaje
- Visualización interactiva del grafo de rutas
- API REST completa para gestión de ciudades y rutas
- Interfaz web responsive

## Despliegue en Render

### Opción 1: Usando render.yaml (Recomendado)

1. Sube tu código a GitHub
2. Ve a [Render Dashboard](https://dashboard.render.com/)
3. Click en "New +" → "Blueprint"
4. Conecta tu repositorio de GitHub
5. Render detectará automáticamente el archivo `render.yaml` y configurará todo

### Opción 2: Despliegue Manual

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Name**: grafo-bolivia (o el nombre que prefieras)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

5. Click en "Create Web Service"

## Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## API Endpoints

- `GET /` - Página principal
- `POST /ruta` - Calcular ruta óptima
- `GET /api/data` - Obtener datos del grafo
- `GET /api/ciudades` - Listar ciudades
- `POST /api/ciudades` - Agregar ciudad
- `DELETE /api/ciudades` - Eliminar ciudad
- `GET /api/rutas` - Listar rutas
- `POST /api/rutas` - Agregar ruta
- `DELETE /api/rutas` - Eliminar ruta
- `GET /api/estadisticas` - Estadísticas del grafo

## Tecnologías

- Flask 3.1.0
- Gunicorn 23.0.0
- Python 3.11
- Algoritmo de Dijkstra para cálculo de rutas óptimas
