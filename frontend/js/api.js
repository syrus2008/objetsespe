/**
 * Module de gestion des appels API
 */
class Api {
    /**
     * Récupère tous les objets trouvés
     */
    static async getFoundItems() {
        try {
            const response = await fetch(`${CONFIG.API_URL}/found`);
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Erreur lors de la récupération des objets trouvés:', error);
            throw error;
        }
    }

    /**
     * Récupère tous les objets perdus
     */
    static async getLostItems() {
        try {
            const response = await fetch(`${CONFIG.API_URL}/lost`);
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Erreur lors de la récupération des objets perdus:', error);
            throw error;
        }
    }

    /**
     * Envoie un nouvel objet trouvé avec une image
     */
    static async addFoundItem(formData) {
        try {
            const response = await fetch(`${CONFIG.API_URL}/found`, {
                method: 'POST',
                body: formData
                // Ne pas définir Content-Type car FormData le fait automatiquement avec multipart/form-data
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erreur lors de l\'ajout d\'un objet trouvé:', error);
            throw error;
        }
    }

    /**
     * Envoie un nouvel objet perdu
     */
    static async addLostItem(formData) {
        try {
            const response = await fetch(`${CONFIG.API_URL}/lost`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erreur lors de l\'ajout d\'un objet perdu:', error);
            throw error;
        }
    }

    /**
     * Supprime un objet (nécessite authentification)
     */
    static async deleteItem(itemId, itemType, credentials) {
        try {
            const response = await fetch(`${CONFIG.API_URL}/${itemType}/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Non autorisé: Identifiants incorrects');
                }
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Erreur lors de la suppression d'un objet ${itemType}:`, error);
            throw error;
        }
    }

    /**
     * Met à jour un objet (nécessite authentification)
     */
    static async updateItem(itemId, itemType, formData, credentials) {
        try {
            const response = await fetch(`${CONFIG.API_URL}/${itemType}/${itemId}`, {
                method: 'PUT',
                body: formData,
                headers: {
                    'Authorization': `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Non autorisé: Identifiants incorrects');
                }
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Erreur lors de la mise à jour d'un objet ${itemType}:`, error);
            throw error;
        }
    }
}
