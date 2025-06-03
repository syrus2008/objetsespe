/**
 * Module de gestion de l'interface utilisateur
 */
class UI {
    /**
     * Initialise l'interface utilisateur
     */
    static init() {
        // Initialiser les gestionnaires d'événements pour les formulaires
        UI.initFormHandlers();
        
        // Initialiser les gestionnaires d'événements pour les filtres
        UI.initFilterHandlers();
        
        // Initialiser les gestionnaires de modaux
        UI.initModalHandlers();
        
        // Initialiser la prévisualisation des images
        UI.initImagePreview();
        
        // Charger les objets au démarrage
        UI.loadAllItems();
    }

    /**
     * Initialise les gestionnaires d'événements pour les formulaires
     */
    static initFormHandlers() {
        // Boutons pour afficher les formulaires
        document.getElementById('showFoundFormBtn').addEventListener('click', () => {
            document.getElementById('foundItemForm').style.display = 'block';
            document.getElementById('lostItemForm').style.display = 'none';
        });
        
        document.getElementById('showLostFormBtn').addEventListener('click', () => {
            document.getElementById('lostItemForm').style.display = 'block';
            document.getElementById('foundItemForm').style.display = 'none';
        });
        
        // Formulaire d'objet trouvé
        document.getElementById('addFoundItemForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(e.target);
                
                // Vérifier que l'image est fournie
                const image = formData.get('image');
                if (!image || image.size === 0) {
                    throw new Error('Veuillez ajouter une image de l\'objet');
                }
                
                // Envoyer les données
                const result = await Api.addFoundItem(formData);
                
                // Réinitialiser le formulaire et afficher un message de succès
                e.target.reset();
                document.getElementById('imagePreview').innerHTML = '';
                document.getElementById('foundItemForm').style.display = 'none';
                
                // Recharger la liste des objets
                UI.loadAllItems();
                
                // Afficher un message de succès
                UI.showToast('Objet trouvé ajouté avec succès!');
            } catch (error) {
                UI.showToast(`Erreur: ${error.message}`, 'error');
            }
        });
        
        // Formulaire d'objet perdu
        document.getElementById('addLostItemForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(e.target);
                
                // Envoyer les données
                const result = await Api.addLostItem(formData);
                
                // Réinitialiser le formulaire et afficher un message de succès
                e.target.reset();
                document.getElementById('lostItemForm').style.display = 'none';
                
                // Recharger la liste des objets
                UI.loadAllItems();
                
                // Afficher un message de succès
                UI.showToast('Objet perdu ajouté avec succès!');
            } catch (error) {
                UI.showToast(`Erreur: ${error.message}`, 'error');
            }
        });
        
        // Formulaire de modification d'objet
        document.getElementById('editItemForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(e.target);
                const itemId = document.getElementById('editItemId').value;
                const itemType = document.getElementById('editItemType').value;
                
                // Récupérer les identifiants stockés dans le localStorage
                const credentials = Auth.getCredentials();
                if (!credentials) {
                    throw new Error('Vous devez être connecté pour modifier un objet');
                }
                
                // Envoyer les données
                const result = await Api.updateItem(itemId, itemType, formData, credentials);
                
                // Fermer le modal et recharger les objets
                UI.closeModal('editItemModal');
                UI.loadAllItems();
                
                // Afficher un message de succès
                UI.showToast('Objet modifié avec succès!');
            } catch (error) {
                UI.showToast(`Erreur: ${error.message}`, 'error');
            }
        });
    }

    /**
     * Initialise les gestionnaires d'événements pour les filtres
     */
    static initFilterHandlers() {
        // Filtres par type d'objet
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', () => {
                // Supprimer la classe active de tous les boutons
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Ajouter la classe active au bouton cliqué
                button.classList.add('active');
                
                // Appliquer le filtre
                const filter = button.dataset.filter;
                UI.filterItems(filter);
            });
        });
        
        // Filtre de recherche
        document.getElementById('searchBtn').addEventListener('click', () => {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            UI.filterItems('all', searchTerm);
        });
        
        // Recherche sur touche "Entrée"
        document.getElementById('searchInput').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                UI.filterItems('all', searchTerm);
            }
        });
        
        // Filtre par date
        document.getElementById('dateFilter').addEventListener('change', (e) => {
            const date = e.target.value;
            UI.filterItemsByDate(date);
        });
    }

    /**
     * Initialise les gestionnaires d'événements pour les modaux
     */
    static initModalHandlers() {
        // Fermer les modaux quand on clique sur X
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                closeBtn.closest('.modal').style.display = 'none';
            });
        });
        
        // Fermer les modaux quand on clique en dehors
        window.addEventListener('click', (e) => {
            document.querySelectorAll('.modal').forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
        
        // Bouton d'administration
        document.getElementById('adminLoginBtn').addEventListener('click', () => {
            // Si déjà connecté, afficher le bouton de déconnexion
            if (Auth.isLoggedIn()) {
                Auth.logout();
                UI.showToast('Déconnecté avec succès');
                document.getElementById('adminLoginBtn').innerHTML = '<i class="fas fa-user-shield"></i> Administration';
                
                // Masquer les boutons d'administration sur tous les objets
                UI.toggleAdminButtons(false);
                return;
            }
            
            // Sinon, afficher le modal de connexion
            UI.openModal('adminLoginModal');
        });
        
        // Formulaire de connexion admin
        document.getElementById('adminLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                // Authentifier l'utilisateur
                const success = await Auth.login(username, password);
                
                if (success) {
                    UI.closeModal('adminLoginModal');
                    document.getElementById('adminLoginBtn').innerHTML = '<i class="fas fa-sign-out-alt"></i> Déconnexion';
                    UI.showToast('Connecté en tant qu\'administrateur');
                    
                    // Afficher les boutons d'administration sur tous les objets
                    UI.toggleAdminButtons(true);
                    
                    // Réinitialiser le formulaire
                    e.target.reset();
                    document.getElementById('loginError').style.display = 'none';
                }
            } catch (error) {
                document.getElementById('loginError').textContent = `Erreur: ${error.message}`;
                document.getElementById('loginError').style.display = 'block';
            }
        });
    }

    /**
     * Initialise la prévisualisation des images
     */
    static initImagePreview() {
        // Prévisualisation de l'image pour le formulaire d'ajout
        document.getElementById('foundImage').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('imagePreview').innerHTML = `<img src="${e.target.result}" alt="Prévisualisation">`;
            };
            reader.readAsDataURL(file);
        });
        
        // Prévisualisation de l'image pour le formulaire de modification
        document.getElementById('editImage').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('editImagePreview').innerHTML = `<img src="${e.target.result}" alt="Prévisualisation">`;
            };
            reader.readAsDataURL(file);
        });
    }

    /**
     * Charge tous les objets (trouvés et perdus)
     */
    static async loadAllItems() {
        try {
            const itemsContainer = document.getElementById('itemsContainer');
            itemsContainer.innerHTML = '<div class="loading">Chargement des objets...</div>';
            
            // Récupérer les objets trouvés et perdus
            const [foundItems, lostItems] = await Promise.all([
                Api.getFoundItems(),
                Api.getLostItems()
            ]);
            
            // Fusionner et trier les objets par date de création (les plus récents d'abord)
            const allItems = [
                ...foundItems.map(item => ({ ...item, type: 'found' })),
                ...lostItems.map(item => ({ ...item, type: 'lost' }))
            ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            // Afficher les objets ou un message si aucun objet n'est disponible
            if (allItems.length === 0) {
                itemsContainer.innerHTML = '<div class="no-items">Aucun objet à afficher</div>';
                return;
            }
            
            // Afficher les objets
            itemsContainer.innerHTML = '';
            allItems.forEach(item => {
                const itemElement = UI.createItemElement(item);
                itemsContainer.appendChild(itemElement);
            });
            
            // Si l'utilisateur est connecté, afficher les boutons d'administration
            if (Auth.isLoggedIn()) {
                UI.toggleAdminButtons(true);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des objets:', error);
            document.getElementById('itemsContainer').innerHTML = `
                <div class="error-message">
                    Erreur lors du chargement des objets: ${error.message}
                </div>
            `;
        }
    }

    /**
     * Filtre les objets selon le type et un terme de recherche
     */
    static filterItems(filter = 'all', searchTerm = '') {
        const items = document.querySelectorAll('.item-card');
        
        items.forEach(item => {
            const itemType = item.dataset.type;
            const description = item.dataset.description.toLowerCase();
            const location = item.dataset.location.toLowerCase();
            
            const matchesType = filter === 'all' || itemType === filter;
            const matchesSearch = !searchTerm || 
                description.includes(searchTerm) || 
                location.includes(searchTerm);
            
            if (matchesType && matchesSearch) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    /**
     * Filtre les objets par date
     */
    static filterItemsByDate(dateString) {
        if (!dateString) {
            // Si aucune date n'est sélectionnée, afficher tous les objets
            UI.filterItems(document.querySelector('.filter-btn.active').dataset.filter);
            return;
        }
        
        const items = document.querySelectorAll('.item-card');
        
        items.forEach(item => {
            const itemDate = item.dataset.date;
            const matches = itemDate === dateString;
            
            if (matches) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    /**
     * Crée un élément HTML pour un objet
     */
    static createItemElement(item) {
        const div = document.createElement('div');
        div.className = 'item-card';
        div.dataset.id = item.id;
        div.dataset.type = item.type;
        div.dataset.description = item.description;
        div.dataset.location = item.type === 'found' ? item.location : item.location;
        div.dataset.date = item.type === 'found' ? item.found_date : item.lost_date;
        
        // Déterminer si l'objet a des correspondances
        const hasMatches = item.possible_matches && item.possible_matches.length > 0;
        
        // Formater la date
        const dateObj = new Date(item.type === 'found' ? item.found_date : item.lost_date);
        const formattedDate = dateObj.toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT);
        
        div.innerHTML = `
            ${item.type === 'found' && item.image_filename ? `
                <div class="item-image">
                    <img src="${CONFIG.UPLOADS_URL}/${item.image_filename}" alt="${item.description}">
                </div>
            ` : ''}
            <div class="item-content">
                <span class="item-type ${item.type}">
                    ${item.type === 'found' ? 'Trouvé' : 'Perdu'}
                </span>
                <h3>${item.description}</h3>
                <div class="item-meta">
                    <div><i class="fas fa-map-marker-alt"></i> ${item.type === 'found' ? item.location : item.location}</div>
                    <div><i class="fas fa-calendar-alt"></i> ${formattedDate}</div>
                    <div><i class="fas fa-clock"></i> ${item.type === 'found' ? item.found_time : item.lost_time}</div>
                </div>
                <div class="item-details">
                    ${item.content_info ? `<p>${item.content_info}</p>` : ''}
                    ${hasMatches ? `<span class="match-badge"><i class="fas fa-exchange-alt"></i> ${item.possible_matches.length} correspondance(s)</span>` : ''}
                </div>
                <div class="item-actions">
                    <button class="btn btn-primary btn-sm view-details" data-id="${item.id}" data-type="${item.type}">
                        <i class="fas fa-eye"></i> Détails
                    </button>
                    <div class="admin-buttons" style="display: none;">
                        <button class="btn btn-secondary btn-sm edit-item" data-id="${item.id}" data-type="${item.type}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger btn-sm delete-item" data-id="${item.id}" data-type="${item.type}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Ajouter les gestionnaires d'événements
        div.querySelector('.view-details').addEventListener('click', () => {
            UI.showItemDetails(item.id, item.type);
        });
        
        const editBtn = div.querySelector('.edit-item');
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                UI.showEditItemForm(item.id, item.type);
            });
        }
        
        const deleteBtn = div.querySelector('.delete-item');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                UI.confirmDeleteItem(item.id, item.type);
            });
        }
        
        return div;
    }

    /**
     * Affiche les détails d'un objet dans un modal
     */
    static async showItemDetails(itemId, itemType) {
        try {
            // Récupérer les données de l'objet
            const items = itemType === 'found' ? 
                await Api.getFoundItems() : 
                await Api.getLostItems();
            
            const item = items.find(i => i.id === itemId);
            if (!item) {
                throw new Error('Objet non trouvé');
            }
            
            // Déterminer si l'objet a des correspondances
            const hasMatches = item.possible_matches && item.possible_matches.length > 0;
            
            // Formater la date
            const dateObj = new Date(itemType === 'found' ? item.found_date : item.lost_date);
            const formattedDate = dateObj.toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT);
            
            // Préparer le contenu du modal
            let modalContent = `
                <div class="item-details-header">
                    <h2>${item.description}</h2>
                    <span class="item-type ${itemType}">
                        ${itemType === 'found' ? 'Objet trouvé' : 'Objet perdu'}
                    </span>
                </div>
            `;
            
            // Ajouter l'image si c'est un objet trouvé et qu'il a une image
            if (itemType === 'found' && item.image_filename) {
                modalContent += `
                    <div class="item-details-image">
                        <img src="${CONFIG.UPLOADS_URL}/${item.image_filename}" alt="${item.description}">
                    </div>
                `;
            }
            
            // Ajouter les informations de l'objet
            modalContent += `
                <div class="item-details-info">
                    <div><strong>Date:</strong> ${formattedDate}</div>
                    <div><strong>Heure:</strong> ${itemType === 'found' ? item.found_time : item.lost_time}</div>
                    <div><strong>Lieu:</strong> ${itemType === 'found' ? item.location : item.location}</div>
                    ${item.content_info ? `<div><strong>Informations complémentaires:</strong> ${item.content_info}</div>` : ''}
                    <div><strong>Date de déclaration:</strong> ${new Date(item.created_at).toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT)}</div>
                </div>
            `;
            
            // Ajouter les correspondances possibles
            if (hasMatches) {
                modalContent += `
                    <div class="item-details-matches">
                        <h3>Correspondances possibles</h3>
                        <div class="match-list" id="matchList">
                            <div class="loading">Chargement des correspondances...</div>
                        </div>
                    </div>
                `;
            }
            
            // Mettre à jour le contenu du modal
            document.getElementById('itemDetails').innerHTML = modalContent;
            
            // Afficher le modal
            UI.openModal('itemDetailsModal');
            
            // Si l'objet a des correspondances, les afficher
            if (hasMatches) {
                const matchList = document.getElementById('matchList');
                
                // Récupérer les objets opposés
                const oppositeItems = itemType === 'found' ? 
                    await Api.getLostItems() : 
                    await Api.getFoundItems();
                
                // Filtrer les objets correspondants
                const matches = oppositeItems.filter(i => item.possible_matches.includes(i.id));
                
                if (matches.length === 0) {
                    matchList.innerHTML = '<div>Aucune correspondance trouvée</div>';
                    return;
                }
                
                // Afficher les correspondances
                matchList.innerHTML = '';
                matches.forEach(match => {
                    const matchDate = new Date(itemType === 'found' ? match.lost_date : match.found_date);
                    const formattedMatchDate = matchDate.toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT);
                    
                    const matchElement = document.createElement('div');
                    matchElement.className = 'match-item';
                    matchElement.innerHTML = `
                        <h4>${match.description}</h4>
                        <div><strong>Date:</strong> ${formattedMatchDate}</div>
                        <div><strong>Lieu:</strong> ${match.location}</div>
                    `;
                    
                    matchElement.addEventListener('click', () => {
                        UI.closeModal('itemDetailsModal');
                        UI.showItemDetails(match.id, itemType === 'found' ? 'lost' : 'found');
                    });
                    
                    matchList.appendChild(matchElement);
                });
            }
        } catch (error) {
            console.error('Erreur lors de l\'affichage des détails de l\'objet:', error);
            UI.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    /**
     * Affiche le formulaire de modification d'un objet
     */
    static async showEditItemForm(itemId, itemType) {
        try {
            // Vérifier que l'utilisateur est connecté
            if (!Auth.isLoggedIn()) {
                throw new Error('Vous devez être connecté pour modifier un objet');
            }
            
            // Récupérer les données de l'objet
            const items = itemType === 'found' ? 
                await Api.getFoundItems() : 
                await Api.getLostItems();
            
            const item = items.find(i => i.id === itemId);
            if (!item) {
                throw new Error('Objet non trouvé');
            }
            
            // Remplir le formulaire
            document.getElementById('editItemId').value = itemId;
            document.getElementById('editItemType').value = itemType;
            document.getElementById('editDescription').value = item.description;
            document.getElementById('editDate').value = itemType === 'found' ? item.found_date : item.lost_date;
            document.getElementById('editTime').value = itemType === 'found' ? item.found_time : item.lost_time;
            document.getElementById('editLocation').value = itemType === 'found' ? item.location : item.location;
            document.getElementById('editContentInfo').value = item.content_info || '';
            
            // Afficher ou masquer le champ d'image selon le type d'objet
            const editImageGroup = document.getElementById('editImageGroup');
            if (itemType === 'found') {
                editImageGroup.style.display = 'block';
                
                // Afficher l'image actuelle si elle existe
                if (item.image_filename) {
                    document.getElementById('editImagePreview').innerHTML = `
                        <img src="${CONFIG.UPLOADS_URL}/${item.image_filename}" alt="${item.description}">
                        <p>Image actuelle (laisser vide pour conserver)</p>
                    `;
                }
            } else {
                editImageGroup.style.display = 'none';
            }
            
            // Afficher le modal
            UI.openModal('editItemModal');
        } catch (error) {
            console.error('Erreur lors de la préparation du formulaire de modification:', error);
            UI.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    /**
     * Affiche les détails d'un objet dans un modal
     */
    static async showItemDetails(itemId, itemType) {
        try {
            // Récupérer les données de l'objet
            const items = itemType === 'found' ? 
                await Api.getFoundItems() : 
                await Api.getLostItems();
            
            const item = items.find(i => i.id === itemId);
            if (!item) {
                throw new Error('Objet non trouvé');
            }
            
            // Déterminer si l'objet a des correspondances
            const hasMatches = item.possible_matches && item.possible_matches.length > 0;
            
            // Formater la date
            const dateObj = new Date(itemType === 'found' ? item.found_date : item.lost_date);
            const formattedDate = dateObj.toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT);
            
            // Préparer le contenu du modal
            let modalContent = `
                <div class="item-details-header">
                    <h2>${item.description}</h2>
                    <span class="item-type ${itemType}">
                        ${itemType === 'found' ? 'Objet trouvé' : 'Objet perdu'}
                    </span>
                </div>
            `;
            
            // Ajouter l'image si c'est un objet trouvé et qu'il a une image
            if (itemType === 'found' && item.image_filename) {
                modalContent += `
                    <div class="item-details-image">
                        <img src="${CONFIG.UPLOADS_URL}/${item.image_filename}" alt="${item.description}">
                    </div>
                `;
            }
            
            // Ajouter les informations de l'objet
            modalContent += `
                <div class="item-details-info">
                    <div><strong>Date:</strong> ${formattedDate}</div>
                    <div><strong>Heure:</strong> ${itemType === 'found' ? item.found_time : item.lost_time}</div>
                    <div><strong>Lieu:</strong> ${itemType === 'found' ? item.location : item.location}</div>
                    ${item.content_info ? `<div><strong>Informations complémentaires:</strong> ${item.content_info}</div>` : ''}
                    <div><strong>Date de déclaration:</strong> ${new Date(item.created_at).toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT)}</div>
                </div>
            `;
            
            // Ajouter les correspondances possibles
            if (hasMatches) {
                modalContent += `
                    <div class="item-details-matches">
                        <h3>Correspondances possibles</h3>
                        <div class="match-list" id="matchList">
                            <div class="loading">Chargement des correspondances...</div>
                        </div>
                    </div>
                `;
            }
            
            // Mettre à jour le contenu du modal
            document.getElementById('itemDetails').innerHTML = modalContent;
            
            // Afficher le modal
            UI.openModal('itemDetailsModal');
            
            // Si l'objet a des correspondances, les afficher
            if (hasMatches) {
                const matchList = document.getElementById('matchList');
                
                // Récupérer les objets opposés
                const oppositeItems = itemType === 'found' ? 
                    await Api.getLostItems() : 
                    await Api.getFoundItems();
                
                // Filtrer les objets correspondants
                const matches = oppositeItems.filter(i => item.possible_matches.includes(i.id));
                
                if (matches.length === 0) {
                    matchList.innerHTML = '<div>Aucune correspondance trouvée</div>';
                    return;
                }
                
                // Afficher les correspondances
                matchList.innerHTML = '';
                matches.forEach(match => {
                    const matchDate = new Date(itemType === 'found' ? match.lost_date : match.found_date);
                    const formattedMatchDate = matchDate.toLocaleDateString('fr-FR', CONFIG.DATE_FORMAT);
                    
                    const matchElement = document.createElement('div');
                    matchElement.className = 'match-item';
                    matchElement.innerHTML = `
                        <h4>${match.description}</h4>
                        <div><strong>Date:</strong> ${formattedMatchDate}</div>
                        <div><strong>Lieu:</strong> ${match.location}</div>
                    `;
                    
                    matchElement.addEventListener('click', () => {
                        UI.closeModal('itemDetailsModal');
                        UI.showItemDetails(match.id, itemType === 'found' ? 'lost' : 'found');
                    });
                    
                    matchList.appendChild(matchElement);
                });
            }
        } catch (error) {
            console.error('Erreur lors de l\'affichage des détails de l\'objet:', error);
            UI.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    /**
     * Affiche le formulaire de modification d'un objet
     */
    static async showEditItemForm(itemId, itemType) {
        try {
            // Vérifier que l'utilisateur est connecté
            if (!Auth.isLoggedIn()) {
                throw new Error('Vous devez être connecté pour modifier un objet');
            }
            
            // Récupérer les données de l'objet
            const items = itemType === 'found' ? 
                await Api.getFoundItems() : 
                await Api.getLostItems();
            
            const item = items.find(i => i.id === itemId);
            if (!item) {
                throw new Error('Objet non trouvé');
            }
            
            // Remplir le formulaire
            document.getElementById('editItemId').value = itemId;
            document.getElementById('editItemType').value = itemType;
            document.getElementById('editDescription').value = item.description;
            document.getElementById('editDate').value = itemType === 'found' ? item.found_date : item.lost_date;
            document.getElementById('editTime').value = itemType === 'found' ? item.found_time : item.lost_time;
            document.getElementById('editLocation').value = itemType === 'found' ? item.location : item.location;
            document.getElementById('editContentInfo').value = item.content_info || '';
            
            // Afficher ou masquer le champ d'image selon le type d'objet
            const editImageGroup = document.getElementById('editImageGroup');
            if (itemType === 'found') {
                editImageGroup.style.display = 'block';
                
                // Afficher l'image actuelle si elle existe
                if (item.image_filename) {
                    document.getElementById('editImagePreview').innerHTML = `
                        <img src="${CONFIG.UPLOADS_URL}/${item.image_filename}" alt="${item.description}">
                        <p>Image actuelle (laisser vide pour conserver)</p>
                    `;
                }
            } else {
                editImageGroup.style.display = 'none';
            }
            
            // Afficher le modal
            UI.openModal('editItemModal');
        } catch (error) {
            console.error('Erreur lors de la préparation du formulaire de modification:', error);
            UI.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    /**
     * Confirme la suppression d'un objet
     */
    static confirmDeleteItem(itemId, itemType) {
        // Vérifier que l'utilisateur est connecté
        if (!Auth.isLoggedIn()) {
            UI.showToast('Vous devez être connecté pour supprimer un objet', 'error');
            return;
        }
        
        // Demander confirmation
        if (confirm(`Êtes-vous sûr de vouloir supprimer cet objet ${itemType === 'found' ? 'trouvé' : 'perdu'} ?`)) {
            UI.deleteItem(itemId, itemType);
        }
    }

    /**
     * Supprime un objet
     */
    static async deleteItem(itemId, itemType) {
        try {
            // Récupérer les identifiants stockés dans le localStorage
            const credentials = Auth.getCredentials();
            if (!credentials) {
                throw new Error('Vous devez être connecté pour supprimer un objet');
            }
            
            // Supprimer l'objet
            await Api.deleteItem(itemId, itemType, credentials);
            
            // Recharger la liste des objets
            UI.loadAllItems();
            
            // Afficher un message de succès
            UI.showToast('Objet supprimé avec succès!');
        } catch (error) {
            console.error('Erreur lors de la suppression de l\'objet:', error);
            UI.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    /**
     * Active ou désactive les boutons d'administration sur tous les objets
     */
    static toggleAdminButtons(show) {
        document.querySelectorAll('.admin-buttons').forEach(buttons => {
            buttons.style.display = show ? 'block' : 'none';
        });
    }

    /**
     * Ouvre un modal
     */
    static openModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    /**
     * Ferme un modal
     */
    static closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    /**
     * Affiche un message toast
     */
    static showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = toast.querySelector('.toast-message');
        const toastIcon = toast.querySelector('.toast-content i');
        const toastProgress = toast.querySelector('.toast-progress');
        
        // Définir le message
        toastMessage.textContent = message;
        
        // Définir l'icône selon le type
        if (type === 'success') {
            toastIcon.className = 'fas fa-check-circle';
            toastIcon.style.color = 'var(--success-color)';
        } else if (type === 'error') {
            toastIcon.className = 'fas fa-times-circle';
            toastIcon.style.color = 'var(--danger-color)';
        } else if (type === 'warning') {
            toastIcon.className = 'fas fa-exclamation-circle';
            toastIcon.style.color = 'var(--warning-color)';
        } else if (type === 'info') {
            toastIcon.className = 'fas fa-info-circle';
            toastIcon.style.color = 'var(--info-color)';
        }
        
        // Afficher le toast
        toast.style.display = 'block';
        
        // Animer la barre de progression
        toastProgress.style.width = '100%';
        
        // Masquer le toast après 4 secondes
        setTimeout(() => {
            toast.style.display = 'none';
            toastProgress.style.width = '0';
        }, 4000);
    }
}
