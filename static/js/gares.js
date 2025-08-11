/**
 * Gestion des Gares - ONCF GIS
 * JavaScript pour la page de gestion des gares
 */

// Variables globales
let allGares = [];
let filteredGares = [];
let currentPage = 1;
let itemsPerPage = 25;
let gareFilters = {
    axes: [],
    types: [],
    etats: []
};
let selectedGare = null;
let isEditing = false;

// Configuration API
const API_BASE = '/api';

/**
 * Initialisation de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏢 Initialisation de la page des gares');
    
    // Charger les données initiales
    Promise.all([
        loadGares(),
        loadGareFilters(),
        loadStatistics()
    ]).then(() => {
        console.log('✅ Toutes les données des gares chargées');
        setupEventListeners();
        renderGares();
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
    document.getElementById('searchGares').addEventListener('input', debounce(applyFilters, 500));
    document.getElementById('filterAxe').addEventListener('change', applyFilters);
    document.getElementById('filterType').addEventListener('change', applyFilters);
    document.getElementById('filterEtat').addEventListener('change', applyFilters);
    document.getElementById('pageSize').addEventListener('change', changePageSize);
    
    // Actualisation automatique toutes les 10 minutes
    setInterval(refreshGares, 10 * 60 * 1000);
}

/**
 * Charger les gares depuis l'API
 */
async function loadGares(page = 1, filters = {}) {
    showLoading(true);
    
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: itemsPerPage,
            ...filters
        });
        
        const response = await fetch(`${API_BASE}/gares?${params}`);
        const data = await response.json();
        
        if (data.success) {
            allGares = data.data;
            filteredGares = [...allGares];
            
            // Mettre à jour la pagination
            if (data.pagination) {
                updatePagination(data.pagination);
            }
            
            console.log(`✅ ${allGares.length} gares chargées`);
            return data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('❌ Erreur chargement gares:', error);
        showNotification('Erreur lors du chargement des gares', 'error');
        return { data: [], pagination: { total: 0, pages: 0 } };
    } finally {
        showLoading(false);
    }
}

/**
 * Charger les options de filtrage pour les gares
 */
async function loadGareFilters() {
    try {
        const response = await fetch(`${API_BASE}/gares/filters`);
        const data = await response.json();
        
        if (data.success) {
            gareFilters = data.data;
            populateFilterOptions();
            console.log('✅ Options de filtrage chargées');
        }
    } catch (error) {
        console.error('❌ Erreur chargement filtres:', error);
    }
}

/**
 * Charger les statistiques
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/statistiques`);
        const data = await response.json();
        
        if (data.success && data.data.gares) {
            const stats = data.data.gares;
            
            document.getElementById('totalGaresCount').textContent = stats.total || 0;
            
            // Calculer les gares par état
            let activeCount = 0, passiveCount = 0;
            stats.par_type.forEach(item => {
                if (item.type && item.type.toLowerCase().includes('active')) {
                    activeCount += item.count;
                } else {
                    passiveCount += item.count;
                }
            });
            
            document.getElementById('activeGaresCount').textContent = activeCount;
            document.getElementById('passiveGaresCount').textContent = passiveCount;
            document.getElementById('filteredGaresCount').textContent = filteredGares.length;
            
            console.log('✅ Statistiques des gares chargées');
        }
    } catch (error) {
        console.error('❌ Erreur chargement statistiques:', error);
    }
}

/**
 * Peupler les options de filtrage
 */
function populateFilterOptions() {
    // Axes
    const axeSelect = document.getElementById('filterAxe');
    axeSelect.innerHTML = '<option value="">Tous les axes</option>';
    gareFilters.axes.forEach(axe => {
        const option = document.createElement('option');
        option.value = axe;
        option.textContent = axe;
        axeSelect.appendChild(option);
    });
    
    // Types
    const typeSelect = document.getElementById('filterType');
    typeSelect.innerHTML = '<option value="">Tous les types</option>';
    gareFilters.types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeSelect.appendChild(option);
    });
    
    // États
    const etatSelect = document.getElementById('filterEtat');
    etatSelect.innerHTML = '<option value="">Tous les états</option>';
    gareFilters.etats.forEach(etat => {
        const option = document.createElement('option');
        option.value = etat;
        option.textContent = etat;
        etatSelect.appendChild(option);
    });
}

/**
 * Appliquer les filtres
 */
async function applyFilters() {
    const search = document.getElementById('searchGares').value;
    const axe = document.getElementById('filterAxe').value;
    const type = document.getElementById('filterType').value;
    const etat = document.getElementById('filterEtat').value;
    
    const filters = {};
    if (search) filters.search = search;
    if (axe) filters.axe = axe;
    if (type) filters.type = type;
    if (etat) filters.etat = etat;
    
    currentPage = 1;
    await loadGares(currentPage, filters);
    renderGares();
    
    console.log(`🔍 Filtres appliqués: ${filteredGares.length} gares trouvées`);
}

