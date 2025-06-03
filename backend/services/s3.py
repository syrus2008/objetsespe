import boto3
import os
from botocore.exceptions import ClientError
from backend.config import get_settings
from fastapi import UploadFile
import uuid

settings = get_settings()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    async def upload_file(self, file: UploadFile) -> str:
        """
        Télécharge un fichier sur S3 et renvoie l'URL
        """
        try:
            # Générer un nom de fichier unique pour éviter les conflits
            filename = f"{uuid.uuid4()}-{file.filename}"
            
            # Lire le contenu du fichier
            contents = await file.read()
            
            # Télécharger le fichier sur S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=contents,
                ContentType=file.content_type
            )
            
            # Renvoyer l'URL du fichier téléchargé
            return f"{settings.s3_url_prefix}{filename}"
            
        except ClientError as e:
            print(f"Erreur lors du téléchargement sur S3: {e}")
            raise Exception(f"Erreur lors du téléchargement du fichier: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Supprime un fichier de S3 à partir de son URL
        """
        try:
            # Extraire le nom du fichier de l'URL
            filename = file_url.replace(settings.s3_url_prefix, "")
            
            # Supprimer le fichier de S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            return True
            
        except ClientError as e:
            print(f"Erreur lors de la suppression du fichier S3: {e}")
            return False

# Créer une instance du service S3
s3_service = S3Service()
