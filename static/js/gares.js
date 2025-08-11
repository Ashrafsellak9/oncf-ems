// ONCF GIS - Gestion des Gares

// Variables globales
let allGares = [];
let filteredGares = [];
let currentPage = 1;
let pageSize = 25;
let currentSortColumn = 0;
let currentSortDirection = 'asc';
let selectedGare = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    loadGares();
    setupEventListeners();
    populateFilters();
});

// Configuration des événements
function setupEventListeners() {
    // Recherche en temps réel
    document.getElementById('searchGares').addEventListener('input', debounce(applyFilters, 300));
    
    // Changement de taille de page
    document.getElementById('pageSize').addEventListener('change', function() {
        pageSize = parseInt(this.value);
        currentPage = 1;
        renderGaresTable();
    });
    
    // Filtres
    document.getElementById('filterAxe').addEventListener('change', applyFilters);
    document.getElementById('filterType').addEventListener('change', applyFilters);
    document.getElementById('filterEtat').addEventListener('change', applyFilters);
}

// Charger les gares
function loadGares() {
    fetch('/api/gares')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allGares = data.data;
                filteredGares = [...allGares];
                updateStatistics();
                renderGaresTable();
                populateFilters();
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des gares:', error);
            showNotification('Erreur lors du chargement des gares', 'error');
        });
}

// Remplir les filtres
function populateFilters() {
    const axes = [...new Set(allGares.map(gare => gare.axe).filter(Boolean))];
    const types = [...new Set(allGares.map(gare => gare.type).filter(Boolean))];
    
    // Remplir le filtre des axes
    const axeSelect = document.getElementById('filterAxe');
    axeSelect.innerHTML = '<option value="">Tous les axes</option>';
    axes.forEach(axe => {
        const option = document.createElement('option');
        option.value = axe;
        option.textContent = axe;
        axeSelect.appendChild(option);
    });
    
    // Remplir le filtre des types
    const typeSelect = document.getElementById('filterType');
    typeSelect.innerHTML = '<option value="">Tous les types</option>';
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeSelect.appendChild(option);
    });
}

// Appliquer les filtres
function applyFilters() {
    const searchTerm = document.getElementById('searchGares').value.toLowerCase();
    const axeFilter = document.getElementById('filterAxe').value;
    const typeFilter = document.getElementById('filterType').value;
    const etatFilter = document.getElementById('filterEtat').value;
    
    filteredGares = allGares.filter(gare => {
        // Filtre de recherche
        const matchesSearch = !searchTerm || 
            (gare.nom && gare.nom.toLowerCase().includes(searchTerm)) ||
            (gare.code && gare.code.toLowerCase().includes(searchTerm)) ||
            (gare.ville && gare.ville.toLowerCase().includes(searchTerm));
        
        // Filtre par axe
        const matchesAxe = !axeFilter || gare.axe === axeFilter;
        
        // Filtre par type
        const matchesType = !typeFilter || gare.type === typeFilter;
        
        // Filtre par état
        const matchesEtat = !etatFilter || gare.etat === etatFilter;
        
        return matchesSearch && matchesAxe && matchesType && matchesEtat;
    });
    
    currentPage = 1;
    updateStatistics();
    renderGaresTable();
}

// Réinitialiser les filtres
function resetFilters() {
    document.getElementById('searchGares').value = '';
    document.getElementById('filterAxe').value = '';
    document.getElementById('filterType').value = '';
    document.getElementById('filterEtat').value = '';
    
    filteredGares = [...allGares];
    currentPage = 1;
    updateStatistics();
    renderGaresTable();
}

// Mettre à jour les statistiques
function updateStatistics() {
    const total = allGares.length;
    const active = allGares.filter(gare => gare.etat === 'ACTIVE').length;
    const passive = allGares.filter(gare => gare.etat === 'PASSIVE').length;
    const filtered = filteredGares.length;
    
    document.getElementById('totalGaresCount').textContent = total;
    document.getElementById('activeGaresCount').textContent = active;
    document.getElementById('passiveGaresCount').textContent = passive;
    document.getElementById('filteredGaresCount').textContent = filtered;
}

