from supabase import create_client, Client
from config import get_settings
from typing import Optional

settings = get_settings()

class StorageService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            # Check if bucket exists
            self.supabase.storage.get_bucket(self.bucket_name)
        except Exception:
            try:
                # Create bucket if it doesn't exist
                self.supabase.storage.create_bucket(self.bucket_name, options={"public": True})
            except Exception as e:
                print(f"Error creating bucket: {e}")

    def upload_chunk(self, bucket: str, file_path: str, chunk: bytes) -> bool:
        """
        In a real-world scenario with Supabase, you'd use TUS for chunked uploads.
        This simplified version uses upsert which overwrites if not careful.
        """
        try:
            self.supabase.storage.from_(bucket).upload(
                path=file_path,
                file=chunk,
                file_options={"upsert": "true"}
            )
            return True
        except Exception as e:
            print(f"Error uploading chunk: {e}")
            return False

    def upload_file(self, bucket: str, file_path: str, file_bytes: bytes, content_type: str = "video/mp4") -> str:
        try:
            self.supabase.storage.from_(bucket).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            return file_path
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def delete_file(self, bucket: str, file_path: str) -> bool:
        try:
            self.supabase.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_url(self, bucket: str, file_path: str) -> str:
        try:
            return self.supabase.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            print(f"Error getting public URL: {e}")
            return None

    def get_signed_url(self, bucket: str, file_path: str, expires_in: int = 86400) -> str:
        try:
            # Supabase Python SDK create_signed_url returns the URL directly or a dict
            res = self.supabase.storage.from_(bucket).create_signed_url(file_path, expires_in)
            if isinstance(res, dict) and 'signedURL' in res:
                return res['signedURL']
            return res
        except Exception as e:
            print(f"Error getting signed URL: {e}")
            return None

storage_service = StorageService()
