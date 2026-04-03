"""
Mi App para trabajar documentos PDF con pyqt6
Versión con soporte para PyInstaller
"""
import sys
import os
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget,QMainWindow,QTabWidget, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QFileDialog,QMessageBox, QTextEdit, QGroupBox
)

# módulos PDF
from pdf.extraer import extraer_paginas
from pdf.unir import unir_pdf
from pdf.foliar import foliar_pdf

# Importar utilidades de rutas
from utils.path_utils import ResourcePath, ConfigPaths


class PDFUtils:
    """Clase para operaciones comunes con PDF"""

    @staticmethod
    def validate_pdf_file(file_path: str) -> bool:
        """validar que el archivo existe y es un PDF"""
        if not file_path:
            return False
        path = Path(file_path)
        return path.exists() and path.suffix.lower() == '.pdf'
    
    @staticmethod
    def validate_page_range(pages_str: str) -> Optional[List[int]]:
        """
        Valida y convertir string de páginas a listas de enteros
        Ejemplos válidos: "1,2,3", "1-5", "1,3-5,7"
        """
        if not pages_str or not pages_str.strip():
            return None
        
        pages = set()
        parts = pages_str.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # Rango de páginas
                try:
                    start, end = map(int, part.split('-'))
                    if start > end:
                        start, end = end, start
                    pages.update(range(start, end + 1))
                except ValueError:
                    return None
            else:
                # Página individual
                try:
                    pages.add(int(part))
                except ValueError:
                    return None

        return sorted(pages)

    @staticmethod
    def validate_positive_integer(value: str) -> Optional[int]:
        """Validar que el string sea un número entero positivo"""
        if not value or not value.strip():
            return None
        try:
            num = int(value)
            if num < 1:
                return None
            return num
        except ValueError:
            return None
    
class SaveFileDialog:
    """Para guardar archivo"""
    @staticmethod
    def get_save_path(parent: QWidget, default_name: str = "documento.pdf") -> Optional[str]:
        """
        Abrir diálogo para guardar archivo
        Returns: Ruta del archivo o None si se cancela
        """
        options = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filetypes = "Archivos PDF (*.pdf);;Todos los archivos (*)"

        save_path, _ = QFileDialog.getSaveFileName(
            parent,"Guardar archivo",
            os.path.join(init_dir, default_name),
            filetypes,options=options
        )

        return save_path if save_path else None

