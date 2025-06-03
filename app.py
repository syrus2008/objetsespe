"""
Point d'entrée principal pour l'application FastAPI
Ce fichier est utilisé par Railway pour démarrer l'application
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import l'application depuis le module backend
from backend.main import app as backend_app

# Exposer l'application pour que Railway puisse la trouver
app = backend_app

# Si ce fichier est exécuté directement, démarrer le serveur
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
