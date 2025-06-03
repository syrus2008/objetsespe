/**
 * Point d'entrée de l'application
 * Ce fichier initialise les différents modules et lance l'application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le module d'authentification
    Auth.init();
    
    // Initialiser l'interface utilisateur
    UI.init();
    
    console.log('Application initialisée avec succès!');
});
