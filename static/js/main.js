// ONCF GIS - Main JavaScript File

// Configuration globale
const CONFIG = {
    API_BASE_URL: '',
    MAP_CENTER: [31.7917, -7.0926], // Centre du Maroc
    MAP_ZOOM: 6,
    REFRESH_INTERVAL: 30000 // 30 secondes
};

// Classe principale de l'application
class ONCFGIS {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation active
        document.addEventListener('DOMContentLoaded', () => {
            this.setActiveNavigation();
            this.setupTooltips();
            this.setupAnimations();
        });

        // Gestion des erreurs globales
        window.addEventListener('error', (e) => {
            console.error('Erreur JavaScript:', e.error);
            this.showNotification('Une erreur est survenue', 'error');
        });
    }

    initializeComponents() {
        // Initialiser les composants selon la page
        const currentPage = this.getCurrentPage();
        
        switch(currentPage) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'carte':
                this.initMap();
                break;
            case 'statistiques':
                this.initCharts();
                break;
            case 'gares':
                this.initGaresTable();
                break;
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/') return 'home';
        if (path === '/dashboard') return 'dashboard';
        if (path === '/carte') return 'carte';
        if (path === '/statistiques') return 'statistiques';
        if (path === '/gares') return 'gares';
        return 'home';
    }

    setActiveNavigation() {
        const currentPage = this.getCurrentPage();
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === window.location.pathname) {
                link.classList.add('active');
            }
        });
    }

    setupTooltips() {
        // Initialiser les tooltips Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupAnimations() {
        // Animation d'apparition des éléments
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observer les cartes et sections
        document.querySelectorAll('.card, .stat-card, .quick-action-card').forEach(el => {
            observer.observe(el);
        });
    }

    // Méthodes pour le Dashboard
    initDashboard() {
        this.loadDashboardStats();
        this.initDashboardCharts();
    }

    loadDashboardStats() {
        fetch('/api/statistiques')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateDashboardStats(data.data);
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des statistiques:', error);
                this.showNotification('Erreur lors du chargement des données', 'error');
            });
    }

    updateDashboardStats(stats) {
        // Mettre à jour les statistiques du dashboard
        const elements = {
            'total-gares': stats.gares.total,
            'total-arcs': stats.arcs.total,
            'gares-actives': stats.gares.par_type.find(t => t.type === 'ACTIVE')?.count || 0,
            'gares-passives': stats.gares.par_type.find(t => t.type === 'PASSIVE')?.count || 0
        };

        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumber(element, elements[id]);
            }
        });
    }

    animateNumber(element, targetValue) {
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();

        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }

        requestAnimationFrame(updateNumber);
    }

    initDashboardCharts() {
        // Initialiser les graphiques du dashboard
        this.createGaresTypeChart();
        this.createAxesChart();
    }

    createGaresTypeChart() {
        const ctx = document.getElementById('garesTypeChart');
        if (!ctx) return;

        fetch('/api/statistiques')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const chartData = data.data.gares.par_type;
                    
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: chartData.map(item => item.type || 'Non défini'),
                            datasets: [{
                                data: chartData.map(item => item.count),
                                backgroundColor: [
                                    '#0d6efd',
                                    '#198754',
                                    '#ffc107',
                                    '#dc3545',
                                    '#6c757d'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'bottom'
                                },
                                title: {
                                    display: true,
                                    text: 'Répartition des Gares par Type'
                                }
                            }
                        }
                    });
                }
            });
    }

    createAxesChart() {
        const ctx = document.getElementById('axesChart');
        if (!ctx) return;

        fetch('/api/statistiques')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const chartData = data.data.gares.par_axe;
                    
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: chartData.map(item => item.axe || 'Non défini'),
                            datasets: [{
                                label: 'Nombre de Gares',
                                data: chartData.map(item => item.count),
                                backgroundColor: '#0d6efd',
                                borderColor: '#0d6efd',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Répartition des Gares par Axe'
                                }
                            }
                        }
                    });
                }
            });
    }

    // Méthodes pour la Carte
    initMap() {
        // Initialisation de la carte (sera implémentée dans carte.js)
        if (typeof initONCFMap === 'function') {
            initONCFMap();
        }
    }

    // Méthodes pour les Statistiques
    initCharts() {
        // Initialiser les graphiques de statistiques
        this.createGaresTypeChart();
        this.createAxesChart();
        this.createTimelineChart();
    }

    createTimelineChart() {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) return;

        // Exemple de données temporelles
        const data = {
            labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Trafic Passagers',
                data: [65, 59, 80, 81, 56, 55],
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4
            }]
        };

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Évolution du Trafic'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Méthodes pour la Table des Gares
    initGaresTable() {
        this.loadGaresData();
        this.setupTableFilters();
    }

    loadGaresData() {
        const tableBody = document.getElementById('garesTableBody');
        if (!tableBody) return;

        fetch('/api/gares')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.renderGaresTable(data.data);
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des gares:', error);
                this.showNotification('Erreur lors du chargement des gares', 'error');
            });
    }

    renderGaresTable(gares) {
        const tableBody = document.getElementById('garesTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        gares.forEach(gare => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${gare.nom || 'N/A'}</td>
                <td>${gare.code || 'N/A'}</td>
                <td>${gare.type || 'N/A'}</td>
                <td>${gare.axe || 'N/A'}</td>
                <td>${gare.ville || 'N/A'}</td>
                <td>
                    <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">
                        ${gare.etat || 'N/A'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="showGareDetails(${gare.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    setupTableFilters() {
        // Implémenter les filtres de table
        const searchInput = document.getElementById('searchGares');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterGaresTable(e.target.value);
            });
        }
    }

    filterGaresTable(searchTerm) {
        const rows = document.querySelectorAll('#garesTableBody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const match = text.includes(searchTerm.toLowerCase());
            row.style.display = match ? '' : 'none';
        });
    }

    // Utilitaires
    showNotification(message, type = 'info') {
        // Créer une notification toast
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = document.getElementById('toastContainer') || document.body;
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Supprimer après fermeture
        toast.addEventListener('hidden.bs.toast', () => {
            container.removeChild(toast);
        });
    }

    startAutoRefresh() {
        // Actualisation automatique des données
        setInterval(() => {
            if (this.getCurrentPage() === 'dashboard') {
                this.loadDashboardStats();
            }
        }, CONFIG.REFRESH_INTERVAL);
    }

    // Méthodes utilitaires pour les géométries
    parseGeometry(geometryString) {
        if (!geometryString) return null;
        
        try {
            // Parser la géométrie WKT
            const match = geometryString.match(/POINT\(([^)]+)\)/);
            if (match) {
                const coords = match[1].split(' ').map(Number);
                return [coords[1], coords[0]]; // [lat, lng] pour Leaflet
            }
        } catch (error) {
            console.error('Erreur lors du parsing de la géométrie:', error);
        }
        
        return null;
    }
}

// Fonctions globales
function showGareDetails(gareId) {
    // Afficher les détails d'une gare
    fetch(`/api/gares/${gareId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Créer une modal avec les détails
                const modal = new bootstrap.Modal(document.getElementById('gareDetailsModal'));
                // Remplir les données de la modal
                modal.show();
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des détails:', error);
        });
}

// Initialiser l'application
document.addEventListener('DOMContentLoaded', () => {
    window.oncfGIS = new ONCFGIS();
});

// Exporter pour utilisation dans d'autres fichiers
window.ONCFGIS = ONCFGIS; 