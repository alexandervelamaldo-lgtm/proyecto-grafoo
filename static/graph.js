let network = null;
let allNodes = null;
let allEdges = null;

// Iconos según tipo de ciudad
const iconos = {
    capital: '🏛️',
    normal: '🏘️',
    turistica: '🏕️',
    comercial: '🏬',
    industrial: '🏭'
};

function cargarGrafo() {
    fetch('/api/data')
        .then(res => res.json())
        .then(edges => {
            const nodes = new vis.DataSet([]);
            const edgesSet = new vis.DataSet([]);
            const nodeIds = new Set();

            // Procesar nodos
            edges.forEach(e => {
                if (!nodeIds.has(e.from)) {
                    nodes.add({
                        id: e.from,
                        label: `${iconos.normal} ${e.from}`,
                        title: e.from,
                        color: getColorPorTipo('normal'),
                        font: { color: 'white', size: 16 },
                        shape: 'circle',
                        size: 25
                    });
                    nodeIds.add(e.from);
                }
                if (!nodeIds.has(e.to)) {
                    nodes.add({
                        id: e.to,
                        label: `${iconos.normal} ${e.to}`,
                        title: e.to,
                        color: getColorPorTipo('normal'),
                        font: { color: 'white', size: 16 },
                        shape: 'circle',
                        size: 25
                    });
                    nodeIds.add(e.to);
                }

                // Agregar arista con información completa
                edgesSet.add({
                    id: `${e.from}-${e.to}`,
                    from: e.from,
                    to: e.to,
                    label: `📏 ${e.distancia}km\n⏱️ ${e.tiempo}min\n💰 ${e.peaje}bs`,
                    title: `Distancia: ${e.distancia}km\nTiempo: ${e.tiempo}min\nPeaje: ${e.peaje}bs`,
                    color: { color: '#7f8c8d', opacity: 0.7 },
                    width: 2,
                    font: { color: '#ecf0f1', size: 12, strokeWidth: 3, strokeColor: '#2c3e50' }
                });
            });

            allNodes = nodes;
            allEdges = edgesSet;

            // Crear red (Es el proceso de planificar, diseñar e implementar la estructura física )
            const container = document.getElementById("mynetwork");
            const data = { nodes, edges: edgesSet };
            const options = {
                nodes: {
                    shape: "dot",
                    size: 25,
                    font: {
                        size: 16,
                        color: "#ffffff",
                        strokeWidth: 3,
                        strokeColor: "rgba(0,0,0,0.8)"
                    },
                    borderWidth: 2,
                    shadow: true
                },
                edges: {
                    width: 2,
                    shadow: true,
                    smooth: {
                        type: "continuous",
                        roundness: 0.5
                    },
                    font: {
                        color: '#ecf0f1',
                        size: 12,
                        face: 'arial',
                        background: 'rgba(0,0,0,0.7)',
                        strokeWidth: 3
                    }
                },
                physics: {
                    enabled: true,
                    stabilization: { iterations: 100 },
                    barnesHut: {
                        gravitationalConstant: -8000,
                        springConstant: 0.04,
                        springLength: 95
                    }
                },
                interaction: {
                    dragNodes: true,
                    dragView: true,
                    zoomView: true,
                    hover: true,
                    tooltipDelay: 200
                }
            };

            network = new vis.Network(container, data, options);

            // Resaltar ruta si existe (usando las nuevas variables)
            // Verificar si las variables existen antes de usarlas
            if (typeof rutaCamino !== "undefined" && rutaCamino && rutaCamino.length > 0) {
                resaltarRuta(rutaCamino);
            }

            // Eventos de interacción
            network.on("selectNode", function(params) {
                console.log("Nodo seleccionado:", params.nodes[0]);
            });

            network.on("doubleClick", function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    mostrarInfoCiudad(nodeId);
                }
            });
        })
        .catch(error => console.error('Error cargando grafo:', error));
}

function getColorPorTipo(tipo) {
    const colores = {
        capital: { background: '#e74c3c', border: '#c0392b' },
        normal: { background: '#3498db', border: '#2980b9' },
        turistica: { background: '#2ecc71', border: '#27ae60' },
        comercial: { background: '#f39c12', border: '#d35400' },
        industrial: { background: '#9b59b6', border: '#8e44ad' }
    };
    return colores[tipo] || colores.normal;
}

function resaltarRuta(camino) {
    if (!allEdges || !network || !camino || camino.length === 0) return;

    // Resetear todos los edges
    const edgesToUpdate = [];
    allEdges.forEach(edge => {
        edgesToUpdate.push({
            id: edge.id,
            color: { color: '#7f8c8d', opacity: 0.7 },
            width: 2
        });
    });
    if (edgesToUpdate.length > 0) {
        allEdges.update(edgesToUpdate);
    }

    // Resaltar edges de la ruta
    const edgesToHighlight = [];
    for (let i = 0; i < camino.length - 1; i++) {
        const edgeId1 = `${camino[i]}-${camino[i+1]}`;
        const edgeId2 = `${camino[i+1]}-${camino[i]}`;
        
        if (allEdges.get(edgeId1)) {
            edgesToHighlight.push({
                id: edgeId1,
                color: { color: '#e94560', opacity: 1 },
                width: 5
            });
        } else if (allEdges.get(edgeId2)) {
            edgesToHighlight.push({
                id: edgeId2,
                color: { color: '#e94560', opacity: 1 },
                width: 5
            });
        }
    }
    
    if (edgesToHighlight.length > 0) {
        allEdges.update(edgesToHighlight);
    }

    // Resaltar nodos de la ruta
    const nodesToUpdate = [];
    allNodes.forEach(node => {
        const enRuta = camino.includes(node.id);
        nodesToUpdate.push({
            id: node.id,
            color: enRuta ? 
                { background: '#e94560', border: '#c0392b' } :
                getColorPorTipo('normal'),
            size: enRuta ? 30 : 25
        });
    });
    
    if (nodesToUpdate.length > 0) {
        allNodes.update(nodesToUpdate);
    }
}

function mostrarInfoCiudad(ciudad) {
    fetch(`/api/ciudad/${ciudad}`)
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                alert(`🏙️ ${data.nombre}\n📊 Tipo: ${data.tipo}\n🔗 Conexiones: ${data.conexiones}`);
            }
        })
        .catch(error => console.error('Error obteniendo info de ciudad:', error));
}

// Cargar grafo cuando la página esté lista
document.addEventListener('DOMContentLoaded', cargarGrafo);