// Rendre le tableau des gares
function renderGaresTable() {
    const tableBody = document.getElementById('garesTableBody');
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const pageGares = filteredGares.slice(startIndex, endIndex);
    
    if (pageGares.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    <i class="fas fa-search me-2"></i>
                    Aucune gare trouvée
                </td>
            </tr>
        `;
    } else {
        tableBody.innerHTML = '';
        pageGares.forEach(gare => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="gare-checkbox" value="${gare.id}" onchange="updateSelectAll()">
                </td>
                <td><strong>${gare.nom || 'N/A'}</strong></td>
                <td><code>${gare.code || 'N/A'}</code></td>
                <td>${gare.type || 'N/A'}</td>
                <td>${gare.axe || 'N/A'}</td>
                <td>${gare.ville || 'N/A'}</td>
                <td>
                    <span class="gare-status ${gare.etat === 'ACTIVE' ? 'active' : 'passive'}"></span>
                    <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">
                        ${gare.etat || 'N/A'}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" onclick="showGareDetails(${gare.id})" title="Voir détails">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="editGare(${gare.id})" title="Modifier">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="showOnMap(${gare.id})" title="Voir sur la carte">
                            <i class="fas fa-map-marker-alt"></i>
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    renderPagination();
    updatePaginationInfo();
}

// Rendre la pagination
function renderPagination() {
    const totalPages = Math.ceil(filteredGares.length / pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Bouton précédent
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Pages
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(1)">1</a>
            </li>
        `;
        if (startPage > 2) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${totalPages})">${totalPages}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
}

// Aller à une page
function goToPage(page) {
    const totalPages = Math.ceil(filteredGares.length / pageSize);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderGaresTable();
    }
}

// Mettre à jour les informations de pagination
function updatePaginationInfo() {
    const startIndex = (currentPage - 1) * pageSize + 1;
    const endIndex = Math.min(currentPage * pageSize, filteredGares.length);
    const total = filteredGares.length;
    
    document.getElementById('paginationInfo').textContent = 
        `Affichage ${startIndex}-${endIndex} de ${total} résultats`;
}

// Trier le tableau
function sortTable(columnIndex) {
    if (currentSortColumn === columnIndex) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = columnIndex;
        currentSortDirection = 'asc';
    }
    
    const columnNames = ['nom', 'code', 'type', 'axe', 'ville', 'etat'];
    const columnName = columnNames[columnIndex - 1];
    
    filteredGares.sort((a, b) => {
        let aValue = a[columnName] || '';
        let bValue = b[columnName] || '';
        
        if (typeof aValue === 'string') aValue = aValue.toLowerCase();
        if (typeof bValue === 'string') bValue = bValue.toLowerCase();
        
        if (aValue < bValue) return currentSortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
    
    renderGaresTable();
}

// Sélectionner/désélectionner tout
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.gare-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
}

// Mettre à jour la case "sélectionner tout"
function updateSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.gare-checkbox');
    const checkedBoxes = document.querySelectorAll('.gare-checkbox:checked');
    
    selectAll.checked = checkedBoxes.length === checkboxes.length && checkboxes.length > 0;
    selectAll.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < checkboxes.length;
}

// Afficher les détails d'une gare
function showGareDetails(gareId) {
    const gare = allGares.find(g => g.id === gareId);
    if (!gare) return;
    
    selectedGare = gare;
    
    const modalContent = document.getElementById('gareModalContent');
    modalContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-primary">Informations Générales</h6>
                <table class="table table-sm">
                    <tr><td><strong>Nom:</strong></td><td>${gare.nom || 'N/A'}</td></tr>
                    <tr><td><strong>Code:</strong></td><td><code>${gare.code || 'N/A'}</code></td></tr>
                    <tr><td><strong>Type:</strong></td><td>${gare.type || 'N/A'}</td></tr>
                    <tr><td><strong>Axe:</strong></td><td>${gare.axe || 'N/A'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-success">Informations Techniques</h6>
                <table class="table table-sm">
                    <tr><td><strong>État:</strong></td><td>
                        <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">
                            ${gare.etat || 'N/A'}
                        </span>
                    </td></tr>
                    <tr><td><strong>Ville:</strong></td><td>${gare.ville || 'N/A'}</td></tr>
                    <tr><td><strong>Code Opérationnel:</strong></td><td>${gare.codeoperationnel || 'N/A'}</td></tr>
                    <tr><td><strong>Code Réseau:</strong></td><td>${gare.codereseau || 'N/A'}</td></tr>
                </table>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-info">Informations Supplémentaires</h6>
                <table class="table table-sm">
                    <tr><td><strong>Publish ID:</strong></td><td>${gare.publishid || 'N/A'}</td></tr>
                    <tr><td><strong>SIV Type:</strong></td><td>${gare.sivtypegare || 'N/A'}</td></tr>
                    <tr><td><strong>Num PK:</strong></td><td>${gare.num_pk || 'N/A'}</td></tr>
                    <tr><td><strong>ID Ville:</strong></td><td>${gare.idville || 'N/A'}</td></tr>
                </table>
            </div>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('gareDetailsModal'));
    modal.show();
}

