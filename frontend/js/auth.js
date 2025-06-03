/**
 * Module de gestion de l'authentification
 */
class Auth {
    /**
     * Vérifie si l'utilisateur est connecté
     */
    static isLoggedIn() {
        return localStorage.getItem('auth_credentials') !== null;
    }
    
    /**
     * Récupère les identifiants stockés
     */
    static getCredentials() {
        const credentials = localStorage.getItem('auth_credentials');
        return credentials ? JSON.parse(credentials) : null;
    }
    
    /**
     * Stocke les identifiants
     */
    static setCredentials(username, password) {
        const credentials = { username, password };
        localStorage.setItem('auth_credentials', JSON.stringify(credentials));
    }
    
    /**
     * Supprime les identifiants
     */
    static logout() {
        localStorage.removeItem('auth_credentials');
    }
    
    /**
     * Initialise les gestionnaires d'événements pour l'authentification
     */
    static init() {
        // Formulaire de connexion
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                // Tester l'authentification
                const isValid = await Api.checkAuth(username, password);
                
                if (isValid) {
                    // Stocker les identifiants
                    Auth.setCredentials(username, password);
                    
                    // Fermer le modal
                    UI.closeModal('loginModal');
                    
                    // Afficher les boutons d'administration
                    UI.toggleAdminButtons(true);
                    
                    // Afficher un toast de succès
                    UI.showToast('Connexion réussie!');
                } else {
                    UI.showToast('Identifiants incorrects', 'error');
                }
            } catch (error) {
                console.error('Erreur lors de la connexion:', error);
                UI.showToast(`Erreur: ${error.message}`, 'error');
            }
        });
        
        // Bouton de déconnexion
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            
            // Supprimer les identifiants
            Auth.logout();
            
            // Masquer les boutons d'administration
            UI.toggleAdminButtons(false);
            
            // Afficher un toast de succès
            UI.showToast('Déconnexion réussie!');
        });
        
        // Bouton d'affichage du formulaire de connexion
        document.getElementById('showLoginBtn').addEventListener('click', (e) => {
            e.preventDefault();
            
            // Si l'utilisateur est déjà connecté, on le déconnecte
            if (Auth.isLoggedIn()) {
                Auth.logout();
                UI.toggleAdminButtons(false);
                UI.showToast('Déconnexion réussie!');
                return;
            }
            
            // Sinon on affiche le formulaire de connexion
            UI.openModal('loginModal');
        });
        
        // Vérifier si l'utilisateur est déjà connecté au chargement
        if (Auth.isLoggedIn()) {
            UI.toggleAdminButtons(true);
        } else {
            UI.toggleAdminButtons(false);
        }
    }
}
