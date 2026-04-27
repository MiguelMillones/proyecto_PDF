#!/usr/bin/env python3
"""
Script de construcción para DocTriX con soporte para ReportLab
"""

import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path


class DocTriXBuilder:
    """Constructor de DocTriX"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "DocTriX"
        self.version = "2.1.0"
        self.system = platform.system()
        
    def clean(self):
        """Limpiar archivos de construcción anteriores"""
        print("\n🧹 Limpiando archivos anteriores...")
        
        dirs_to_clean = ['build', 'dist', '__pycache__']
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✓ Eliminado: {dir_name}")
        
        for pycache in self.project_root.rglob('__pycache__'):
            shutil.rmtree(pycache)
    
    def build_windows(self):
        """Construir para Windows"""
        print("\n🔨 Construyendo para Windows...")
        
        separator = ';'
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            f'--add-data=assets{separator}assets',
            f'--add-data=src/pdf{separator}pdf',
            f'--add-data=src/utils{separator}utils',
            '--paths=src',
            '--hidden-import=PyPDF2',
            '--hidden-import=reportlab',
            '--hidden-import=reportlab.pdfgen',
            '--hidden-import=reportlab.pdfgen.canvas',
            '--hidden-import=reportlab.pdfbase',
            '--hidden-import=reportlab.pdfbase.ttfonts',
            '--hidden-import=reportlab.lib',
            '--hidden-import=PyQt6',
            '--hidden-import=PIL',
            '--hidden-import=pdf.extraer',
            '--hidden-import=pdf.unir',
            '--hidden-import=pdf.foliar',
            '--hidden-import=utils.path_utils',
            '--collect-all=PyQt6',
            '--collect-all=reportlab',
            'src/main.py'
        ]
        
        # Agregar icono
        icon_path = self.project_root / 'assets' / 'icon.ico'
        if icon_path.exists():
            cmd.insert(5, f'--icon={icon_path}')
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error: {e}")
            return False
    
    def build_linux(self):
        """Construir para Linux"""
        print("\n🔨 Construyendo para Linux...")
        
        separator = ':'
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            f'--add-data=assets{separator}assets',
            f'--add-data=src/pdf{separator}pdf',
            f'--add-data=src/utils{separator}utils',
            '--paths=src',
            '--hidden-import=PyPDF2',
            '--hidden-import=reportlab',
            '--hidden-import=reportlab.pdfgen',
            '--hidden-import=reportlab.pdfgen.canvas',
            '--hidden-import=reportlab.pdfbase',
            '--hidden-import=reportlab.pdfbase.ttfonts',
            '--hidden-import=reportlab.lib',
            '--hidden-import=PyQt6',
            '--hidden-import=PIL',
            '--hidden-import=pdf.extraer',
            '--hidden-import=pdf.unir',
            '--hidden-import=pdf.foliar',
            '--hidden-import=utils.path_utils',
            '--collect-all=PyQt6',
            '--collect-all=reportlab',
            'src/main.py'
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error: {e}")
            return False
    
    def run(self):
        """Ejecutar proceso completo"""
        print("=" * 60)
        print(f"🚀 DocTriX Builder v{self.version}")
        print(f"📁 Sistema: {self.system}")
        print("=" * 60)
        
        self.clean()
        
        if self.system == 'Windows':
            success = self.build_windows()
        elif self.system == 'Linux':
            success = self.build_linux()
        elif self.system == 'Darwin':
            print("macOS requiere configuración específica")
            success = False
        else:
            print(f"Sistema no soportado: {self.system}")
            success = False
        
        if success:
            if self.system == 'Windows':
                exe_path = self.project_root / 'dist' / f'{self.app_name}.exe'
            else:
                exe_path = self.project_root / 'dist' / self.app_name
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n✅ ¡Construcción exitosa!")
                print(f"📁 Ejecutable: {exe_path}")
                print(f"📦 Tamaño: {size_mb:.1f} MB")
        
        return success


if __name__ == '__main__':
    builder = DocTriXBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)