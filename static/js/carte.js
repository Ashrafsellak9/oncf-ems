// ONCF GIS - Carte Interactive

let map;
let garesLayer;
let arcsLayer;
let incidentsLayer;
let selectedGare = null;

// Variables de pagination pour les incidents
let currentIncidentPage = 1;
let totalIncidentPages = 1;
let incidentsPerPage = 50;
let allIncidents = [];
let currentIncidents = [];

// Configuration de la carte
const MAP_CONFIG = {
    center: [31.7917, -7.0926], // Centre du Maroc
    zoom: 6,
    minZoom: 5,
    maxZoom: 18
};

// Initialisation de la carte
function initONCFMap() {
    // Créer la carte
    map = L.map('map', {
        center: MAP_CONFIG.center,
        zoom: MAP_CONFIG.zoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom
    });

    // Ajouter les tuiles de base (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Créer les couches
    garesLayer = L.layerGroup().addTo(map);
    arcsLayer = L.layerGroup().addTo(map);
    incidentsLayer = L.layerGroup().addTo(map);

    // Charger les données
    loadMapData();
    
    // Initialiser les contrôles
    initializeMapControls();
    
    // Ajouter les événements de la carte
    setupMapEvents();
}

// Charger les données de la carte
function loadMapData() {
    // Charger toutes les gares pour la carte
    fetch('/api/gares?all=true')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addGaresToMap(data.data);
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des gares:', error);
            showNotification('Erreur lors du chargement des gares', 'error');
        });

    // Charger les arcs
    fetch('/api/arcs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addArcsToMap(data.data);
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des arcs:', error);
            showNotification('Erreur lors du chargement des voies', 'error');
        });
        
    // Charger tous les incidents
    loadAllIncidents();
}

// Ajouter les gares à la carte
function addGaresToMap(gares) {
    garesLayer.clearLayers();
    
    gares.forEach(gare => {
        const coords = parseGeometry(gare.geometrie);
        if (coords) {
            const marker = createGareMarker(gare, coords);
            garesLayer.addLayer(marker);
        }
    });
    
    updateMapStats();
}

// Créer un marqueur pour une gare
function createGareMarker(gare, coords) {
    // Définir l'icône selon le type de gare
    const iconColor = getGareIconColor(gare.type);
    const iconSize = getGareIconSize(gare.type);
    
    const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            width: ${iconSize}px; 
            height: ${iconSize}px; 
            background-color: ${iconColor}; 
            border: 2px solid white; 
            border-radius: 50%; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: ${iconSize * 0.6}px;
        "><i class="fas fa-train"></i></div>`,
        iconSize: [iconSize, iconSize],
        iconAnchor: [iconSize/2, iconSize/2]
    });

    const marker = L.marker(coords, { icon: icon });
    
    // Ajouter le popup
    const popupContent = createGarePopup(gare);
    marker.bindPopup(popupContent);
    
    // Ajouter l'événement de clic
    marker.on('click', () => {
        selectedGare = gare;
        showGareInfo(gare);
    });
    
    return marker;
}

// Obtenir la couleur de l'icône selon le type de gare
function getGareIconColor(type) {
    switch(type?.toUpperCase()) {
        case 'PRINCIPALE':
        case 'MAJOR':
            return '#dc3545'; // Rouge pour les gares principales
        case 'SECONDAIRE':
        case 'MINOR':
            return '#198754'; // Vert pour les gares secondaires
        default:
            return '#0d6efd'; // Bleu par défaut
    }
}

// Obtenir la taille de l'icône selon le type de gare
function getGareIconSize(type) {
    switch(type?.toUpperCase()) {
        case 'PRINCIPALE':
        case 'MAJOR':
            return 20; // Plus grand pour les gares principales
        case 'SECONDAIRE':
        case 'MINOR':
            return 16; // Moyen pour les gares secondaires
        default:
            return 14; // Petit par défaut
    }
}

