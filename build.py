#!/usr/bin/env python3
"""
Script de construcción multiplataforma para DocTriX
Genera ejecutables para Windows, Linux y macOS
"""

import sys
import os
import subprocess
import shutil
import platform
from pathlib import Path

class DocTriXBuilder:
    """Constructor multiplataforma de DocTriX"""
    
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
        
        # Limpiar archivos .pyc
        for pycache in self.project_root.rglob('__pycache__'):
            shutil.rmtree(pycache)
            print(f"  ✓ Eliminado: {pycache}")
    
    def check_dependencies(self):
        """Verificar dependencias necesarias"""
        print("\n📦 Verificando dependencias...")
        
        required = ['PyPDF2', 'reportlab', 'PyQt6', 'PIL']
        missing = []
        
        for module in required:
            try:
                __import__(module)
                print(f"  ✓ {module} instalado")
            except ImportError:
                missing.append(module)
                print(f"  ✗ {module} no instalado")
        
        if missing:
            print(f"\n  Instala las dependencias con:")
            print(f"  pip install {' '.join(missing)}")
            return False
        
        # Verificar PyInstaller
        try:
            import PyInstaller
            print("  ✓ PyInstaller instalado")
        except ImportError:
            print("  ✗ PyInstaller no instalado")
            print("\n  pip install pyinstaller")
            return False
        
        return True
    
    def get_icon_path(self):
        """Obtener la ruta del icono según el sistema operativo"""
        if self.system == 'Windows':
            icon = self.project_root / 'assets' / 'icon.ico'
        elif self.system == 'Darwin':  # macOS
            icon = self.project_root / 'assets' / 'icon.icns'
            if not icon.exists():
                icon = self.project_root / 'assets' / 'icon.png'
        else:  # Linux
            icon = self.project_root / 'assets' / 'icon.png'
        
        return str(icon) if icon.exists() else None
    
    def get_separator(self):
        """Obtener separador para --add-data según SO"""
        return ';' if self.system == 'Windows' else ':'
    
    def build_windows(self):
        """Construir para Windows (.exe)"""
        print("\n🔨 Construyendo para Windows...")
        
        icon = self.get_icon_path()
        separator = self.get_separator()
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',  # Sin consola
            '--name', self.app_name,
            '--add-data', f'assets{separator}assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            '--hidden-import', 'PIL',
            '--collect-all', 'PyQt6',
        ]
        
        if icon:
            cmd.extend(['--icon', icon])
        
        cmd.append(str(self.project_root / 'src' / 'main.py'))
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        
        exe_path = self.project_root / 'dist' / f'{self.app_name}.exe'
        return exe_path
    
    def build_linux(self):
        """Construir para Linux (ejecutable)"""
        print("\n🔨 Construyendo para Linux...")
        
        separator = self.get_separator()
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            '--add-data', f'assets{separator}assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            '--hidden-import', 'PIL',
            str(self.project_root / 'src' / 'main.py')
        ]
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        
        exe_path = self.project_root / 'dist' / self.app_name
        return exe_path
    
    def build_macos(self):
        """Construir para macOS (.app)"""
        print("\n🔨 Construyendo para macOS...")
        
        icon = self.get_icon_path()
        separator = self.get_separator()
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', self.app_name,
            '--add-data', f'assets{separator}assets',
            '--hidden-import', 'PyPDF2',
            '--hidden-import', 'reportlab',
            '--hidden-import', 'PyQt6',
            '--hidden-import', 'PIL',
        ]
        
        if icon and icon.endswith('.icns'):
            cmd.extend(['--icon', icon])
        
        cmd.append(str(self.project_root / 'src' / 'main.py'))
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        
        # En macOS, PyInstaller crea un .app
        app_path = self.project_root / 'dist' / f'{self.app_name}.app'
        if app_path.exists():
            return app_path
        else:
            return self.project_root / 'dist' / self.app_name
    
    def build(self):
        """Construir según la plataforma actual"""
        print("\n" + "=" * 60)
        print(f"🚀 Construyendo {self.app_name} v{self.version}")
        print(f"📁 Sistema operativo: {self.system}")
        print("=" * 60)
        
        # Verificar dependencias
        if not self.check_dependencies():
            return False
        
        # Verificar que existe main.py
        main_file = self.project_root / 'src' / 'main.py'
        if not main_file.exists():
            print(f"\n✗ Error: No se encuentra {main_file}")
            return False
        
        # Verificar que existe la carpeta assets
        assets_dir = self.project_root / 'assets'
        if not assets_dir.exists():
            print(f"\n⚠️ Advertencia: No se encuentra {assets_dir}")
        
        # Limpiar construcciones anteriores
        self.clean()
        
        # Construir según plataforma
        try:
            if self.system == 'Windows':
                exe_path = self.build_windows()
                print(f"\n✅ Ejecutable generado: {exe_path}")
                
            elif self.system == 'Linux':
                exe_path = self.build_linux()
                print(f"\n✅ Ejecutable generado: {exe_path}")
                # Dar permisos de ejecución
                if exe_path.exists():
                    exe_path.chmod(0o755)
                    
            elif self.system == 'Darwin':  # macOS
                exe_path = self.build_macos()
                print(f"\n✅ Aplicación generada: {exe_path}")
                
            else:
                print(f"\n✗ Sistema no soportado: {self.system}")
                return False
            
            # Mostrar tamaño
            if exe_path and exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Tamaño: {size_mb:.1f} MB")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error en la construcción: {e}")
            return False
    
    def test_executable(self):
        """Ejecutar prueba rápida del ejecutable"""
        if self.system == 'Windows':
            exe_path = self.project_root / 'dist' / f'{self.app_name}.exe'
        elif self.system == 'Darwin':
            exe_path = self.project_root / 'dist' / f'{self.app_name}.app'
        else:
            exe_path = self.project_root / 'dist' / self.app_name
        
        if exe_path.exists():
            print("\n🧪 Probando ejecutable...")
            try:
                if self.system == 'Windows':
                    subprocess.Popen([str(exe_path)], shell=True)
                elif self.system == 'Darwin':
                    subprocess.Popen(['open', str(exe_path)])
                else:
                    subprocess.Popen([str(exe_path)])
                print("  ✓ Ejecutable iniciado correctamente")
            except Exception as e:
                print(f"  ✗ Error al ejecutar: {e}")


def main():
    builder = DocTriXBuilder()
    success = builder.build()
    
    if success:
        builder.test_executable()
    
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()