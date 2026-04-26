#!/usr/bin/env python3
"""
Script de construcción multiplataforma para DocTriX
Genera ejecutables para Windows, Linux y macOS
"""
import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path


class PlatformBuilder:
    """Constructor para diferentes plataformas"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent
        self.app_name = "DocTriX"
        self.version = "2.0.0"
        
    def clean(self):
        """Limpiar archivos de construcción anteriores"""
        print("🧹 Limpiando archivos anteriores...")
        dirs_to_clean = ['build', 'dist', '__pycache__']
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Eliminado: {dir_name}")
    
    def build_windows(self):
        """Construir para Windows"""
        print("\n🔨 Construyendo para Windows...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            '--icon', str(self.project_root / 'assets' / 'icon.ico'),
            '--add-data', f'assets{os.pathsep}assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            '--collect-all', 'PyQt6',
            str(self.project_root / 'src' / 'main.py')
        ]
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        print(f"✅ Ejecutable generado: dist/{self.app_name}.exe")
    
    def build_linux(self):
        """Construir para Linux"""
        print("\n🔨 Construyendo para Linux...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            '--add-data', f'assets:assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            str(self.project_root / 'src' / 'main.py')
        ]
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        print(f"✅ Ejecutable generado: dist/{self.app_name}")
    
    def build_macos(self):
        """Construir para macOS"""
        print("\n🔨 Construyendo para macOS...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            '--add-data', f'assets:assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            str(self.project_root / 'src' / 'main.py')
        ]
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        print(f"✅ Aplicación generada: dist/{self.app_name}")
    
    def build(self):
        """Construir según la plataforma actual"""
        print("=" * 50)
        print(f"🚀 Construyendo {self.app_name} v{self.version}")
        print(f"📁 Sistema: {self.system}")
        print("=" * 50)
        
        self.clean()
        
        if self.system == 'Windows':
            self.build_windows()
        elif self.system == 'Linux':
            self.build_linux()
        elif self.system == 'Darwin':
            self.build_macos()
        else:
            print(f"❌ Sistema no soportado: {self.system}")
            return False
        
        print("\n" + "=" * 50)
        print("✅ Construcción completada exitosamente!")
        print("=" * 50)
        return True


if __name__ == '__main__':
    builder = PlatformBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)