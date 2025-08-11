/**
 * Gestion des Incidents - ONCF GIS
 * JavaScript pour la page de gestion des incidents
 */

// Variables globales
let allIncidents = [];
let filteredIncidents = [];
let currentPage = 1;
let itemsPerPage = 50; // Augmenté de 12 à 50 pour afficher plus d'incidents
let incidentTypes = [];
let locations = [];
let selectedIncident = null;

// Configuration API
const API_BASE = '/api';

/**
 * Initialisation de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚨 Initialisation de la page des incidents');
    
    // Charger les données initiales
    Promise.all([
        loadIncidents(),
        loadIncidentTypes(),
        loadLocations(),
        loadStatistics()
    ]).then(() => {
        console.log('✅ Toutes les données des incidents chargées');
        setupEventListeners();
        renderIncidents();
    }).catch(error => {
        console.error('❌ Erreur lors du chargement des données:', error);
        showNotification('Erreur lors du chargement des données', 'error');
    });
});

/**
 * Configuration des écouteurs d'événements
 */
function setupEventListeners() {
    // Filtres en temps réel
    document.getElementById('statusFilter').addEventListener('change', applyFilters);
    document.getElementById('periodFilter').addEventListener('change', applyFilters);
    document.getElementById('searchFilter').addEventListener('input', debounce(applyFilters, 500));
    
    // Actualisation automatique toutes les 5 minutes
    setInterval(refreshIncidents, 5 * 60 * 1000);
}

/**
 * Charger les incidents depuis l'API
 */
async function loadIncidents(page = 1, filters = {}) {
    showLoading(true);
    
    try {
        // Charger tous les incidents en une seule requête
        const params = new URLSearchParams({
            per_page: 348, // Charger tous les 348 incidents
            ...filters
        });
        
        const response = await fetch(`${API_BASE}/evenements?${params}`);
        const data = await response.json();
        
        if (data.success) {
            allIncidents = data.data;
            filteredIncidents = [...allIncidents];
            
            // Calculer la pagination côté client
            const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
            const pagination = {
                total: filteredIncidents.length,
                pages: totalPages,
                page: currentPage,
                per_page: itemsPerPage
            };
            
            // Mettre à jour la pagination
            updatePagination(pagination);
            
            console.log(`✅ ${allIncidents.length} incidents chargés au total`);
            return data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('❌ Erreur chargement incidents:', error);
        showNotification('Erreur lors du chargement des incidents', 'error');
        return { data: [], pagination: { total: 0, pages: 0 } };
    } finally {
        showLoading(false);
    }
}

/**
 * Charger les types d'incidents
 */
async function loadIncidentTypes() {
    try {
        const response = await fetch(`${API_BASE}/types-incidents`);
        const data = await response.json();
        
        if (data.success) {
            incidentTypes = data.data;
            populateTypeFilters();
            populateTypeSelect();
            console.log(`✅ ${incidentTypes.length} types d'incidents chargés`);
        }
    } catch (error) {
        console.error('❌ Erreur chargement types:', error);
    }
}

/**
 * Charger les localisations
 */
async function loadLocations() {
    try {
        const response = await fetch(`${API_BASE}/localisations`);
        const data = await response.json();
        
        if (data.success) {
            locations = data.data;
            populateLocationSelect();
            console.log(`✅ ${locations.length} localisations chargées`);
        }
    } catch (error) {
        console.error('❌ Erreur chargement localisations:', error);
    }
}

/**
 * Charger les statistiques
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/statistiques`);
        const data = await response.json();
        
        if (data.success && data.data.evenements) {
            const stats = data.data.evenements;
            
            document.getElementById('totalIncidents').textContent = stats.total || 0;
            
            // Calculer les incidents par statut
            let openCount = 0, resolvedCount = 0;
            stats.par_statut.forEach(item => {
                if (item.statut && item.statut.toLowerCase().includes('ouvert')) {
                    openCount += item.count;
                } else if (item.statut && (item.statut.toLowerCase().includes('résolu') || item.statut.toLowerCase().includes('fermé'))) {
                    resolvedCount += item.count;
                }
            });
            
            document.getElementById('openIncidents').textContent = openCount;
            document.getElementById('resolvedIncidents').textContent = resolvedCount;
            document.getElementById('avgResolutionTime').textContent = '2.5h'; // Exemple
            
            console.log('✅ Statistiques des incidents chargées');
        }
    } catch (error) {
        console.error('❌ Erreur chargement statistiques:', error);
    }
}

/**
 * Peupler les filtres par type
 */
function populateTypeFilters() {
    const container = document.getElementById('typeFilters');
    container.innerHTML = '';
    
    incidentTypes.forEach(type => {
        const chip = document.createElement('div');
        chip.className = 'type-chip';
        chip.textContent = type.libelle;
        chip.dataset.typeId = type.id;
        chip.onclick = () => toggleTypeFilter(chip, type.id);
        container.appendChild(chip);
    });
}

/**
 * Peupler le select des types pour le nouveau formulaire
 */
function populateTypeSelect() {
    const select = document.getElementById('incidentType');
    select.innerHTML = '<option value="">Sélectionner un type</option>';
    
    incidentTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.libelle;
        select.appendChild(option);
    });
}

