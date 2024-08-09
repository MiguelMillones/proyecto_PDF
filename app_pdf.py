"""Mi App para trabajar documentos PDF con pyqt6"""
import sys
import re
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QWidget,QMainWindow,QTabWidget, QLabel, QLineEdit, QPushButton, 
                             QHBoxLayout, QVBoxLayout,QFileDialog,QMessageBox)

def foliar_pdf(archivo_entrada, archivo_salida,inicio_folio):
    """Función para foliar un archivo pdf y crear nuevo archivo PDF de salida"""
    try:
        # Abre el archivo PDF de entrada en modo de lectura binaria
        with open(archivo_entrada, 'rb') as file:
            pdf_reader = PdfReader(file) # Crea un objeto PDFReader
            pdf_writer = PdfWriter()     # Crea un objeto PDFWriter

            fin_folio = len(pdf_reader.pages) + inicio_folio -1

            for _, page in enumerate(pdf_reader.pages):  # páginas del PDF de entrada
                page_origin = page                                # Obtén la página original
                page_size = page_origin.mediabox.upper_right      # Tamaño de página original
                w, h = page_size                                  # width, high original

                num_pagina =fin_folio
                texto_num = str(num_pagina)#str(len(pdf_reader.pages)-num_pagina) # texto de número de folio
                font_h = 16                                       # tamaño de letra
                w_num = len(texto_num)+(12*len(texto_num))        # Ancho de número (texto)
                h_num = font_h+2                                  # altura de texto
                fin_folio -=1

                pdf_num=canvas.Canvas("numerofolio.pdf")          # crar un pdf con el numero de folio.
                pdf_num.setPageSize(page_size)                    # Tamaño de pagina del pdf
                pdf_num.setFont("Times-Roman",font_h)             # Tipo de letra del texto
                pdf_num.setFillColorRGB(0,0,0,1)                  # color de texto
                if w>h:                                           # Comparación si ancho > alto
                    x = float(w - 37 - h_num)                     # calcula coordenada X
                    y = float(36 + w_num)                         # calcula coordenada y
                    pdf_num.translate(x,y)                        # traslada eje cartesiano a (x,y)
                    pdf_num.rotate(-90)                           # rotar para posicionar el texto
                    pdf_num.drawString(0,0,texto_num)             # inserta el texto (número de folio)
                else:
                    x = float(w - 37 - w_num)                     # calcula coordenada X
                    y = float(h - 36 - h_num)                     # calcula coordenada y
                    pdf_num.drawString(x,y,texto_num)             # inserta el texto (número de folio)
                pdf_num.save()                                    # guarda pdf con el texto

                num_folio = PdfReader('numerofolio.pdf')          # leer pdf creado
                page_num_folio = num_folio.pages[0]               # extrae la primera página
                page_origin.merge_page(page_num_folio)            # Unir pagina creada con la original
                pdf_writer.add_page(page_origin)                  # agregar página al objeto PDFWriter

            # Abre un nuevo archivo PDF en modo de escritura binaria
            with open(archivo_salida, 'wb') as salida:
                # Escribe el contenido del objeto PDFWriter en el nuevo archivo PDF
                pdf_writer.write(salida)
        return True
    
    except Exception as e:
        print(f"Error al foliar el documento pdf: {e}")
        return False


def unir_pdf(files, output_file):
    """Función para recorrer las páginas y unir los PDF"""
    try:
        pdf_writer = PdfWriter()                   # Crea un objeto PDFWriter

        for document in files:                     # Recorre los archivos PDF
            with open(document, 'rb') as file:     # Abre los archivos en modo de lectura binaria
                pdf_reader = PdfReader(file)       # Crea objetos PDFReader

                for page_num, _ in enumerate(pdf_reader.pages): # recorre las paginas y las enumera
                    page = pdf_reader.pages[page_num]           # Lee la página y se guarda en page
                    pdf_writer.add_page(page)                   # Agrega las páginas al escritor

        with open(output_file, 'wb') as output_doc:  # crea un nuevo archivo PDF en modo binario
            pdf_writer.write(output_doc)             # Guarda las páginas en el archivo de salida
        
        return True
    except Exception as e:
        print(f"Error al unir los documentos: {e}")
        return False

