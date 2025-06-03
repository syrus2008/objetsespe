import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import uuid
from ..config import get_settings

settings = get_settings()

# Configuration de Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

class CloudStorageService:
    async def upload_file(self, file: UploadFile) -> str:
        """
        Télécharge un fichier sur Cloudinary et renvoie l'URL
        """
        try:
            # Générer un nom de fichier unique pour éviter les conflits
            filename = f"{uuid.uuid4()}-{file.filename}"
            
            # Lire le contenu du fichier
            contents = await file.read()
            
            # Télécharger le fichier sur Cloudinary
            upload_result = cloudinary.uploader.upload(
                contents,
                public_id=filename,
                folder="festival-objets-perdus",
                resource_type="auto"
            )
            
            # Renvoyer l'URL du fichier téléchargé
            return upload_result["secure_url"]
            
        except Exception as e:
            print(f"Erreur lors du téléchargement sur Cloudinary: {e}")
            raise Exception(f"Erreur lors du téléchargement du fichier: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Supprime un fichier de Cloudinary à partir de son URL
        """
        try:
            # Extraire l'ID public de l'URL
            # Format URL: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/festival-objets-perdus/abcdef-image.jpg
            parts = file_url.split('/')
            folder_index = parts.index("festival-objets-perdus")
            public_id = f"festival-objets-perdus/{parts[folder_index + 1].split('.')[0]}"
            
            # Supprimer le fichier de Cloudinary
            cloudinary.uploader.destroy(public_id)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier Cloudinary: {e}")
            return False

# Créer une instance du service de stockage cloud
cloud_storage_service = CloudStorageService()
