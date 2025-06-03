import uvicorn
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour l'import des modules
sys.path.append(str(Path(__file__).parent.parent))

# Définir le dossier uploads dans le répertoire du backend
uploads_dir = Path(__file__).parent / 'uploads'
uploads_dir.mkdir(exist_ok=True)

if __name__ == "__main__":
    print("🚀 Démarrage du serveur FestivalObjets...")
    # Récupérer le port depuis la variable d'environnement (pour Railway)
    # ou utiliser 8000 par défaut pour le développement local
    port = int(os.environ.get("PORT", 8000))
    
    print(f"✅ API accessible à l'adresse: http://localhost:{port}")
    print(f"✅ Documentation API: http://localhost:{port}/docs")
    print("✅ Interface utilisateur: Ouvrez frontend/index.html dans votre navigateur")
    print("📁 Les données sont stockées dans les fichiers JSON du répertoire backend")
    print("📸 Les images sont stockées dans le dossier backend/uploads")
    print("👤 Utilisateur administrateur par défaut: admin / admin123")
    print("\nAppuyez sur CTRL+C pour arrêter le serveur")
    
    # Lancer le serveur uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