/**
 * Peupler le select des localisations
 */
function populateLocationSelect() {
    const select = document.getElementById('incidentLocation');
    select.innerHTML = '<option value="">Sélectionner une localisation</option>';
    
    locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.id;
        option.textContent = `${location.axe || ''} - ${location.description || location.gare || 'Sans nom'}`.trim();
        select.appendChild(option);
    });
}

/**
 * Basculer le filtre par type
 */
function toggleTypeFilter(chip, typeId) {
    chip.classList.toggle('active');
    applyFilters();
}

/**
 * Appliquer les filtres
 */
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const periodFilter = document.getElementById('periodFilter').value;
    const searchFilter = document.getElementById('searchFilter').value.toLowerCase();
    
    // Types sélectionnés
    const selectedTypes = Array.from(document.querySelectorAll('.type-chip.active'))
        .map(chip => parseInt(chip.dataset.typeId));
    
    filteredIncidents = allIncidents.filter(incident => {
        // Filtre par statut
        if (statusFilter && incident.statut !== statusFilter) {
            return false;
        }
        
        // Filtre par recherche
        if (searchFilter && incident.description && 
            !incident.description.toLowerCase().includes(searchFilter)) {
            return false;
        }
        
        // Filtre par type
        if (selectedTypes.length > 0 && !selectedTypes.includes(incident.type_id)) {
            return false;
        }
        
        // Filtre par période
        if (periodFilter && incident.date_debut) {
            const incidentDate = new Date(incident.date_debut);
            const now = new Date();
            
            switch (periodFilter) {
                case 'today':
                    if (incidentDate.toDateString() !== now.toDateString()) return false;
                    break;
                case 'week':
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    if (incidentDate < weekAgo) return false;
                    break;
                case 'month':
                    if (incidentDate.getMonth() !== now.getMonth() || 
                        incidentDate.getFullYear() !== now.getFullYear()) return false;
                    break;
                case 'year':
                    if (incidentDate.getFullYear() !== now.getFullYear()) return false;
                    break;
            }
        }
        
        return true;
    });
    
    currentPage = 1;
    renderIncidents();
    
    console.log(`🔍 Filtres appliqués: ${filteredIncidents.length} incidents trouvés`);
}

/**
 * Afficher les incidents
 */
