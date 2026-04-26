"""Código para extraer páginas de un documento PDF con barra de progreso"""
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional, Callable

def extraer_paginas(pdf_input, pdf_output, paginas_a_extraer, 
                    callback_progreso: Optional[Callable] = None):
    """
    Extraer páginas de un PDF

    Args:
        pdf_input: Ruta del PDF de entrada
        pdf_output: Ruta del PDF de salida
        paginas_a_extraer: Lista de números de página
        callback_progreso: Función para actualizar progreso (current, total, message)
    """
    def actualizar_progreso(current, total, message=""):
        if callback_progreso:
            callback_progreso(current, total, message)

    try:
        actualizar_progreso(0, len(paginas_a_extraer), "Abriendo archivo PDF...")
        
        # Abre el archivo PDF de entrada en modo binario
        with open(pdf_input, 'rb') as file:
            pdf_reader = PdfReader(file)        # Crea un objeto de lector de PDF
            pdf_writer = PdfWriter()            # Crea un objeto de escritor de PDF
            total_page = len(pdf_reader.pages)

            actualizar_progreso(0, len(paginas_a_extraer), "Verificando páginas...")

            # Validar páginas primero
            paginas_validas = []
            for pagina_num in paginas_a_extraer:
                if 1 <= pagina_num <= total_page:
                    paginas_validas.append(pagina_num)
                else:
                    print(f"Página {pagina_num} no existe en el documento")
                    return False
                
            if not paginas_validas:
                return False
            
            # Extraer páginas

            for idx, pagina_num in enumerate(paginas_validas):      # Recorre las páginas validas
                mensaje = f"Extrayendo página {pagina_num} de {total_page}"
                actualizar_progreso(idx + 1, len(paginas_validas), mensaje)
                pdf_writer.add_page(pdf_reader.pages[pagina_num - 1]) # Agrega páginas al objeto

                # pequeña pausa para mantener UI responsiva
                if callback_progreso:
                    from PyQt6.QtWidgets import QApplication
                    QApplication.processEvents()

            actualizar_progreso(len(paginas_validas), len(paginas_validas), "Guardando archivo...")
            
            # Crea un nuevo archivo PDF de salida en modo binario
            with open(pdf_output, 'wb') as output_file:
                pdf_writer.write(output_file)   # Escribe las páginas en el nuevo archivo PDF

        actualizar_progreso(len(paginas_validas), len(paginas_validas), "!Completado!")
        return True # Páginas separadas correctamente
    
    except Exception as e:
        print(f"Error al extraer páginas: {e}")
        if callback_progreso:
            callback_progreso(0, 1, f"Error: {str(e)}")
        return False

if __name__ == "__main__":

    PDF_INPUT = 'assets/documento_A.pdf'    # Nombre del doc PDF de entrada
    PDF_OUTPUT = 'paginas_extraidas.pdf'    # Nombre del nuevo doc PDF (páginas separadas)

    paginas_a_extraer = [1, 3, 5]           # Números de las páginas que se quieren extraer
                                            #(puedes cambiar esto según tus necesidades)
    # Llama a la función para extraer las páginas
    extraer_paginas(PDF_INPUT, PDF_OUTPUT, paginas_a_extraer)

    print(f'Se han extraido las páginas {paginas_a_extraer} en el archivo {PDF_OUTPUT}.')