// Créer le contenu du popup pour une gare
function createGarePopup(gare) {
    return `
        <div class="gare-popup">
            <h6>${gare.nom || 'Gare sans nom'}</h6>
            <div class="mb-2">
                <span class="badge bg-primary">${gare.code || 'N/A'}</span>
                <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">${gare.etat || 'N/A'}</span>
            </div>
            <div class="small">
                <div><strong>Type:</strong> ${gare.type || 'N/A'}</div>
                <div><strong>Axe:</strong> ${gare.axe || 'N/A'}</div>
                <div><strong>Ville:</strong> ${gare.ville || 'N/A'}</div>
            </div>
            <button class="btn btn-sm btn-primary mt-2" onclick="showGareDetails(${gare.id})">
                <i class="fas fa-info-circle me-1"></i>Détails
            </button>
        </div>
    `;
}

// Ajouter les arcs à la carte
function addArcsToMap(arcs) {
    arcsLayer.clearLayers();
    
    arcs.forEach(arc => {
        const coords = parseArcGeometry(arc.geometrie);
        if (coords && coords.length >= 2) {
            const polyline = createArcPolyline(arc, coords);
            arcsLayer.addLayer(polyline);
        }
    });
    
    updateMapStats();
}

// Parser la géométrie d'un arc (LINESTRING)
function parseArcGeometry(geometryString) {
    if (!geometryString) return null;
    
    try {
        const match = geometryString.match(/LINESTRING\(([^)]+)\)/);
        if (match) {
            const coords = match[1].split(',').map(coord => {
                const [lng, lat] = coord.trim().split(' ').map(Number);
                return [lat, lng]; // [lat, lng] pour Leaflet
            });
            return coords;
        }
    } catch (error) {
        console.error('Erreur lors du parsing de la géométrie d\'arc:', error);
    }
    
    return null;
}

// Créer une polyligne pour un arc
function createArcPolyline(arc, coords) {
    const color = getArcColor(arc.axe);
    const weight = getArcWeight(arc.axe);
    
    const polyline = L.polyline(coords, {
        color: color,
        weight: weight,
        opacity: 0.8
    });
    
    // Ajouter le popup
    const popupContent = createArcPopup(arc);
    polyline.bindPopup(popupContent);
    
    // Ajouter l'événement de clic
    polyline.on('click', () => {
        showArcInfo(arc);
    });
    
    return polyline;
}

// Obtenir la couleur d'un arc selon l'axe
function getArcColor(axe) {
    const colors = {
        'CASABLANCA': '#dc3545',
        'RABAT': '#198754',
        'FES': '#ffc107',
        'MARRAKECH': '#fd7e14',
        'TANGER': '#6f42c1',
        'AGADIR': '#20c997'
    };
    
    return colors[axe?.toUpperCase()] || '#0d6efd';
}

// Obtenir l'épaisseur d'un arc selon l'axe
function getArcWeight(axe) {
    const weights = {
        'CASABLANCA': 4,
        'RABAT': 4,
        'FES': 3,
        'MARRAKECH': 3,
        'TANGER': 3,
        'AGADIR': 2
    };
    
    return weights[axe?.toUpperCase()] || 2;
}

// Créer le contenu du popup pour un arc
function createArcPopup(arc) {
    return `
        <div class="arc-popup">
            <h6>Section de Voie</h6>
            <div class="info-row">
                <span class="info-label">Axe:</span>
                <span class="info-value">${arc.axe || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Point de départ:</span>
                <span class="info-value">${arc.plod || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Point d'arrivée:</span>
                <span class="info-value">${arc.plof || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Cumul départ:</span>
                <span class="info-value">${arc.cumuld || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Cumul arrivée:</span>
                <span class="info-value">${arc.cumulf || 'N/A'}</span>
            </div>
        </div>
    `;
}

// Ajouter les incidents à la carte
function addIncidentsToMap(incidents) {
    incidentsLayer.clearLayers();
    
    incidents.forEach(incident => {
        // Créer un marqueur pour l'incident
        const marker = createIncidentMarker(incident);
        if (marker) {
            incidentsLayer.addLayer(marker);
        }
    });
    
    updateMapStats();
}