def separar_paginas(pdf_input, pdf_output, paginas_a_separar):
    """Función para separar las páginas"""
    try:
        # Abre el archivo PDF de entrada en modo binario
        with open(pdf_input, 'rb') as file:
            pdf_reader = PdfReader(file)        # Crea un objeto de lector de PDF
            pdf_writer = PdfWriter()            # Crea un objeto de escritor de PDF

            total_page = len(pdf_reader.pages)

            for pagina_num in paginas_a_separar:      # Recorre las páginas que se quieren separar
                if pagina_num<=total_page:
                    pdf_writer.add_page(pdf_reader.pages[pagina_num - 1]) # Agrega páginas al objeto
                else:
                    print('numero de pagina no se encuntra en achivo')
                    return False  # Página no existe

            # Crea un nuevo archivo PDF de salida en modo binario
            with open(pdf_output, 'wb') as output_file:
                pdf_writer.write(output_file)   # Escribe las páginas en el nuevo archivo PDF

        print(f'Se han separado las páginas {paginas_a_separar} en el archivo {pdf_output}.')
        return True # Páginas separadas correctamente
    except Exception as e:
        print(f"Error al separar páginas: {e}")
        return False

def save_file(self,name_output):
    """Función para guardar documento PDF"""
    option = QFileDialog.Option.DontUseNativeDialog
    init_dir = name_output
    filetypes = "Archivos PDF (*.pdf);;All files(*)"
    save_name, _ = QFileDialog.getSaveFileName(self,"Save File",init_dir,filetypes, options=option)

    if save_name:
        return save_name
    return None


