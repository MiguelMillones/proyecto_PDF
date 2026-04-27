"""
Mi App para trabajar documentos PDF con pyqt6
Versión con soporte para PyInstaller
"""
import sys
import os
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import Qt, QStandardPaths, QMimeData, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QApplication, QWidget,QMainWindow,QTabWidget, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QFileDialog, QMessageBox, QTextEdit, QGroupBox,
    QListWidget, QListWidgetItem, QAbstractItemView, QInputDialog, QProgressBar
)

# importar módulos PDF
from pdf.extraer import extraer_paginas
from pdf.unir import unir_pdf
from pdf.foliar import foliar_pdf

# Importar utilidades de rutas
try:
    from utils.path_utils import ResourcePath, ConfigPaths
except ImportError:
    # si no existe el módulo
    class ResourcePath:
        @staticmethod
        def get_asset_path(asset_name):
            return Path(f"assets/{asset_name}")

# ==================== CLASES PARA THREADING ====================

class WorkerSignals(QObject):
    """Señales para comunicación entre threads"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class PDFWorker(QThread):
    """Thread worker para operaciones PDF sin bloquear la UI"""
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    def run(self):
        """Ejecutar la tarea en segundo plano"""
        try:
            def progress_callback(current, total, message=""):
                self.signals.progress.emit(current, total, message)
            
            result = self.task_func(
                *self.args,
                callback_progreso=progress_callback,
                **self.kwargs
            )
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

# ==================== CLASES DE UTILIDAD ====================

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
                    if start == 0 or end == 0:
                        return None
                    if start > end:
                        start, end = end, start
                    pages.update(range(start, end + 1))
                except ValueError:
                    return None
            else:
                # Página individual
                try:
                    if int(part) == 0:
                        return None
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
    
class DraggableListWidget(QListWidget):
    """ListWidget personalizada que soporta drag and drop para reordenar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDropIndicatorShown(True)

    def dropEvent(self, event: QDropEvent):
        """Manejar evento de drop para reordenar items"""
        event.setDropAction(Qt.DropAction.MoveAction)
        super().dropEvent(event)

# ==================== CLASE PRINCIPAL ====================