// Créer un marqueur pour un incident
function createIncidentMarker(incident) {
    // Utiliser les vraies coordonnées de l'incident si disponibles
    let coords = [31.7917, -7.0926]; // Centre du Maroc par défaut
    
    if (incident.geometrie) {
        const parsedCoords = parseGeometry(incident.geometrie);
        if (parsedCoords) {
            coords = parsedCoords;
        }
    }
    
    const icon = L.divIcon({
        className: 'incident-marker',
        html: `<div style="
            width: 16px; 
            height: 16px; 
            background-color: #dc3545; 
            border: 2px solid white; 
            border-radius: 50%; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
        "><i class="fas fa-exclamation-triangle"></i></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    const marker = L.marker(coords, { icon: icon });
    
    // Ajouter le popup
    const popupContent = createIncidentPopup(incident);
    marker.bindPopup(popupContent);
    
    return marker;
}

// Créer le contenu du popup pour un incident
function createIncidentPopup(incident) {
    const date = incident.date_debut ? new Date(incident.date_debut).toLocaleDateString('fr-FR') : 'N/A';
    const heure = incident.heure_debut || 'N/A';
    
    // Informations de localisation
    let locationInfo = '';
    if (incident.location_name) {
        locationInfo = `<div><strong>Localisation:</strong> ${incident.location_name}</div>`;
    } else if (incident.gare_debut_id || incident.gare_fin_id) {
        const gares = [];
        if (incident.gare_debut_id) gares.push(incident.gare_debut_id);
        if (incident.gare_fin_id) gares.push(incident.gare_fin_id);
        locationInfo = `<div><strong>Gares concernées:</strong> ${gares.join(' - ')}</div>`;
    }
    
    // Informations de PK si disponibles
    let pkInfo = '';
    if (incident.pk_debut || incident.pk_fin) {
        pkInfo = `<div><strong>PK:</strong> ${incident.pk_debut || 'N/A'} - ${incident.pk_fin || 'N/A'}</div>`;
    }
    
    return `
        <div class="incident-popup">
            <h6><i class="fas fa-exclamation-triangle text-danger"></i> Incident #${incident.id}</h6>
            <div class="mb-2">
                <span class="badge bg-danger">${incident.statut || 'Ouvert'}</span>
                <span class="badge bg-secondary">${date}</span>
            </div>
            <div class="small">
                <div><strong>Heure:</strong> ${heure}</div>
                ${locationInfo}
                ${pkInfo}
                <div><strong>Description:</strong> ${incident.description || 'Aucune description'}</div>
            </div>
            <button class="btn btn-sm btn-outline-danger mt-2" onclick="showIncidentDetails(${incident.id})">
                <i class="fas fa-info-circle me-1"></i>Détails
            </button>
        </div>
    `;
}

// Initialiser les contrôles de la carte
function initializeMapControls() {
    // Remplir les filtres
    populateFilters();
    
    // Ajouter les événements aux contrôles
    document.getElementById('layerSelect').addEventListener('change', filterLayers);
    document.getElementById('axeFilter').addEventListener('change', filterByAxe);
    document.getElementById('typeFilter').addEventListener('change', filterByType);
}

// Remplir les filtres avec les données
function populateFilters() {
    // Charger les axes uniques
    fetch('/api/statistiques')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const axeSelect = document.getElementById('axeFilter');
                const typeSelect = document.getElementById('typeFilter');
                
                // Remplir le filtre des axes
                data.data.gares.par_axe.forEach(axe => {
                    if (axe.axe) {
                        const option = document.createElement('option');
                        option.value = axe.axe;
                        option.textContent = axe.axe;
                        axeSelect.appendChild(option);
                    }
                });
                
                // Remplir le filtre des types
                data.data.gares.par_type.forEach(type => {
                    if (type.type) {
                        const option = document.createElement('option');
                        option.value = type.type;
                        option.textContent = type.type;
                        typeSelect.appendChild(option);
                    }
                });
            }
        });
}

// Filtrer les couches
function filterLayers() {
    const layerValue = document.getElementById('layerSelect').value;
    
    // Retirer toutes les couches d'abord
    map.removeLayer(garesLayer);
    map.removeLayer(arcsLayer);
    map.removeLayer(incidentsLayer);
    
    if (layerValue === 'gares') {
        map.addLayer(garesLayer);
    } else if (layerValue === 'arcs') {
        map.addLayer(arcsLayer);
    } else if (layerValue === 'incidents') {
        map.addLayer(incidentsLayer);
    } else {
        // 'all' - afficher toutes les couches
        map.addLayer(garesLayer);
        map.addLayer(arcsLayer);
        map.addLayer(incidentsLayer);
    }
}

// Filtrer par axe
function filterByAxe() {
    const axeValue = document.getElementById('axeFilter').value;
    // Implémenter le filtrage par axe
    console.log('Filtrer par axe:', axeValue);
}

// Filtrer par type
function filterByType() {
    const typeValue = document.getElementById('typeFilter').value;
    // Implémenter le filtrage par type
    console.log('Filtrer par type:', typeValue);
}

// Réinitialiser la carte
function resetMap() {
    // Réinitialiser les filtres
    document.getElementById('layerSelect').value = 'all';
    document.getElementById('axeFilter').value = '';
    document.getElementById('typeFilter').value = '';
    
    // Afficher toutes les couches
    map.addLayer(garesLayer);
    map.addLayer(arcsLayer);
    map.addLayer(incidentsLayer);
    
    // Réinitialiser la pagination des incidents
    if (allIncidents.length > 0) {
        currentIncidentPage = 1;
        showIncidentsPage(1);
    }
    
    // Centrer la carte
    map.setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
    
    // Masquer le panneau d'info
    document.getElementById('infoPanel').style.display = 'none';
    
    // Mettre à jour les statistiques
    updateMapStats();
}

// Mettre à jour les statistiques de la carte
function updateMapStats() {
    const garesCount = garesLayer.getLayers().length;
    const arcsCount = arcsLayer.getLayers().length;
    const incidentsCount = incidentsLayer.getLayers().length;
    
    document.getElementById('mapGaresCount').textContent = garesCount;
    document.getElementById('mapArcsCount').textContent = arcsCount;
    document.getElementById('mapIncidentsCount').textContent = incidentsCount;
}

// Afficher les informations d'une gare
function showGareInfo(gare) {
    const infoPanel = document.getElementById('infoPanel');
    const infoContent = document.getElementById('infoContent');
    
    infoContent.innerHTML = `
        <h6 class="text-primary">${gare.nom || 'Gare sans nom'}</h6>
        <div class="mb-2">
            <span class="badge bg-primary">${gare.code || 'N/A'}</span>
            <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">${gare.etat || 'N/A'}</span>
        </div>
        <div class="small">
            <div><strong>Type:</strong> ${gare.type || 'N/A'}</div>
            <div><strong>Axe:</strong> ${gare.axe || 'N/A'}</div>
            <div><strong>Ville:</strong> ${gare.ville || 'N/A'}</div>
            <div><strong>Code opérationnel:</strong> ${gare.codeoperationnel || 'N/A'}</div>
        </div>
        <button class="btn btn-sm btn-primary mt-2" onclick="showGareDetails(${gare.id})">
            <i class="fas fa-info-circle me-1"></i>Voir détails
        </button>
    `;
    
    infoPanel.style.display = 'block';
}

// Afficher les informations d'un arc
function showArcInfo(arc) {
    const infoPanel = document.getElementById('infoPanel');
    const infoContent = document.getElementById('infoContent');
    
    infoContent.innerHTML = `
        <h6 class="text-success">Section de Voie</h6>
        <div class="small">
            <div><strong>Axe:</strong> ${arc.axe || 'N/A'}</div>
            <div><strong>Point de départ:</strong> ${arc.plod || 'N/A'}</div>
            <div><strong>Point d'arrivée:</strong> ${arc.plof || 'N/A'}</div>
            <div><strong>Cumul départ:</strong> ${arc.cumuld || 'N/A'}</div>
            <div><strong>Cumul arrivée:</strong> ${arc.cumulf || 'N/A'}</div>
        </div>
    `;
    
    infoPanel.style.display = 'block';
}

// Configurer les événements de la carte
function setupMapEvents() {
    // Événement de clic sur la carte pour masquer le panneau d'info
    map.on('click', () => {
        document.getElementById('infoPanel').style.display = 'none';
    });
    
    // Événement de zoom pour ajuster la taille des marqueurs
    map.on('zoomend', () => {
        const zoom = map.getZoom();
        // Ajuster la taille des marqueurs selon le zoom
        console.log('Nouveau zoom:', zoom);
    });
}

// Fonction globale pour centrer sur une gare
function centerOnGare() {
    if (selectedGare) {
        const coords = parseGeometry(selectedGare.geometrie);
        if (coords) {
            map.setView(coords, 15);
        }
    }
}

// Parser la géométrie (POINT)
function parseGeometry(geometryString) {
    if (!geometryString) return null;
    
    try {
        // Essayer d'abord le format WKT (Well-Known Text)
        const wktMatch = geometryString.match(/POINT\(([^)]+)\)/);
        if (wktMatch) {
            const coords = wktMatch[1].split(' ').map(Number);
            return [coords[1], coords[0]]; // [lat, lng] pour Leaflet
        }
        
        // Si c'est du WKB (Well-Known Binary), on ne peut pas le parser côté client
        // On va utiliser des coordonnées par défaut pour le Maroc
        if (geometryString.startsWith('0101000020')) {
            console.warn('Géométrie WKB détectée, utilisation de coordonnées par défaut');
            // Coordonnées par défaut au centre du Maroc
            return [31.7917, -7.0926];
        }
        
    } catch (error) {
        console.error('Erreur lors du parsing de la géométrie:', error);
    }
    
    return null;
}

// Afficher une notification
function showNotification(message, type = 'info') {
    if (window.oncfGIS && window.oncfGIS.showNotification) {
        window.oncfGIS.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Fonctions de pagination pour les incidents
function loadAllIncidents() {
    fetch('/api/evenements?per_page=348')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allIncidents = data.data;
                totalIncidentPages = Math.ceil(allIncidents.length / incidentsPerPage);
                currentIncidentPage = 1;
                
                console.log(`✅ ${allIncidents.length} incidents chargés au total`);
                showIncidentsPage(1);
                updateIncidentPaginationInfo();
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des incidents:', error);
            showNotification('Erreur lors du chargement des incidents', 'error');
        });
}

function showIncidentsPage(page) {
    const startIndex = (page - 1) * incidentsPerPage;
    const endIndex = startIndex + incidentsPerPage;
    currentIncidents = allIncidents.slice(startIndex, endIndex);
    
    // Effacer les incidents existants et ajouter les nouveaux
    incidentsLayer.clearLayers();
    addIncidentsToMap(currentIncidents);
    
    // Mettre à jour les contrôles de pagination
    updateIncidentPaginationControls();
    updateMapStats();
}

function updateIncidentPaginationInfo() {
    const infoElement = document.getElementById('incidentPaginationInfo');
    const pageInfoElement = document.getElementById('incidentPageInfo');
    
    if (infoElement && pageInfoElement) {
        infoElement.textContent = `Affichage des incidents ${(currentIncidentPage - 1) * incidentsPerPage + 1} à ${Math.min(currentIncidentPage * incidentsPerPage, allIncidents.length)} sur ${allIncidents.length} au total`;
        pageInfoElement.textContent = `Page ${currentIncidentPage} sur ${totalIncidentPages}`;
    }
}

function updateIncidentPaginationControls() {
    const prevButton = document.getElementById('prevIncidents');
    const nextButton = document.getElementById('nextIncidents');
    const paginationDiv = document.getElementById('incidentPagination');
    
    if (prevButton && nextButton && paginationDiv) {
        prevButton.disabled = currentIncidentPage <= 1;
        nextButton.disabled = currentIncidentPage >= totalIncidentPages;
        
        // Afficher les contrôles de pagination seulement s'il y a plus d'une page
        paginationDiv.style.display = totalIncidentPages > 1 ? 'block' : 'none';
        
        updateIncidentPaginationInfo();
    }
}

function loadNextIncidents() {
    if (currentIncidentPage < totalIncidentPages) {
        currentIncidentPage++;
        showIncidentsPage(currentIncidentPage);
    }
}

function loadPreviousIncidents() {
    if (currentIncidentPage > 1) {
        currentIncidentPage--;
        showIncidentsPage(currentIncidentPage);
    }
}

// Initialiser la carte quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    if (typeof L !== 'undefined') {
        initONCFMap();
    } else {
        console.error('Leaflet n\'est pas chargé');
    }
}); 