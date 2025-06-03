"""
Point d'entrée principal pour l'application FastAPI
Ce fichier est utilisé par Railway pour démarrer l'application
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse

# Import l'application depuis le module backend
from backend.main import app as backend_app

# Configuration de l'application
app = backend_app

# Monter les fichiers statiques du frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")

# Route racine qui sert index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Route pour les autres pages HTML
@app.get("/admin.html", response_class=HTMLResponse)
async def read_admin():
    with open("frontend/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Favicon
@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return FileResponse("frontend/favicon.ico")

# Si ce fichier est exécuté directement, démarrer le serveur
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