class Ventana(QMainWindow):
    """ clase para inicializar y estructurar las ventanas"""

    def __init__(self):
        super().__init__()

        # Variables de estado
        self.input_pdf_extract: Optional[str] = None
        self.input_pdf_foliar: Optional[str] = None
        self.files_to_merge: List[str] = []

        # Variables para threading
        self.current_worker: Optional[PDFWorker] = None

        # initialize UI
        self.inicializar()

        # load styles
        self.cargar_estilos()

    def inicializar(self):
        """función para dar el tamaño y titulo de la ventana principal"""
        self.setFixedSize(700,600)
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
            QMainWindow { background-color: #f0f0f0; }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLabel { color: #333; }
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
            QTabWidget::pane { border: 1px solid #ccc; border-radius: 4px; }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """

    def _set_buttons_enabled(self, enabled: bool):
        """Habilitar/deshabilitar botones durante procesamiento"""
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(enabled)

    def generarventanas(self):
        """Crear las pestañas de la aplicación"""
        tab_option=QTabWidget(self)

        # Crear widgets para cada pestaña
        self.extractOption = QWidget()
        self.mergeOption = QWidget()
        self.foliarOption = QWidget()
        self.aboutOption = QWidget()

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
           
    # ==================== Pestaña de Extracción ====================
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

        # Barra de progreso
        self.progress_bar_extract = QProgressBar()
        self.progress_bar_extract.setVisible(False)
        layout.addWidget(self.progress_bar_extract)
        
        self.progress_label_extract = QLabel("")
        self.progress_label_extract.setVisible(False)
        self.progress_label_extract.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label_extract)
        
        # Botón de extraer
        btn_extract = QPushButton("✅ Extraer páginas")
        btn_extract.clicked.connect(self.extract_pages)
        btn_extract.setMinimumHeight(40)
        layout.addWidget(btn_extract)
        
        layout.addStretch()        
        self.extractOption.setLayout(layout) #asignar layout a ventana extraer

    # ==================== Pestaña de Unión ====================
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

        # Barra de botones superior
        buttons_layout = QHBoxLayout()

        # Botón de seleccionar archivos
        btn_select = QPushButton("📂 Seleccionar archivos")
        btn_select.clicked.connect(self.select_files_merge)
        buttons_layout.addWidget(btn_select)

        # Botón de borrar archivos
        btn_remove = QPushButton("🗑️ Eliminar seleccionados")
        btn_remove.clicked.connect(self.remove_selected_files)
        buttons_layout.addWidget(btn_remove)

        # Botón de limpiar
        btn_clear_all = QPushButton("🚮 Limpiar todo")
        btn_clear_all.clicked.connect(self.clear_all_files)
        buttons_layout.addWidget(btn_clear_all)

        buttons_layout.addStretch()
        files_layout.addLayout(buttons_layout)

        # Información de ordenamiento
        info_label = QLabel("💡 Arrastra los items para reordenar")
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #2196F3;")
        files_layout.addWidget(info_label)

        # Lista de archivos (soporta drag & drop)
        self.files_list = DraggableListWidget()
        self.files_list.setMinimumHeight(200)
        self.files_list.model().rowsMoved.connect(self.on_files_reordered)
        files_layout.addWidget(self.files_list)

        # Contador de archivos
        self.counter_label = QLabel("📄 Archivos seleccionados: 0 ")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        files_layout.addWidget(self.counter_label)

        group_files.setLayout(files_layout)
        layout.addWidget(group_files)

        # Botones de ordenamiento adicionales
        order_layout = QHBoxLayout()
        
        btn_move_up = QPushButton("⬆️ Subir")
        btn_move_up.clicked.connect(self.move_selected_up)
        order_layout.addWidget(btn_move_up)
        
        btn_move_down = QPushButton("⬇️ Bajar")
        btn_move_down.clicked.connect(self.move_selected_down)
        order_layout.addWidget(btn_move_down)
        
        btn_sort_az = QPushButton("🔤 Ordenar A-Z")
        btn_sort_az.clicked.connect(self.sort_alphabetical)
        order_layout.addWidget(btn_sort_az)
        
        btn_sort_za = QPushButton("🔤 Ordenar Z-A")
        btn_sort_za.clicked.connect(self.sort_reverse_alphabetical)
        order_layout.addWidget(btn_sort_za)
        
        order_layout.addStretch()
        layout.addLayout(order_layout)

        # Barra de progreso
        self.progress_bar_merge = QProgressBar()
        self.progress_bar_merge.setVisible(False)
        layout.addWidget(self.progress_bar_merge)
        
        self.progress_label_merge = QLabel("")
        self.progress_label_merge.setVisible(False)
        self.progress_label_merge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label_merge)
        
        # Botón de acción
        btn_merge = QPushButton("🔗 Unir documentos")
        btn_merge.clicked.connect(self.merge)
        btn_merge.setMinimumHeight(40)     
        layout.addWidget(btn_merge)

        layout.addStretch()
        self.mergeOption.setLayout(layout)

    # ==================== Pestaña de Foliado ====================

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

        # Agregar barra de progreso
        self.progress_bar_foliar = QProgressBar()
        self.progress_bar_foliar.setVisible(False)
        layout.addWidget(self.progress_bar_foliar)
        
        self.progress_label_foliar = QLabel("")
        self.progress_label_foliar.setVisible(False)
        self.progress_label_foliar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label_foliar)

        #boton de acción
        btn_foliar = QPushButton("🔢 Foliar documento")
        btn_foliar.clicked.connect(self.foliar)
        btn_foliar.setMinimumHeight(40)
        layout.addWidget(btn_foliar)

        layout.addStretch()
        self.foliarOption.setLayout(layout)

    # ==================== Pestaña Acerca De ====================

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
        layout.addStretch()

        self.aboutOption.setLayout(layout)

    # ==================== Funciones de organización de archivos ====================

    def update_file_list_display(self):
        """Actualizar la visualización de la lista de archivos"""
        self.files_list.clear()
        for file_path in self.files_to_merge:
            nombre = Path(file_path).name
            item = QListWidgetItem(f"📄 {nombre}")
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self.files_list.addItem(item)
        
        # Actualizar contador
        count = len(self.files_to_merge)
        self.counter_label.setText(f"📄 Archivos seleccionados: {count} ")

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
            for file in files_name:
                if file not in self.files_to_merge:
                    self.files_to_merge.append(file)
            self.update_file_list_display()

    def remove_selected_files(self):
        """Eliminar archivos seleccionados de la lista"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "No hay archivos seleccionados para eliminar")
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar {len(selected_items)} archivo(s) de la lista?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.files_to_merge:
                    self.files_to_merge.remove(file_path)
            self.update_file_list_display()

    def clear_all_files(self):
        """Limpiar todos los archivos de la lista"""
        if not self.files_to_merge:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar limpieza",
            f"¿Eliminar todos los {len(self.files_to_merge)} archivo(s) de la lista?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.files_to_merge.clear()
            self.update_file_list_display()

    def move_selected_up(self):
        """Mover elementos seleccionados hacia arriba"""
        selected_rows = sorted([self.files_list.row(item) for item in self.files_list.selectedItems()])
        
        for row in selected_rows:
            if row > 0:
                # Intercambiar elementos en la lista
                self.files_to_merge[row], self.files_to_merge[row - 1] = \
                    self.files_to_merge[row - 1], self.files_to_merge[row]
        
        self.update_file_list_display()

    def move_selected_down(self):
        """Mover elementos seleccionados hacia abajo"""
        selected_rows = sorted([self.files_list.row(item) for item in self.files_list.selectedItems()], reverse=True)
        
        for row in selected_rows:
            if row < len(self.files_to_merge) - 1:
                # Intercambiar elementos en la lista
                self.files_to_merge[row], self.files_to_merge[row + 1] = \
                    self.files_to_merge[row + 1], self.files_to_merge[row]
        
        self.update_file_list_display()

    def sort_alphabetical(self):
        """Ordenar archivos alfabéticamente (A-Z)"""
        self.files_to_merge.sort(key=lambda x: Path(x).name.lower())
        self.update_file_list_display()
        QMessageBox.information(self, "Ordenado", "Archivos ordenados alfabéticamente (A-Z)")

    def sort_reverse_alphabetical(self):
        """Ordenar archivos alfabéticamente inverso (Z-A)"""
        self.files_to_merge.sort(key=lambda x: Path(x).name.lower(), reverse=True)
        self.update_file_list_display()
        QMessageBox.information(self, "Ordenado", "Archivos ordenados alfabéticamente (Z-A)")

    def on_files_reordered(self, parent, start, end, destination, row):
        """Callback cuando se reordenan archivos con drag & drop"""
        # La lista ya fue reordenada por Qt, solo actualizamos nuestra lista
        self.files_to_merge.clear()
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            self.files_to_merge.append(file_path)
        self.update_file_list_display()

    # ==================== Funciones de extracción ====================

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
            self.input_pdf_extract = file_name
            doc_name = Path(file_name).name
            self.label_file_extract.setText(doc_name)
            self.label_file_extract.setStyleSheet("color: #4CAF50; font-weight: bold;")

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
        pdf_output = SaveFileDialog.get_save_path(self,"Páginas_extraidas.pdf")    # Nombre del nuevo doc PDF
        if not pdf_output:
            return
        
        self._ejecutar_operacion(
            task_func=extraer_paginas,
            args=(self.input_pdf_extract, pdf_output, pages),
            progress_bar=self.progress_bar_extract,
            progress_label=self.progress_label_extract,
            success_msg=f"✅ Páginas extraídas correctamente!\n\nPáginas extraídas: {len(pages)}\nArchivo guardado en:\n{pdf_output}"
        )
    
    # ==================== Funciones de unión ====================

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

        # Confirmar orden
        orden = "\n".join([f"{i+1}. {Path(f).name}" for i, f in enumerate(self.files_to_merge)])
        reply = QMessageBox.question(
            self, "Confirmar orden",
            f"Los documentos se unirán en este orden:\n\n{orden}\n\n¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self._ejecutar_operacion(
            task_func=unir_pdf,
            args=(self.files_to_merge, name_output),
            progress_bar=self.progress_bar_merge,
            progress_label=self.progress_label_merge,
            success_msg=f"✅ Documentos unidos correctamente!\n\nDocumentos unidos: {len(self.files_to_merge)}\nArchivo guardado en:\n{name_output}"
        )
        
    # ==================== Funciones de foliado ====================

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
                "Por favor, ingresa un número positivo y mayor que 0..."
            )
            return

        # Guardar archivo de salida
        pdf_output = SaveFileDialog.get_save_path(self, "Páginas_foliadas.pdf")
        if not pdf_output:
            return

        self._ejecutar_operacion(
            task_func=foliar_pdf,
            args=(self.input_pdf_foliar, pdf_output, init),
            progress_bar=self.progress_bar_foliar,
            progress_label=self.progress_label_foliar,
            success_msg=f"✅ Documento foliado correctamente!\n\nNúmero inicial: {init}\nArchivo guardado en:\n{pdf_output}"
        )

    # ==================== Función genérica para ejecutar operaciones ====================

    def _ejecutar_operacion(self, task_func, args, progress_bar, progress_label, success_msg):
        """
        Ejecuta una operación en un thread separado con barra de progreso
        """
        # Verificar que los widgets aún existen
        if progress_bar is None or progress_label is None:
            QMessageBox.critical(self, "Error", "Error interno: widgets de progreso no disponibles")
            return
        
        # Crear worker
        self.current_worker = PDFWorker(task_func, *args)
        
        # Conectar señales
        self.current_worker.signals.progress.connect(
            lambda c, t, m: self._actualizar_progreso(progress_bar, progress_label, c, t, m)
        )
        self.current_worker.signals.finished.connect(
            lambda r: self._operacion_finalizada(r, success_msg, progress_bar, progress_label)
        )
        self.current_worker.signals.error.connect(
            lambda e: self._operacion_error(e, progress_bar, progress_label)
        )
        
        # Deshabilitar botones y mostrar progreso
        self._set_buttons_enabled(False)
        
        # Verificar que los widgets existen antes de usarlos
        if progress_bar:
            progress_bar.setValue(0)
            progress_bar.setVisible(True)
        if progress_label:
            progress_label.setText("Iniciando...")
            progress_label.setVisible(True)
        
        # Iniciar worker
        self.current_worker.start()

    def _actualizar_progreso(self, progress_bar, progress_label, current, total, message):
        """Actualizar barra de progreso de forma segura"""
        # Verificar que los widgets aún existen
        if progress_bar is None:
            return
        
        try:
            if total > 0:
                percentage = int((current / total) * 100)
                progress_bar.setValue(percentage)
                progress_bar.setFormat(f"{percentage}% - {current}/{total}")
            
            if progress_label and message:
                progress_label.setText(message)
        except RuntimeError:
            # Widget fue eliminado, ignorar
            pass

    def _operacion_finalizada(self, result, success_msg, progress_bar, progress_label):
        """Manejar finalización de operación"""
        # Restaurar UI
        self._set_buttons_enabled(True)
        
        # Ocultar barra de progreso
        try:
            if progress_bar:
                progress_bar.setVisible(False)
                progress_bar.setValue(0)
            if progress_label:
                progress_label.setText("")
                progress_label.setVisible(False)
        except RuntimeError:
            # Widget fue eliminado, ignorar
            pass
        
        # Limpiar worker
        self.current_worker = None
        
        # Mostrar resultado
        if result:
            QMessageBox.information(self, "Éxito", success_msg)
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error durante el proceso")

    def _operacion_error(self, error_msg, progress_bar, progress_label):
        """Manejar error en operación"""
        self._set_buttons_enabled(True)
        
        try:
            if progress_bar:
                progress_bar.setVisible(False)
                progress_bar.setValue(0)
            if progress_label:
                progress_label.setText("")
                progress_label.setVisible(False)
        except RuntimeError:
            pass
        
        self.current_worker = None
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")


if __name__=='__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Estilo moderno

    ventana = Ventana()
    sys.exit(app.exec())