function renderIncidents() {
    const container = document.getElementById('incidentsList');
    container.innerHTML = '';
    
    if (filteredIncidents.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>Aucun incident trouvé</h4>
                    <p class="text-muted">Essayez de modifier vos filtres de recherche</p>
                </div>
            </div>
        `;
        
        // Mettre à jour les informations de pagination
        updatePaginationInfo();
        return;
    }
    
    // Pagination côté client
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredIncidents.length);
    const pageIncidents = filteredIncidents.slice(startIndex, endIndex);
    
    pageIncidents.forEach(incident => {
        const card = createIncidentCard(incident);
        container.appendChild(card);
    });
    
    // Mettre à jour la pagination et les informations
    updateClientPagination();
    updatePaginationInfo();
}

/**
 * Créer une carte d'incident
 */
function createIncidentCard(incident) {
    const col = document.createElement('div');
    col.className = 'col-lg-4 col-md-6 mb-4';
    
    // Déterminer la classe de statut
    let statusClass = 'open';
    if (incident.statut) {
        const status = incident.statut.toLowerCase();
        if (status.includes('résolu') || status.includes('fermé')) {
            statusClass = 'resolved';
        } else if (status.includes('cours')) {
            statusClass = 'in-progress';
        }
    }
    
    // Trouver le type d'incident
    const type = incidentTypes.find(t => t.id === incident.type_id);
    const typeLabel = type ? type.libelle : 'Type inconnu';
    
    // Formatage des dates
    const dateDebut = incident.date_debut ? 
        new Date(incident.date_debut).toLocaleDateString('fr-FR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }) : 'Non définie';
    
    // Description tronquée
    const description = incident.description || 'Aucune description disponible';
    const shortDescription = description.length > 150 ? 
        description.substring(0, 150) + '...' : description;
    
    col.innerHTML = `
        <div class="card incident-card ${statusClass}" onclick="showIncidentDetails(${incident.id})">
            <div class="card-header d-flex justify-content-between align-items-center">
                <small class="text-muted">Incident #${incident.id}</small>
                <span class="badge status-badge bg-${getStatusColor(incident.statut)}">
                    ${incident.statut || 'Non défini'}
                </span>
            </div>
            <div class="card-body">
                <h6 class="card-title mb-2">
                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                    ${typeLabel}
                </h6>
                <p class="card-text incident-description">
                    ${shortDescription}
                </p>
                <div class="mt-3">
                    <small class="text-muted d-block">
                        <i class="fas fa-calendar me-1"></i>
                        ${dateDebut}
                    </small>
                    ${incident.heure_debut ? `
                        <small class="text-muted d-block">
                            <i class="fas fa-clock me-1"></i>
                            ${incident.heure_debut}
                        </small>
                    ` : ''}
                </div>
            </div>
            <div class="card-footer">
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        Localisation #${incident.localisation_id || 'N/A'}
                    </small>
                    <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showIncidentDetails(${incident.id})">
                        Détails
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

/**
 * Obtenir la couleur du badge de statut
 */
function getStatusColor(statut) {
    if (!statut) return 'secondary';
    
    const status = statut.toLowerCase();
    if (status.includes('ouvert')) return 'danger';
    if (status.includes('cours')) return 'warning';
    if (status.includes('résolu') || status.includes('fermé')) return 'success';
    return 'secondary';
}

/**
 * Afficher les détails d'un incident
 */
function showIncidentDetails(incidentId) {
    const incident = allIncidents.find(i => i.id === incidentId);
    if (!incident) return;
    
    selectedIncident = incident;
    const type = incidentTypes.find(t => t.id === incident.type_id);
    const location = locations.find(l => l.id === incident.localisation_id);
    
    const content = document.getElementById('incidentDetailsContent');
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Informations générales</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>ID:</strong></td>
                        <td>#${incident.id}</td>
                    </tr>
                    <tr>
                        <td><strong>Type:</strong></td>
                        <td>${type ? type.libelle : 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Statut:</strong></td>
                        <td>
                            <span class="badge bg-${getStatusColor(incident.statut)}">
                                ${incident.statut || 'Non défini'}
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Date début:</strong></td>
                        <td>${incident.date_debut ? new Date(incident.date_debut).toLocaleString('fr-FR') : 'Non définie'}</td>
                    </tr>
                    <tr>
                        <td><strong>Date fin:</strong></td>
                        <td>${incident.date_fin ? new Date(incident.date_fin).toLocaleString('fr-FR') : 'En cours'}</td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Localisation</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Axe:</strong></td>
                        <td>${location ? location.axe || 'Non défini' : 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Section:</strong></td>
                        <td>${location ? location.section || 'Non définie' : 'Non définie'}</td>
                    </tr>
                    <tr>
                        <td><strong>Gare:</strong></td>
                        <td>${location ? location.gare || 'Non définie' : 'Non définie'}</td>
                    </tr>
                    <tr>
                        <td><strong>PK:</strong></td>
                        <td>${location && location.pk_debut ? `${location.pk_debut} - ${location.pk_fin || location.pk_debut}` : 'Non défini'}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="mt-4">
            <h6>Description complète</h6>
            <div class="border rounded p-3 bg-light">
                ${incident.description || 'Aucune description disponible'}
            </div>
        </div>
        
        <div class="mt-4">
            <h6>Chronologie</h6>
            <div class="timeline-item">
                <strong>Création:</strong> ${incident.date_debut ? new Date(incident.date_debut).toLocaleString('fr-FR') : 'Non définie'}
                <br><small class="text-muted">Incident signalé</small>
            </div>
            ${incident.date_fin ? `
                <div class="timeline-item">
                    <strong>Résolution:</strong> ${new Date(incident.date_fin).toLocaleString('fr-FR')}
                    <br><small class="text-muted">Incident résolu</small>
                </div>
            ` : ''}
        </div>
    `;
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('incidentDetailsModal'));
    modal.show();
}

/**
 * Mettre à jour la pagination côté client
 */
function updateClientPagination() {
    const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
    const pagination = document.getElementById('paginationControls');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    // Calculer les indices de début et fin pour la page courante
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredIncidents.length);
    
    let html = '';
    
    // Informations sur la pagination
    html += `
        <li class="page-item disabled">
            <span class="page-link">
                Affichage ${startIndex}-${endIndex} sur ${filteredIncidents.length} incidents
            </span>
        </li>
    `;
    
    // Bouton précédent
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage - 1}); return false;">
                <i class="fas fa-chevron-left"></i> Précédent
            </a>
        </li>
    `;
    
    // Numéros de pages avec logique intelligente
    const maxVisiblePages = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Ajuster si on est près de la fin
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Première page
    if (startPage > 1) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(1); return false;">1</a>
            </li>
        `;
        if (startPage > 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Pages visibles
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Dernière page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${totalPages}); return false;">${totalPages}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage + 1}); return false;">
                Suivant <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

/**
 * Aller à une page spécifique
 */
function goToPage(page) {
    const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderIncidents();
}

/**
 * Changer le nombre d'éléments par page
 */
function changeItemsPerPage() {
    const newItemsPerPage = parseInt(document.getElementById('itemsPerPageSelect').value);
    itemsPerPage = newItemsPerPage;
    currentPage = 1; // Retour à la première page
    renderIncidents();
    showNotification(`Affichage de ${newItemsPerPage} incidents par page`, 'info');
}

/**
 * Mettre à jour les informations de pagination
 */
function updatePaginationInfo() {
    const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredIncidents.length);
    
    // Mettre à jour l'information principale
    const paginationInfo = document.getElementById('paginationInfo');
    if (paginationInfo) {
        paginationInfo.textContent = `Affichage des incidents ${startIndex} à ${endIndex} sur ${filteredIncidents.length} au total`;
    }
    
    // Mettre à jour les statistiques
    const paginationStats = document.getElementById('paginationStats');
    if (paginationStats) {
        paginationStats.textContent = `Page ${currentPage} sur ${totalPages} | ${itemsPerPage} par page`;
    }
}

/**
 * Actualiser les incidents
 */
async function refreshIncidents() {
    console.log('🔄 Actualisation des incidents...');
    await Promise.all([
        loadIncidents(),
        loadStatistics()
    ]);
    applyFilters();
    showNotification('Incidents actualisés', 'success');
}

/**
 * Enregistrer un nouvel incident
 */
async function saveNewIncident() {
    const form = document.getElementById('newIncidentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    showLoading(true);
    
    try {
        const incidentData = {
            type_id: parseInt(document.getElementById('incidentType').value),
            localisation_id: parseInt(document.getElementById('incidentLocation').value),
            date_debut: document.getElementById('incidentDateDebut').value,
            date_fin: document.getElementById('incidentDateFin').value || null,
            description: document.getElementById('incidentDescription').value,
            statut: document.getElementById('incidentStatut').value
        };
        
        const response = await fetch(`${API_BASE}/evenements`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(incidentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Fermer la modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newIncidentModal'));
            modal.hide();
            
            // Réinitialiser le formulaire
            form.reset();
            
            // Recharger les incidents
            await loadIncidents();
            applyFilters();
            
            showNotification('Incident créé avec succès', 'success');
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la création:', error);
        showNotification('Erreur lors de la création de l\'incident', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Modifier un incident
 */
function editIncident() {
    if (!selectedIncident) return;
    
    // Remplir le formulaire avec les données de l'incident sélectionné
    document.getElementById('incidentType').value = selectedIncident.type_id || '';
    document.getElementById('incidentLocation').value = selectedIncident.localisation_id || '';
    document.getElementById('incidentDateDebut').value = selectedIncident.date_debut ? 
        selectedIncident.date_debut.replace(' ', 'T') : '';
    document.getElementById('incidentDateFin').value = selectedIncident.date_fin ? 
        selectedIncident.date_fin.replace(' ', 'T') : '';
    document.getElementById('incidentDescription').value = selectedIncident.description || '';
    document.getElementById('incidentStatut').value = selectedIncident.statut || 'Ouvert';
    
    // Changer le titre de la modal
    document.querySelector('#newIncidentModal .modal-title').textContent = 'Modifier l\'Incident';
    
    // Changer le bouton de sauvegarde
    const saveButton = document.querySelector('#newIncidentModal .btn-primary');
    saveButton.textContent = 'Modifier';
    saveButton.onclick = updateIncident;
    
    // Fermer la modal de détails et ouvrir la modal de modification
    const detailsModal = bootstrap.Modal.getInstance(document.getElementById('incidentDetailsModal'));
    detailsModal.hide();
    
    const editModal = new bootstrap.Modal(document.getElementById('newIncidentModal'));
    editModal.show();
}

/**
 * Mettre à jour un incident existant
 */
async function updateIncident() {
    if (!selectedIncident) return;
    
    const form = document.getElementById('newIncidentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    showLoading(true);
    
    try {
        const incidentData = {
            type_id: parseInt(document.getElementById('incidentType').value),
            localisation_id: parseInt(document.getElementById('incidentLocation').value),
            date_debut: document.getElementById('incidentDateDebut').value,
            date_fin: document.getElementById('incidentDateFin').value || null,
            resume: document.getElementById('incidentDescription').value,
            etat: document.getElementById('incidentStatut').value
        };
        
        const response = await fetch(`${API_BASE}/evenements/${selectedIncident.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(incidentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Fermer la modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newIncidentModal'));
            modal.hide();
            
            // Réinitialiser le formulaire et le titre
            form.reset();
            document.querySelector('#newIncidentModal .modal-title').textContent = 'Nouveau Incident';
            
            // Restaurer le bouton de sauvegarde
            const saveButton = document.querySelector('#newIncidentModal .btn-primary');
            saveButton.textContent = 'Enregistrer';
            saveButton.onclick = saveNewIncident;
            
            // Recharger les incidents
            await loadIncidents();
            applyFilters();
            
            showNotification('Incident modifié avec succès', 'success');
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la modification:', error);
        showNotification('Erreur lors de la modification de l\'incident', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Mettre à jour la pagination (API)
 */
function updatePagination(pagination) {
    // Cette fonction est appelée pour la pagination côté serveur
    // Pour l'instant, nous utilisons la pagination côté client
}

/**
 * Afficher/masquer le loading
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    // Utiliser le système de notifications global si disponible
    if (window.oncfGIS && window.oncfGIS.showNotification) {
        window.oncfGIS.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

/**
 * Fonction debounce pour optimiser les recherches
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Fonctions globales pour les événements onclick
window.showIncidentDetails = showIncidentDetails;
window.goToPage = goToPage;
window.refreshIncidents = refreshIncidents;
window.applyFilters = applyFilters;
window.saveNewIncident = saveNewIncident;
window.editIncident = editIncident;
window.updateIncident = updateIncident;