// Éditer une gare
function editGare(gareId) {
    const gare = allGares.find(g => g.id === gareId);
    if (!gare) return;
    
    selectedGare = gare;
    fillGareForm(gare);
    
    document.getElementById('gareFormTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Modifier la Gare';
    
    const modal = new bootstrap.Modal(document.getElementById('gareFormModal'));
    modal.show();
}

// Ajouter une nouvelle gare
function addNewGare() {
    selectedGare = null;
    clearGareForm();
    
    document.getElementById('gareFormTitle').innerHTML = '<i class="fas fa-plus me-2"></i>Nouvelle Gare';
    
    const modal = new bootstrap.Modal(document.getElementById('gareFormModal'));
    modal.show();
}

// Remplir le formulaire avec les données d'une gare
function fillGareForm(gare) {
    document.getElementById('gareNom').value = gare.nom || '';
    document.getElementById('gareCode').value = gare.code || '';
    document.getElementById('gareType').value = gare.type || '';
    document.getElementById('gareAxe').value = gare.axe || '';
    document.getElementById('gareVille').value = gare.ville || '';
    document.getElementById('gareEtat').value = gare.etat || 'ACTIVE';
    document.getElementById('gareCodeOp').value = gare.codeoperationnel || '';
    document.getElementById('gareCodeReseau').value = gare.codereseau || '';
    document.getElementById('gareDescription').value = '';
}

// Vider le formulaire
function clearGareForm() {
    document.getElementById('gareForm').reset();
}

// Sauvegarder une gare
function saveGare() {
    const formData = {
        nom: document.getElementById('gareNom').value,
        code: document.getElementById('gareCode').value,
        type: document.getElementById('gareType').value,
        axe: document.getElementById('gareAxe').value,
        ville: document.getElementById('gareVille').value,
        etat: document.getElementById('gareEtat').value,
        codeoperationnel: document.getElementById('gareCodeOp').value,
        codereseau: document.getElementById('gareCodeReseau').value
    };
    
    if (!formData.nom || !formData.code) {
        showNotification('Le nom et le code sont obligatoires', 'error');
        return;
    }
    
    // Simuler la sauvegarde
    if (selectedGare) {
        // Mise à jour
        Object.assign(selectedGare, formData);
        showNotification('Gare mise à jour avec succès', 'success');
    } else {
        // Nouvelle gare
        const newGare = {
            id: Date.now(), // ID temporaire
            ...formData
        };
        allGares.unshift(newGare);
        showNotification('Nouvelle gare ajoutée avec succès', 'success');
    }
    
    // Fermer le modal et actualiser
    bootstrap.Modal.getInstance(document.getElementById('gareFormModal')).hide();
    applyFilters();
}

// Afficher sur la carte
function showOnMap() {
    if (selectedGare) {
        // Rediriger vers la carte avec la gare sélectionnée
        window.location.href = `/carte?gare=${selectedGare.id}`;
    }
}

// Actualiser les gares
function refreshGares() {
    loadGares();
    showNotification('Données actualisées', 'info');
}

// Exporter les gares
function exportGares() {
    const data = filteredGares.map(gare => ({
        'Nom': gare.nom || '',
        'Code': gare.code || '',
        'Type': gare.type || '',
        'Axe': gare.axe || '',
        'Ville': gare.ville || '',
        'État': gare.etat || '',
        'Code Opérationnel': gare.codeoperationnel || '',
        'Code Réseau': gare.codereseau || ''
    }));
    
    const csv = convertToCSV(data);
    downloadCSV(csv, 'gares_oncf.csv');
    showNotification('Export terminé', 'success');
}

// Convertir en CSV
function convertToCSV(data) {
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

// Télécharger le CSV
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Fonction utilitaire pour debounce
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

// Fonction pour afficher les notifications
function showNotification(message, type = 'info') {
    if (window.oncfGIS && window.oncfGIS.showNotification) {
        window.oncfGIS.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
} 