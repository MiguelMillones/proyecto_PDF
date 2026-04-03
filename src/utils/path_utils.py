"""
Utilidades para manejo de rutas en aplicaciones empaquetadas con PyInstaller
"""
import sys
import os
from pathlib import Path
from typing import Optional, Union

class ResourcePath:
    """Manejador de rutas para recursos en aplicaciones empaquetadas"""
    
    @staticmethod
    def get_base_path() -> Path:
        """
        Obtiene la ruta base de la aplicación
        - En desarrollo: Directorio del script
        - En ejecutable: Directorio temporal _MEIPASS
        """
        if getattr(sys, 'frozen', False):
            # Ejecutable PyInstaller
            return Path(sys._MEIPASS)
        else:
            # Modo desarrollo
            return Path(__file__).parent.parent.parent
    
    @staticmethod
    def get_resource_path(relative_path: Union[str, Path]) -> Path:
        """
        Obtiene la ruta absoluta de un recurso
        
        Args:
            relative_path: Ruta relativa desde la raíz del proyecto
            
        Returns:
            Path: Ruta absoluta del recurso
        """
        base_path = ResourcePath.get_base_path()
        return base_path / relative_path
    
    @staticmethod
    def resource_exists(relative_path: Union[str, Path]) -> bool:
        """Verifica si un recurso existe"""
        return ResourcePath.get_resource_path(relative_path).exists()
    
    @staticmethod
    def get_asset_path(asset_name: str) -> Path:
        """Obtiene ruta específica para assets"""
        return ResourcePath.get_resource_path(f"assets/{asset_name}")


class ConfigPaths:
    """Manejador de rutas de configuración y archivos de usuario"""
    
    @staticmethod
    def get_user_data_dir(app_name: str = "DocTriX") -> Path:
        """
        Obtiene el directorio de datos del usuario
        - Windows: %APPDATA%/DocTriX
        - Linux: ~/.config/DocTriX
        - macOS: ~/Library/Application Support/DocTriX
        """
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
        elif sys.platform == 'darwin':
            base = Path.home() / 'Library/Application Support'
        else:  # Linux y otros
            base = Path.home() / '.config'
        
        user_dir = base / app_name
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    @staticmethod
    def get_temp_dir() -> Path:
        """Obtiene el directorio temporal para la aplicación"""
        if getattr(sys, 'frozen', False):
            # En ejecutable, usar directorio temporal del sistema
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "DocTriX"
        else:
            # En desarrollo, usar directorio local
            temp_dir = Path(__file__).parent.parent.parent / "temp"
        
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    @staticmethod
    def get_recent_files_path() -> Path:
        """Obtiene la ruta para el archivo de archivos recientes"""
        return ConfigPaths.get_user_data_dir() / "recent_files.json"
    
    @staticmethod
    def get_config_path() -> Path:
        """Obtiene la ruta para el archivo de configuración"""
        return ConfigPaths.get_user_data_dir() / "config.json"