class Ventana(QMainWindow):
    """ clase para inicializar y estructurar las ventanas"""
    def __init__(self):
        super().__init__()
        self.input_pdf = ''
        self.input_pdf3 = ''
        self.files = ''
        self.inicializar()
        with open('estilos.css',"r") as archivo:
            style=archivo.read()
        self.setStyleSheet(style)

    def inicializar(self):
        """función para dar el tamaño y titulo de la ventana principal"""
        self.setFixedSize(500,370)
        self.setWindowTitle("PDF-SUF")
        self.generarventanas()
        self.show()

    def generarventanas(self):

        tab_opcion=QTabWidget(self)
        self.separarOpcion=QWidget()
        self.unirOpcion=QWidget()
        self.foliarOpcion=QWidget()
        self.aboutOpcion=QWidget()

        tab_opcion.addTab(self.separarOpcion,"SEPARAR")
        tab_opcion.addTab(self.unirOpcion,"UNIR")
        tab_opcion.addTab(self.unirOpcion,"UNIR")
        tab_opcion.addTab(self.foliarOpcion,"FOLIAR")
        tab_opcion.addTab(self.aboutOpcion,"ABOUT")

        self.ventana_separar()
        self.ventana_unir()
        self.ventana_foliar()
        self.ventana_about()

        tab_ubication=QHBoxLayout()           
        tab_ubication.addWidget(tab_opcion)

        contenedor_tab = QWidget()              #se crea un Widget para QmainWindow
        contenedor_tab.setLayout(tab_ubication)
        self.setCentralWidget(contenedor_tab)
        

        # """Función para generar el menu de las ventanas"""
        # #ventana 1
    def ventana_separar(self):
        titulo = QLabel("SEPARAR PÁGINAS DE DOCUMENTOS PDF")
        titulo.setFont(QFont("Arial",16))
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        labels = QLabel("Seleccionar  un archivo PDF:")
        labels.setFont(QFont("Arial",12))
        botons = QPushButton("Seleccionar Archivo")
        botons.clicked.connect(self.selec_archivo)
        labels1 = QLabel("Archivo PDF:")
        labels1.setFont(QFont("Arial",12))
        self.labels1_1 = QLabel("nombre de archivo seleccionado")
        self.labels1_1.setFont(QFont("Arial",10))
        labels2 = QLabel("Ingresar las páginas a separar (separadas por comas):")
        labels2.setFont(QFont("Arial",12))
        labels3 = QLabel("Páginas a separar:")
        labels3.setFont(QFont("Arial",12))
        self.pages_sep = QLineEdit()
        botons1 = QPushButton("Separar páginas")
        botons1.clicked.connect(self.separar)

        layouts_vertical = QVBoxLayout()
        layouts_horizon = QHBoxLayout()
        layouts_horizon1 = QHBoxLayout()
        layouts_horizon2 = QHBoxLayout()

        layouts_horizon.addWidget(labels)
        layouts_horizon.addWidget(botons)
        layouts_horizon1.addWidget(labels1)
        layouts_horizon1.addWidget(self.labels1_1)
        layouts_horizon2.addWidget(labels3)
        layouts_horizon2.addWidget(self.pages_sep)

        layouts_vertical.addWidget(titulo)
        layouts_vertical.addLayout(layouts_horizon)
        layouts_vertical.addLayout(layouts_horizon1)
        layouts_vertical.addWidget(labels2)
        layouts_vertical.addLayout(layouts_horizon2)
        layouts_vertical.addWidget(botons1)

        self.separarOpcion.setLayout(layouts_vertical) #asignar layout a ventana separar

    def ventana_unir(self):
        #ventana 2
        titulo_2 = QLabel("UNIR DOCUMENTOS PDF")
        titulo_2.setFont(QFont("Arial",18))
        titulo_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels2_1 = QLabel("Seleccionar  los archivos PDF:")
        labels2_1.setFont(QFont("Arial",12))
        botons2_1 = QPushButton("Seleccionar Archivos")
        botons2_1.clicked.connect(self.selec_archivos)
        labels2_2 = QLabel("Archivos PDF:")
        labels2_2.setFont(QFont("Arial",12))
        labels2_2.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.labels2_3 = QLabel("nombres de archivos seleccionados")
        self.labels2_3.setFont(QFont("Arial",10))
        self.labels2_3.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        botons2_2 = QPushButton("Unir documentos")
        botons2_2.clicked.connect(self.unir)

        layouts2_vertical = QVBoxLayout()
        layouts2_horizon1 = QHBoxLayout()
        layouts2_horizon2 = QHBoxLayout()

        layouts2_horizon1.addWidget(labels2_1)
        layouts2_horizon1.addWidget(botons2_1)
        layouts2_horizon2.addWidget(labels2_2)
        layouts2_horizon2.addWidget(self.labels2_3)

        layouts2_vertical.addWidget(titulo_2)
        layouts2_vertical.addLayout(layouts2_horizon1)
        layouts2_vertical.addLayout(layouts2_horizon2)
        layouts2_vertical.addWidget(botons2_2)

        self.unirOpcion.setLayout(layouts2_vertical)

    def ventana_foliar(self):
        #ventana 3
        titulo_3 = QLabel("FOLIAR DOCUMENTO PDF")
        titulo_3.setFont(QFont("Arial",18))
        titulo_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labels3_1 = QLabel("Seleccionar  un archivo PDF:")
        labels3_1.setFont(QFont("Arial",12))
        botons3_1 = QPushButton("Seleccionar Archivo")
        botons3_1.clicked.connect(self.selec_archivof)
        labels3_2 = QLabel("Archivo PDF:")
        labels3_2.setFont(QFont("Arial",12))
        self.labels3_3 = QLabel("nombre de archivo seleccionado")
        self.labels3_3.setFont(QFont("Arial",10))
        labels3_4 = QLabel("Número de inicio de folio:")
        labels3_4.setFont(QFont("Arial",12))
        self.num_inicio = QLineEdit()
        botons3_2 = QPushButton("Foliar documento")
        botons3_2.clicked.connect(self.foliar)

        layout3_vertical = QVBoxLayout()
        layouts3_horizon1 = QHBoxLayout()
        layouts3_horizon2 = QHBoxLayout()
        layouts3_horizon3 = QHBoxLayout()

        layouts3_horizon1.addWidget(labels3_1)
        layouts3_horizon1.addWidget(botons3_1)
        layouts3_horizon2.addWidget(labels3_2)
        layouts3_horizon2.addWidget(self.labels3_3)
        layouts3_horizon3.addWidget(labels3_4)
        layouts3_horizon3.addWidget(self.num_inicio)

        layout3_vertical.addWidget(titulo_3)
        layout3_vertical.addLayout(layouts3_horizon1)
        layout3_vertical.addLayout(layouts3_horizon2)
        layout3_vertical.addLayout(layouts3_horizon3)
        layout3_vertical.addWidget(botons3_2)

        self.foliarOpcion.setLayout(layout3_vertical)

    def ventana_about(self):
        #ventana 4
        titulo_4 = QLabel("PDF-SUF\n\nVersion 1.0.0\nThis is a sample application made with PyQt6.\n\n"
                          "Author: Miguel Millones\n"
                          "Copyright © 2024 Miguel Angel\n\n"
                          "For more information, visit our website:\n"
                          "https://github.com/MiguelMillones/proyecto_PDF\n\n"
                          "License: MIT License\n\n"
                          "Contact: support@example.com")
        titulo_4.setFont(QFont("Arial",12))
        titulo_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_4 = QVBoxLayout()
        layout_4.addWidget(titulo_4)

        self.aboutOpcion.setLayout(layout_4)

    def selec_archivo(self):
        """Función para seleccionar documento PDF"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filetypes = "Archivos PDF (*.pdf);;All files(*)"
        file_name, _ = QFileDialog.getOpenFileName(self,"Open File",init_dir,filetypes, options=option)

        if file_name:
            doc_name = file_name.split("/")
            self.labels1_1.setText(f'{doc_name[-1]}')
            self.input_pdf=file_name
        else:
            QMessageBox.critical(self,'Error','Por favor, selecciona un archivo PDF.')

    def separar(self):
        """función para separar las paginas"""
        pdf_input = self.input_pdf               # Nombre del doc PDF de entrada
        name_pdfseparar='Páginas_separadas.pdf'# Nombre del nuevo doc PDF (páginas separadas)
        paginas_a_separar = self.pages_sep.text()

        if pdf_input=='':
            QMessageBox.critical(self,'Error','Por favor, selecciona un archivo PDF.')
            return

        if paginas_a_separar==['']:
            QMessageBox.critical(self, 'Error',
                                 'Por favor, ingresa al menos una página para separar.')
            return

        # Verificar que las páginas ingresadas consistan solo en números y comas
        if not re.match(r'^\d+(,\d+)*$', paginas_a_separar):
            QMessageBox.critical(self,'Error',
                                 'Por favor, ingresa páginas válidas (números separados por comas).')
            return
        
        pdf_output = save_file(self,name_pdfseparar)    # Nombre del nuevo doc PDF
        if pdf_output is None:
            QMessageBox.critical(self,'Error','No se guardo el nombre del nuevo documento PDF')
            return

        paginas_a_separar = paginas_a_separar.split(',')
        paginas_a_separar = list(map(int,paginas_a_separar))

        if separar_paginas(pdf_input,pdf_output,paginas_a_separar):
            QMessageBox.information(self, 'Éxito', 'Páginas separadas correctamente!')
        else:
            QMessageBox.critical(self, 'Error',
                                 'Una o más páginas no existen en el archivo seleccionado. Por favor, verifica las páginas ingresadas.')

    def selec_archivos(self):
        """Función para seleccionar documentos PDF"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filetypes = "Archivos PDF (*.pdf);;All files(*)"
        files_name, _ = QFileDialog.getOpenFileNames(self,"Open Files",init_dir,filetypes, options=option)

        if files_name:
            if len(files_name)>1:
                doc_name = ''
                for n in files_name:
                    ruta = n.split("/")
                    doc_name = doc_name + ruta[-1]+'\n '
                self.labels2_3.setText(f'{doc_name}')
                self.files = files_name
            else:
                QMessageBox.critical(self,'Error','Por favor, selecciona más de 2 documentos PDF.')
        else:
            QMessageBox.critical(self,'Error','!Ningun documento seleccionado! \n Por favor, selecciona más de 2 documentos PDF.')

    def unir(self):
        """función para comprobar archivos"""
        pdf_inputs = self.files               # Nombre del doc PDF de entrada
        name_pdfunidos='Documentos_unidos.pdf'# Nombre del archivo PDF (documentos unidos).

        if pdf_inputs == '':
            QMessageBox.critical(self,'Error','Por favor, selecciona un archivo PDF.')
            return

        name_output = save_file(self,name_pdfunidos)        # Nombre del archivo PDF (documentos unidos).

        if name_output is None:
            QMessageBox.critical(self,'Error','No se guardo el nombre del nuevo documento PDF')
            return

        if unir_pdf(pdf_inputs, name_output):
            QMessageBox.information(self, 'Éxito', 'Documentos unidos correctamente!')
        else:
            QMessageBox.critical(self, 'Error',
                                 'No se a seleccionado mas de un documento pdf. Por favor, verifica la seleccion.')

    def selec_archivof(self):
        """Función para seleccionar documento PDF para foliar"""
        option = QFileDialog.Option.DontUseNativeDialog
        init_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        filetypes = "Archivos PDF (*.pdf);;All files(*)"
        file_name3, _ = QFileDialog.getOpenFileName(self,"Open File",init_dir,filetypes, options=option)

        if file_name3:
            doc_name = file_name3.split("/")
            self.labels3_3.setText(f'{doc_name[-1]}')
            self.input_pdf3=file_name3
        else:
            QMessageBox.critical(self,'Error','Por favor, selecciona un archivo PDF.')

    def foliar(self):
        """función para comprobar y preparar archivos"""
        pdf_entrada = self.input_pdf3               # Nombre del doc PDF de entrada
        name_pdffoliar='Páginas_foliadas.pdf'       # Nombre del nuevo doc PDF (páginas foliadas)
        numero_inicio = self.num_inicio.text()

        if pdf_entrada=='':
            QMessageBox.critical(self,'Error','Por favor, selecciona un archivo PDF.')
            return

        if numero_inicio==['']:
            QMessageBox.critical(self, 'Error',
                                 'Por favor, ingresa el número de inicio.')
            return

        # Verificar que el digito ingresado sea solo un número
        if not re.match(r'^\-?[1-9][0-9]*$', numero_inicio):
            QMessageBox.critical(self,'Error',
                                 'Por favor, ingresa un número entero (sin decimales).')
            return

        pdf_output3 = save_file(self,name_pdffoliar)    # Nombre del nuevo doc PDF
        if pdf_output3 is None:
            QMessageBox.critical(self,'Error','No se guardo el nombre del nuevo documento PDF')
            return

        if foliar_pdf(pdf_entrada,pdf_output3,int(numero_inicio)):
            QMessageBox.information(self, 'Éxito', 'Páginas foliadas correctamente!')
        else:
            QMessageBox.critical(self, 'Error',
                                 'No se ha ingresado un número correcto. Por favor, verifica el número.')


if __name__=='__main__':
    app = QApplication(sys.argv)
    ventana = Ventana()
    sys.exit(app.exec())
