"""Código para unir documentos PDF"""
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional, Callable

def unir_pdf(files, output_file, callback_progreso: Optional[Callable] = None):
    """
    Unir múltiples PDFs en uno solo
    
    Args:
        files: Lista de rutas de archivos PDF
        output_file: Ruta del archivo de salida
        callback_progreso: Función para actualizar progreso (current, total, message)
    """
    def actualizar_progreso(current, total, message=""):
        if callback_progreso:
            callback_progreso(current, total, message)
    
    try:
        # primero, contar total de páginas 
        actualizar_progreso(0, 1, "Analizando documentos...")

        total_paginas = 0
        docs_info = []

        for doc_path in files:
            with open(doc_path, 'rb') as f:
                reader = PdfReader(f)
                pages = len(reader.pages)
                total_paginas += pages
                docs_info.append({'path': doc_path, 'pages': pages, 'reader': None})

        if total_paginas == 0:
            actualizar_progreso(0, 1, "Error: No hay páginas para unir")
            return False

        pdf_writer = PdfWriter()                   # Crea un objeto PDFWriter
        paginas_procesadas = 0

        # Procesar cada documento
        for doc_info in docs_info:                     # Recorre los archivos PDF
            with open(doc_info['path'], 'rb') as file:     # Abre los archivos en modo de lectura binaria
                pdf_reader = PdfReader(file)       # Crea objetos PDFReader
                doc_name = doc_info['path'].split('/')[-1]

                for page_num, page in enumerate(pdf_reader.pages):
                    mensaje = f"Uniendo: {doc_name} - Página {page_num + 1}/{doc_info['pages']}"
                    actualizar_progreso(paginas_procesadas + 1, total_paginas, mensaje)

                    pdf_writer.add_page(page)
                    paginas_procesadas += 1        

                    # Mantener UI responsiva
                    if callback_progreso:
                        from PyQt6.QtWidgets import QApplication
                        QApplication.processEvents()

        actualizar_progreso(total_paginas, total_paginas, "Guardando archivo unido...") 

        with open(output_file, 'wb') as output_doc:  # crea un nuevo archivo PDF en modo binario
            pdf_writer.write(output_doc)             # Guarda las páginas en el archivo de salida
        
        actualizar_progreso(total_paginas, total_paginas, "¡Unión completada!")
        return True
    
    except Exception as e:
        print(f"Error al unir los documentos: {e}")
        if callback_progreso:
            callback_progreso(0, 1, f"Error: {str(e)}")
        return False

if __name__ == "__main__":

    INPUT_1 = 'assets/documento_A.pdf'   # Nombre del primer archivo de ejemplo.
    INPUT_2 = 'assets/documento_B.pdf'   # Nombre del segundo archivo de ejemplo.
    INPUTS = [INPUT_1, INPUT_2]          # Lista entradas a la lista.
    NAME_OUTPUT = 'resultado_Union.pdf'  # nombre de documentos unidos.

    unir_pdf(INPUTS, NAME_OUTPUT)        # Llama a la función para unir los archivos PDF

    print(f"¡Los archivos {INPUTS} se han unido correctamente en {NAME_OUTPUT}!")
