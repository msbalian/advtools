import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional, List
import models

class StorageProvider(ABC):
    @abstractmethod
    async def save_file(self, content: bytes, relative_path: str, filename: str) -> str:
        """Salva o arquivo e retorna o caminho/ID para persistência no banco."""
        pass

    @abstractmethod
    async def get_file_url(self, path_or_id: str) -> str:
        """Retorna a URL de exibição/download."""
        pass

    @abstractmethod
    async def delete_file(self, path_or_id: str):
        """Remove o arquivo."""
        pass

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "static"):
        # Garante que o path seja absoluto para evitar confusão com CWD
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, content: bytes, relative_path: str, filename: str) -> str:
        # relative_path esperado: "armazenamento/cliente_1/documentos"
        # Se não começar com armazenamento, adicionamos
        if not relative_path.startswith("armazenamento"):
            relative_path = os.path.join("armazenamento", relative_path)
            
        target_dir = os.path.join(self.base_dir, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        
        full_path = os.path.join(target_dir, filename)
        with open(full_path, "wb") as f:
            f.write(content)
            
        # Retorna o path relativo ao 'static/'
        return os.path.join(relative_path, filename).replace("\\", "/")

    async def get_file_url(self, path: str) -> str:
        # Retorna o path pronto para ser prefixado por /static/
        return path

    async def delete_file(self, path: str):
        full_path = os.path.join(self.base_dir, path)
        if os.path.exists(full_path):
            os.remove(full_path)

def get_storage_provider(escritorio: models.Escritorio) -> StorageProvider:
    return LocalStorageProvider()
