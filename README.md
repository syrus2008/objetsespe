# Application Objets Perdus et Trouvés - Festival

Une application web complète pour gérer les objets perdus et trouvés lors de festivals, avec une interface utilisateur responsive et un backend API REST.

## Fonctionnalités

- 📱 Interface utilisateur responsive
- 🖼️ Upload d'images pour les objets trouvés
- 🔍 Recherche et filtrage par type et date
- 🔄 Association automatique entre objets perdus et trouvés
- 🔐 Interface d'administration sécurisée

## Structure du projet

```
objtsperdu/
├── backend/
│   ├── uploads/      # Stockage des images
│   ├── database.py   # Gestion des données JSON
│   ├── main.py       # API FastAPI
│   ├── models.py     # Modèles de données
│   └── start_server.py # Script de démarrage
├── frontend/
│   ├── css/          # Styles CSS
│   ├── js/           # Scripts JavaScript
│   └── index.html    # Page principale
├── .gitignore        # Fichiers à ignorer par Git
├── Procfile          # Configuration pour Railway
└── requirements.txt  # Dépendances Python
```

## Installation locale

1. Cloner le dépôt
2. Installer les dépendances Python :
   ```
   pip install -r requirements.txt
   ```
3. Démarrer le serveur backend :
   ```
   cd backend
   python start_server.py
   ```
4. Ouvrir `frontend/index.html` dans un navigateur

## Déploiement sur Railway

### Prérequis

- Un compte [Railway](https://railway.app/)
- [Git](https://git-scm.com/) installé sur votre machine

### Étapes de déploiement

1. Créer un nouveau projet sur Railway :
   - Aller sur [Railway](https://railway.app/)
   - Cliquer sur "New Project"
   - Sélectionner "Deploy from GitHub repo"

2. Configurer le déploiement :
   - Connecter votre compte GitHub
   - Sélectionner le dépôt contenant ce projet
   - Railway détectera automatiquement le Procfile

3. Variables d'environnement (optionnelles) :
   - Vous pouvez définir des variables d'environnement personnalisées dans les paramètres du projet

4. Accéder à l'application :
   - Une fois le déploiement terminé, cliquer sur "Domains" pour obtenir l'URL de votre application

### Persistance des données

Sur Railway, les fichiers JSON et les images uploadées seront perdus à chaque redéploiement. Pour une solution de production, envisagez l'une des options suivantes :

1. **Solution temporaire** : Ajouter manuellement les fichiers JSON et images via Railway CLI
2. **Solution recommandée** : Migrer vers une base de données PostgreSQL et un stockage S3 pour les images

## Connexion administrateur

- Nom d'utilisateur par défaut : `admin`
- Mot de passe par défaut : `admin123`

⚠️ **Important** : Changez ces identifiants pour la production en modifiant le fichier `database.py`.

## Technologies utilisées

- **Backend** : FastAPI, Python
- **Frontend** : HTML5, CSS3, JavaScript (vanilla)
- **Stockage** : Fichiers JSON, système de fichiers local
- **Déploiement** : Railway

## Licence

Projet développé pour la gestion des objets perdus et trouvés en festivals. Tous droits réservés.