class Ventana(QMainWindow):
    """ clase para inicializar y estructurar las ventanas"""

    def __init__(self):
        super().__init__()

        # Variables de estado
        self.input_pdf_extract: Optional[str] = None
        self.input_pdf_foliar: Optional[str] = None
        self.files_to_merge: List[str] = []

        # initialize UI
        self.inicializar()

        # load styles
        self.cargar_estilos()

    def inicializar(self):
        """función para dar el tamaño y titulo de la ventana principal"""
        self.setFixedSize(550,450)
        self.setWindowTitle("DocTriX")

        # Configure icono con manejo de rutas para PyInstaller
        self.load_icono()
        
        self.generarventanas()
        self.show()

    def load_icono(self):
        """Cargar icono de la aplicación con soporte para PyInstaller"""
        # Intentar diferentes rutas para el icono
        icon_paths = [
            ResourcePath.get_asset_path("icon.png"),      # PNG para Linux/macOS
            ResourcePath.get_asset_path("icon.ico"),      # ICO para Windows
            Path("assets/icon.png"),                      # Ruta relativa (desarrollo)
            Path("assets/icon.ico"),                      # Ruta relativa (desarrollo)
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    self.setWindowIcon(QIcon(str(icon_path)))
                    print(f"✅ Icono cargado desde: {icon_path}")
                    return
                except Exception as e:
                    print(f"⚠️ Error cargando icono desde {icon_path}: {e}")
        
        print("⚠️ No se encontró el icono de la aplicación")

    def cargar_estilos(self):
        """Cargar archivo CSS de estilos con soporte para PyInstaller"""
        try:
            # Intentar diferentes rutas para el CSS
            css_paths = [
                ResourcePath.get_asset_path("estilos.css"),  # Ruta empaquetada
                Path(__file__).parent.parent / "assets" / "estilos.css",  # Ruta desarrollo
                Path("assets/estilos.css"),                   # Ruta relativa
            ]
            
            css_file = None
            for path in css_paths:
                if path.exists():
                    css_file = path
                    break
            
            if css_file:
                with open(css_file, "r", encoding='utf-8') as archivo:
                    style = archivo.read()
                self.setStyleSheet(style)
                print(f"✅ Estilos cargados desde: {css_file}")
            else:
                # Estilos por defecto si no existe archivo
                self.setStyleSheet(self._get_default_styles())
                print("⚠️ Usando estilos por defecto")
                
        except Exception as e:
            print(f"❌ Error cargando estilos: {e}")
            self.setStyleSheet(self._get_default_styles())

    def _get_default_styles(self) -> str:
        """Estilos por defecto de la aplicación"""
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
            QLabel {
                color: #333;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 4px;
            }
        """

    def generarventanas(self):
        """Crear las pestañas de la aplicación"""
        tab_option=QTabWidget(self)

        # Crear widgets para cada pestaña
        self.extractOption=QWidget()
        self.mergeOption=QWidget()
        self.foliarOption=QWidget()
        self.aboutOption=QWidget()

        # Configurar pestañas
        self.tab_extract()
        self.tab_merge()
        self.tab_foliar()
        self.tab_about()

        # Agregar pestañas
        tab_option.addTab(self.extractOption,"📄 EXTRAER")
        tab_option.addTab(self.mergeOption,"🔗 UNIR")
        tab_option.addTab(self.foliarOption,"🔢 FOLIAR")
        tab_option.addTab(self.aboutOption,"ℹ️ ABOUT")

        # Configurar layout principal
        layout_principal=QHBoxLayout()           
        layout_principal.addWidget(tab_option)

        contenedor_tab = QWidget()              #se crea un Widget para QmainWindow
        contenedor_tab.setLayout(layout_principal)
        self.setCentralWidget(contenedor_tab)
        
        #ventana 1
    def tab_extract(self):
        """Configurar pestaña de extracción"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Título
        titulo = QLabel("📄 Extraer Páginas de PDF")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(titulo)

        # Grupo de selección de archivo
        grupo_archivo = QGroupBox("Archivo de entrada")
        grupo_layout = QVBoxLayout()

        # Selección de archivo
        hbox1 = QHBoxLayout()
        label_select = QLabel("Seleccionar archivo PDF:")
        label_select.setFont(QFont("Arial", 10))
        boton_select = QPushButton("📂 Buscar archivo")
        boton_select.clicked.connect(self.select_file_extract)
        hbox1.addWidget(label_select)
        hbox1.addWidget(boton_select)
        hbox1.addStretch()
        grupo_layout.addLayout(hbox1)

        # Mostrar archivo seleccionado
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Archivo:"))
        self.label_file_extract = QLabel("Ningún archivo seleccionado")
        self.label_file_extract.setStyleSheet("color: #666; font-style: italic;")
        hbox2.addWidget(self.label_file_extract)
        hbox2.addStretch()
        grupo_layout.addLayout(hbox2)

        grupo_archivo.setLayout(grupo_layout)
        layout.addWidget(grupo_archivo)
        
        # Grupo de páginas a extraer
        group_pages = QGroupBox("Páginas a extraer")
        pages_layout = QVBoxLayout()

        label_instruction = QLabel(
            "Ingrese las páginas a extraer (ejemplos válidos):\n"
            "Páginas individuales: 1,3,5\n"
            "Rango de páginas: 1-5\n"
            "Combinación: 1,3-5,7\n"
        )
        label_instruction.setFont(QFont("Arial",9))
        label_instruction.setStyleSheet("color: #666;")
        pages_layout.addWidget(label_instruction)

        hbox_pages = QHBoxLayout()
        hbox_pages.addWidget(QLabel("Páginas:"))
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("Ej: 1,3-5,7")
        hbox_pages.addWidget(self.pages_input)
        pages_layout.addLayout(hbox_pages)

        group_pages.setLayout(pages_layout)
        layout.addWidget(group_pages)
        
        # Botón de extraer
        btn_extract = QPushButton("✅ Extraer páginas")
        btn_extract.clicked.connect(self.extract_pages)
        btn_extract.setMinimumHeight(40)
        layout.addWidget(btn_extract)
        
        layout.addStretch()        
        self.extractOption.setLayout(layout) #asignar layout a ventana extraer

    def tab_merge(self):
        """Configurar pestaña de unión"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Título
        titulo = QLabel("🔗 Unir Documentos PDF")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Grupo de selección de archivos
        group_files = QGroupBox("Archivos a unir")
        files_layout = QVBoxLayout()

        # Botón seleccionar
        hbox1 = QHBoxLayout()
        btn_select = QPushButton("📂 Seleccionar archivos")
        btn_select.clicked.connect(self.select_files_merge)
        hbox1.addWidget(btn_select)
        hbox1.addStretch()
        files_layout.addLayout(hbox1)

        #  Lista de archivos seleccionados
        files_layout.addWidget(QLabel("Archivos seleccionados:"))
        self.lbl_files_merge = QTextEdit()
        self.lbl_files_merge.setReadOnly(True)
        self.lbl_files_merge.setMaximumHeight(150)
        self.lbl_files_merge.setPlaceholderText("No hay archivos seleccionados")
        files_layout.addWidget(self.lbl_files_merge)

        group_files.setLayout(files_layout)
        layout.addWidget(group_files)
        
        # Botón de acción
        btn_merge = QPushButton("🔗 Unir documentos")
        btn_merge.clicked.connect(self.merge)
        btn_merge.setMinimumHeight(40)     
        layout.addWidget(btn_merge)

        layout.addStretch()
        self.mergeOption.setLayout(layout)

    def tab_foliar(self):
        """Configurar pestaña de foliado"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Título
        titulo = QLabel("🔢 Foliar Documento PDF")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Grupo de selección de archivo
        group_file = QGroupBox("Archivo de entrada")
        group_layout = QVBoxLayout()

        # Seleccion de archivo
        hbox1 = QHBoxLayout()
        label_select = QLabel("Seleccionar archivo PDF:")
        label_select.setFont(QFont("Arial",10))        
        btn_select = QPushButton("📂 Buscar archivo")
        btn_select.clicked.connect(self.select_file_foliar)
        hbox1.addWidget(label_select)
        hbox1.addWidget(btn_select)
        hbox1.addStretch()
        group_layout.addLayout(hbox1)

        # mostrar archivo seleccionado
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Archivo:"))
        self.lbl_file_foliar = QLabel("Ningún archivo seleccionado")
        self.lbl_file_foliar.setStyleSheet("color: #666; font-style: italic;")
        hbox2.addWidget(self.lbl_file_foliar)
        hbox2.addStretch()
        group_layout.addLayout(hbox2)

        group_file.setLayout(group_layout)
        layout.addWidget(group_file)

        # Grupo de configuración de foliado
        group_config = QGroupBox("Configuración de foliado")
        config_layout = QVBoxLayout()

        hbox_num = QHBoxLayout()
        hbox_num.addWidget(QLabel("Número inicial:"))
        self.num_inicio = QLineEdit()
        self.num_inicio.setPlaceholderText("Ej: 1, 100, etc.")
        self.num_inicio.setText("1")
        hbox_num.addWidget(self.num_inicio)
        config_layout.addLayout(hbox_num)

        lbl_info_foliar = QLabel(
            "El foliado se realizará desde la última pagina hasta la primera.\n"
            "El número de folio se colocará en la esquina superior derecha."
        )
        lbl_info_foliar.setFont(QFont("Arial", 8))
        lbl_info_foliar.setStyleSheet("color: #666;")
        config_layout.addWidget(lbl_info_foliar)

        group_config.setLayout(config_layout)
        layout.addWidget(group_config)

        #boton de acción
        btn_foliar = QPushButton("🔢 Foliar documento")
        btn_foliar.clicked.connect(self.foliar)
        btn_foliar.setMinimumHeight(40)
        layout.addWidget(btn_foliar)

        layout.addStretch()
        self.foliarOption.setLayout(layout)

    def tab_about(self):
        """Configurar la pestaña de Acerca de"""
        layout = QVBoxLayout()
        about_text = QLabel(
            "📄 DocTriX\n\n"
            "Version 2.0.0\n\n"
            "Características:\n"
            "• Extraer páginas específicas de documentos PDF\n"
            "• Unir múltiples documentos PDF en uno solo\n"
            "• Foliar documentos PDF con numeración personalizada\n\n"
            "Desarrollador: Miguel Millones\n"
            "Copyright © 2024 Miguel Angel\n\n"
            "GitHub: https://github.com/MiguelMillones/proyecto_PDF\n"
            "License: MIT License\n\n"
            "Contact: miguelmillones22@gmail.com"
        )
        about_text.setFont(QFont("Arial",10))
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_text.setWordWrap(True)

        layout.addStretch()        
        layout.addWidget(about_text)

        self.aboutOption.setLayout(layout)

    # ==================== Manejadores de eventos ====================

    def select_file_extract(self):
        """Seleccionar archivo para extraer páginas"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        filetypes = "Archivos PDF (*.pdf);;All files (*)"
        file_name, _ = QFileDialog.getOpenFileName(
            self,"Open File", init_dir, filetypes, options=option
        )

        if file_name:
            self.input_pdf_extract=file_name
            doc_name = Path(file_name).name
            self.label_file_extract.setText(doc_name)
            self.label_file_extract.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def select_files_merge(self):
        """Seleccionar archivos para unir"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        filetypes = "Archivos PDF (*.pdf);;All files(*)"
        files_name, _ = QFileDialog.getOpenFileNames(
            self,"Open Files", init_dir, filetypes, options=option
        )

        if files_name:
            if len(files_name)>=2:
                self.files_to_merge = files_name

                # Mostrar lista de archivos
                doc_name = ""
                for n, file in enumerate(files_name, 1):
                    nombre = Path(file).name
                    doc_name += f"{n}. {nombre}\n"
                
                self.lbl_files_merge.setText(doc_name)
                self.lbl_files_merge.setStyleSheet("color: #4CAF50;")
                
            else:
                QMessageBox.warning(
                    self, "Advertencia",
                    "Por favor, selecciona al menos 2 documentos PDF para unir"
                )

    def select_file_foliar(self):
        """Seleccionar archivo para foliar"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        filetypes = "Archivos PDF (*.pdf);;All files (*)"
        file_name, _ = QFileDialog.getOpenFileName(
            self,"Open File", init_dir, filetypes, options=option
        )

        if file_name:
            self.input_pdf_foliar = file_name
            doc_name = Path(file_name).name
            self.lbl_file_foliar.setText(doc_name)
            self.lbl_file_foliar.setStyleSheet("color: #4CAF50; font-weight: bold;")
    
    def extract_pages(self):
        """función para extraer las paginas"""
        # Validaciones
        if not PDFUtils.validate_pdf_file(self.input_pdf_extract):
            QMessageBox.critical(
                self,"Error", "Por favor, selecciona un archivo PDF válido."
            )
            return
        
        pages_extract = self.pages_input.text().strip()
        if not pages_extract:
            QMessageBox.critical(
                self, 'Error',
                'Por favor, ingresa las páginas a extraer.'
            )
            return

        # Verificar que las páginas ingresadas consistan solo en números y comas
        pages = PDFUtils.validate_page_range(pages_extract)
        if pages is None:
            QMessageBox.critical(
                self,"Error",
                "Formato de páginas inválido.\n\n"
                "Ejemplos válidos:\n"
                "• 1,3,5 (páginas individuales)\n"
                "• 1-5 (rango)\n"
                "• 1,3-5,7 (combinación)"
            )
            return
        
        # Guardar archivo de salida 
        pdf_output = SaveFileDialog.get_save_path(self,"Páginas_separadas.pdf")    # Nombre del nuevo doc PDF
        if not pdf_output:
            return
        
        try:
            # Ejecutar extracción
            if extraer_paginas(self.input_pdf_extract, pdf_output, pages): #llama a la funcion 
                QMessageBox.information(
                    self, "Éxito", 
                    f"✅ Páginas extraídas correctamente!\n\n"
                    f"Páginas extraídas: {len(pages)}\n"
                    f"Archivo guardado en:\n{pdf_output}"
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Algunas páginas no existen en el documento.\n"
                    "Verifica que las páginas existan en el documento."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error al extraer páginas:\n{str(e)}"
            )

    def merge(self):
        """Unir documentos PDF"""
        if len(self.files_to_merge)<2:
            QMessageBox.critical(
                self,'Error',
                "Por favor, selecciona al menos 2 documentos PDF para unir."
            )
            return

        # Validar que todos los archivos existan
        for file in self.files_to_merge:
            if not PDFUtils.validate_pdf_file(file):
                QMessageBox.critical(
                    self, "Error", 
                    f"El archivo no es válido:\n{file}"
                )
                return
            
        # Guardar archivo de salida
        name_output = SaveFileDialog.get_save_path(self, "Documentos_unidos.pdf")
        if not name_output:
            return

        try:
            # Ejecutar unión
            if unir_pdf(self.files_to_merge, name_output):
                QMessageBox.information(
                    self, "Éxito", 
                    f"✅ Documentos unidos correctamente!\n\n"
                    f"Documentos unidos: {len(self.files_to_merge)}\n"
                    f"Archivo guardado en:\n{name_output}"
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    "No se pudieron unir los documentos. "
                    "Verifica que todos los archivos sean PDF válidos."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error al unir documentos:\n{str(e)}"
            )

    def foliar(self):
        """Foliar documento PDF"""
        # Validaciones
        if not PDFUtils.validate_pdf_file(self.input_pdf_foliar):
            QMessageBox.critical(
                self,"Error",
                "Por favor, selecciona un archivo PDF válido."
            )
            return

        # Validar número de incio
        num_init_text = self.num_inicio.text().strip()
        init = PDFUtils.validate_positive_integer(num_init_text)

        if init is None:
            QMessageBox.critical(
                self, "Error",
                "Por favor, ingresa un número entero positivo válido (ejemplo: 1, 100)."
            )
            return

        # Guardar archivo de salida
        pdf_output = SaveFileDialog.get_save_path(self, "Páginas_foliadas.pdf")
        if not pdf_output:
            return

        try:
            # Ejecutar foliado
            if foliar_pdf(self.input_pdf_foliar,pdf_output, init):
                QMessageBox.information(
                    self, "Éxito",
                    f"✅ Documento foliado correctamente!\n\n"
                    f"Número inicial: {init}\n"
                    f"Archivo guardado en:\n{pdf_output}"
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    "No se pudo foliar el documento. "
                    "Verifica que el archivo sea un PDF válido."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error al foliar documento:\n{str(e)}"
            )


if __name__=='__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Estilo moderno

    ventana = Ventana()
    sys.exit(app.exec())
