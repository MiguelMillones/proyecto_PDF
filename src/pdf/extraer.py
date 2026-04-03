"""Código para extraer páginas de un documento PDF"""
from PyPDF2 import PdfReader, PdfWriter

def extraer_paginas(pdf_input, pdf_output, paginas_a_extraer):
    """Función para extraer las páginas"""
    try:
        # Abre el archivo PDF de entrada en modo binario
        with open(pdf_input, 'rb') as file:
            pdf_reader = PdfReader(file)        # Crea un objeto de lector de PDF
            pdf_writer = PdfWriter()            # Crea un objeto de escritor de PDF

            total_page = len(pdf_reader.pages)

            for pagina_num in paginas_a_extraer:      # Recorre las páginas que se quieren extraer
                if 1 <= pagina_num <= total_page:
                    pdf_writer.add_page(pdf_reader.pages[pagina_num - 1]) # Agrega páginas al objeto
                else:
                    print('numero de pagina no se encuntra en achivo')
                    return False  # Página no existe

            # Crea un nuevo archivo PDF de salida en modo binario
            with open(pdf_output, 'wb') as output_file:
                pdf_writer.write(output_file)   # Escribe las páginas en el nuevo archivo PDF

        return True # Páginas separadas correctamente
    except Exception as e:
        print(f"Error al extraer páginas: {e}")
        return False

if __name__ == "__main__":

    PDF_INPUT = 'assets/documento_A.pdf'    # Nombre del doc PDF de entrada
    PDF_OUTPUT = 'paginas_extraidas.pdf'    # Nombre del nuevo doc PDF (páginas separadas)

    paginas_a_extraer = [1, 3, 5]           # Números de las páginas que se quieren extraer
                                            #(puedes cambiar esto según tus necesidades)
    # Llama a la función para extraer las páginas
    extraer_paginas(PDF_INPUT, PDF_OUTPUT, paginas_a_extraer)

    print(f'Se han extraido las páginas {paginas_a_extraer} en el archivo {PDF_OUTPUT}.')