"""
Encryption service for sensitive financial data
"""
from cryptography.fernet import Fernet
import base64
from app.config import settings


class EncryptionService:
    """Server-side encryption for sensitive data"""
    
    def __init__(self) -> None:
        # Ensure encryption key is valid Fernet key (32 bytes base64 encoded)
        key = settings.ENCRYPTION_KEY.encode()
        self.fernet = Fernet(key)
    
    def encrypt(self, client_encrypted: str) -> str:
        """
        Re-encrypt client-encrypted data with app key
        
        Args:
            client_encrypted: Data already encrypted by client with user key
        
        Returns:
            Double-encrypted data for database storage
        """
        return self.fernet.encrypt(client_encrypted.encode()).decode()
    
    def decrypt(self, db_value: str) -> str:
        """
        Decrypt server-side encryption to get client-encrypted value
        
        Args:
            db_value: Double-encrypted data from database
        
        Returns:
            Client-encrypted value (frontend will decrypt further)
        """
        return self.fernet.decrypt(db_value.encode()).decode()
    
    def encrypt_server_only(self, plaintext: str) -> str:
        """
        Encrypt data that doesn't need client-side encryption
        
        Args:
            plaintext: Plain text data
        
        Returns:
            Server-encrypted data
        """
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt_server_only(self, encrypted: str) -> str:
        """
        Decrypt server-only encrypted data
        
        Args:
            encrypted: Server-encrypted data
        
        Returns:
            Plain text data
        """
        return self.fernet.decrypt(encrypted.encode()).decode()


# Global encryption service instance
encryption_service = EncryptionService()