/**
 * Réinitialiser les filtres
 */
function resetFilters() {
    document.getElementById('searchGares').value = '';
    document.getElementById('filterAxe').value = '';
    document.getElementById('filterType').value = '';
    document.getElementById('filterEtat').value = '';
    
    applyFilters();
    showNotification('Filtres réinitialisés', 'info');
}

/**
 * Afficher les gares
 */
function renderGares() {
    const tbody = document.getElementById('garesTableBody');
    tbody.innerHTML = '';
    
    if (filteredGares.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>Aucune gare trouvée</h4>
                    <p class="text-muted">Essayez de modifier vos filtres de recherche</p>
                </td>
            </tr>
        `;
        return;
    }
    
    filteredGares.forEach(gare => {
        const row = createGareRow(gare);
        tbody.appendChild(row);
    });
    
    updatePaginationInfo();
}

/**
 * Créer une ligne de gare
 */
function createGareRow(gare) {
    const row = document.createElement('tr');
    
    const statusClass = gare.etat === 'ACTIVE' ? 'active' : 'passive';
    const statusText = gare.etat === 'ACTIVE' ? 'Active' : 'Passive';
    
    row.innerHTML = `
        <td>
            <input type="checkbox" class="gare-checkbox" value="${gare.id}">
        </td>
        <td>
            <strong>${gare.nom || 'Sans nom'}</strong>
            <br><small class="text-muted">ID: ${gare.id}</small>
        </td>
        <td>${gare.code || 'N/A'}</td>
        <td>${gare.type || 'Non défini'}</td>
        <td>${gare.axe || 'Non défini'}</td>
        <td>${gare.ville || 'Non définie'}</td>
        <td>
            <span class="gare-status ${statusClass}"></span>
            ${statusText}
        </td>
        <td>
            <div class="action-buttons">
                <button class="btn btn-sm btn-outline-primary" onclick="showGareDetails(${gare.id})" title="Voir détails">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="editGare(${gare.id})" title="Modifier">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteGare(${gare.id})" title="Supprimer">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    
    return row;
}

/**
 * Afficher les détails d'une gare
 */
function showGareDetails(gareId) {
    const gare = allGares.find(g => g.id === gareId);
    if (!gare) return;
    
    selectedGare = gare;
    
    const content = document.getElementById('gareModalContent');
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Informations générales</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>ID:</strong></td>
                        <td>#${gare.id}</td>
                    </tr>
                    <tr>
                        <td><strong>Nom:</strong></td>
                        <td>${gare.nom || 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Code:</strong></td>
                        <td>${gare.code || 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Type:</strong></td>
                        <td>${gare.type || 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>État:</strong></td>
                        <td>
                            <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">
                                ${gare.etat === 'ACTIVE' ? 'Active' : 'Passive'}
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Localisation</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Axe:</strong></td>
                        <td>${gare.axe || 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Ville:</strong></td>
                        <td>${gare.ville || 'Non définie'}</td>
                    </tr>
                    <tr>
                        <td><strong>Code Opérationnel:</strong></td>
                        <td>${gare.codeoperationnel || 'Non défini'}</td>
                    </tr>
                    <tr>
                        <td><strong>Code Réseau:</strong></td>
                        <td>${gare.codereseau || 'Non défini'}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        ${gare.geometrie ? `
        <div class="mt-4">
            <h6>Coordonnées géographiques</h6>
            <div class="border rounded p-3 bg-light">
                <code>${gare.geometrie}</code>
            </div>
        </div>
        ` : ''}
    `;
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('gareDetailsModal'));
    modal.show();
}

/**
 * Ajouter une nouvelle gare
 */
function addNewGare() {
    isEditing = false;
    selectedGare = null;
    
    // Réinitialiser le formulaire
    document.getElementById('gareForm').reset();
    document.getElementById('gareFormTitle').innerHTML = '<i class="fas fa-plus me-2"></i>Nouvelle Gare';
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('gareFormModal'));
    modal.show();
}

/**
 * Modifier une gare
 */
function editGare(gareId) {
    const gare = allGares.find(g => g.id === gareId);
    if (!gare) return;
    
    isEditing = true;
    selectedGare = gare;
    
    // Remplir le formulaire
    document.getElementById('gareNom').value = gare.nom || '';
    document.getElementById('gareCode').value = gare.code || '';
    document.getElementById('gareType').value = gare.type || '';
    document.getElementById('gareAxe').value = gare.axe || '';
    document.getElementById('gareVille').value = gare.ville || '';
    document.getElementById('gareEtat').value = gare.etat || 'ACTIVE';
    document.getElementById('gareCodeOp').value = gare.codeoperationnel || '';
    document.getElementById('gareCodeReseau').value = gare.codereseau || '';
    
    document.getElementById('gareFormTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Modifier la Gare';
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('gareFormModal'));
    modal.show();
}

/**
 * Sauvegarder une gare (création ou modification)
 */
async function saveGare() {
    const form = document.getElementById('gareForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    showLoading(true);
    
    try {
        const gareData = {
            nom: document.getElementById('gareNom').value,
            code: document.getElementById('gareCode').value,
            type: document.getElementById('gareType').value,
            axe: document.getElementById('gareAxe').value,
            ville: document.getElementById('gareVille').value,
            etat: document.getElementById('gareEtat').value,
            codeoperationnel: document.getElementById('gareCodeOp').value,
            codereseau: document.getElementById('gareCodeReseau').value
        };
        
        const url = isEditing ? 
            `${API_BASE}/gares/${selectedGare.id}` : 
            `${API_BASE}/gares`;
        
        const method = isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(gareData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Fermer la modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('gareFormModal'));
            modal.hide();
            
            // Recharger les gares
            await loadGares();
            renderGares();
            
            showNotification(
                isEditing ? 'Gare modifiée avec succès' : 'Gare créée avec succès', 
                'success'
            );
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        showNotification('Erreur lors de la sauvegarde de la gare', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Supprimer une gare
 */
async function deleteGare(gareId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette gare ?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/gares/${gareId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Recharger les gares
            await loadGares();
            renderGares();
            
            showNotification('Gare supprimée avec succès', 'success');
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        showNotification('Erreur lors de la suppression de la gare', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Voir la gare sur la carte
 */
function showOnMap() {
    if (!selectedGare) return;
    
    // Rediriger vers la carte avec la gare sélectionnée
    window.location.href = `/carte?gare=${selectedGare.id}`;
}

/**
 * Exporter les gares
 */
function exportGares() {
    // Créer un fichier CSV avec les gares filtrées
    const headers = ['ID', 'Nom', 'Code', 'Type', 'Axe', 'Ville', 'État', 'Code Opérationnel', 'Code Réseau'];
    const csvContent = [
        headers.join(','),
        ...filteredGares.map(gare => [
            gare.id,
            `"${gare.nom || ''}"`,
            `"${gare.code || ''}"`,
            `"${gare.type || ''}"`,
            `"${gare.axe || ''}"`,
            `"${gare.ville || ''}"`,
            `"${gare.etat || ''}"`,
            `"${gare.codeoperationnel || ''}"`,
            `"${gare.codereseau || ''}"`
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `gares_oncf_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Export des gares terminé', 'success');
}

/**
 * Actualiser les gares
 */
async function refreshGares() {
    console.log('🔄 Actualisation des gares...');
    await Promise.all([
        loadGares(),
        loadGareFilters(),
        loadStatistics()
    ]);
    applyFilters();
    showNotification('Gares actualisées', 'success');
}

/**
 * Changer la taille de page
 */
function changePageSize() {
    itemsPerPage = parseInt(document.getElementById('pageSize').value);
    currentPage = 1;
    applyFilters();
}

/**
 * Mettre à jour la pagination
 */
function updatePagination(pagination) {
    const paginationElement = document.getElementById('pagination');
    
    if (pagination.pages <= 1) {
        paginationElement.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Bouton précédent
    html += `
        <li class="page-item ${pagination.page === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.page - 1}); return false;">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Numéros de pages
    const maxVisiblePages = 5;
    let startPage = Math.max(1, pagination.page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(pagination.pages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === pagination.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    html += `
        <li class="page-item ${pagination.page === pagination.pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.page + 1}); return false;">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationElement.innerHTML = html;
}

/**
 * Aller à une page spécifique
 */
async function goToPage(page) {
    currentPage = page;
    await loadGares(page);
    renderGares();
}

/**
 * Mettre à jour les informations de pagination
 */
function updatePaginationInfo() {
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredGares.length);
    
    document.getElementById('paginationInfo').textContent = 
        `Affichage ${startIndex}-${endIndex} de ${filteredGares.length} résultats`;
}

/**
 * Basculer la sélection de toutes les gares
 */
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const gareCheckboxes = document.querySelectorAll('.gare-checkbox');
    
    gareCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

/**
 * Trier le tableau
 */
function sortTable(columnIndex) {
    // Implémentation du tri (à développer selon les besoins)
    showNotification('Fonctionnalité de tri en développement', 'info');
}

/**
 * Afficher/masquer le loading
 */
function showLoading(show) {
    // Utiliser un indicateur de chargement global si disponible
    if (window.oncfGIS && window.oncfGIS.showLoading) {
        window.oncfGIS.showLoading(show);
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
window.showGareDetails = showGareDetails;
window.editGare = editGare;
window.deleteGare = deleteGare;
window.saveGare = saveGare;
window.addNewGare = addNewGare;
window.showOnMap = showOnMap;
window.exportGares = exportGares;
window.refreshGares = refreshGares;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.goToPage = goToPage;
window.changePageSize = changePageSize;
window.toggleSelectAll = toggleSelectAll;
window.sortTable = sortTable; 