"""Código para separar páginas de un documento PDF"""
from PyPDF2 import PdfReader, PdfWriter

def separar_paginas(input_pdf, output_pdf, separar_pag):
    """Función para separar las páginas"""
    # Abre el archivo PDF de entrada en modo binario
    with open(input_pdf, 'rb') as file:
        pdf_reader = PdfReader(file)        # Crea un objeto de lector de PDF
        pdf_writer = PdfWriter()            # Crea un objeto de escritor de PDF

        for pagina_num in separar_pag:      # Recorre las páginas que se quieren separar
            pdf_writer.add_page(pdf_reader.pages[pagina_num - 1]) # Agrega páginas al objeto

        # Crea un nuevo archivo PDF de salida en modo binario
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)   # Escribe las páginas en el nuevo archivo PDF

if __name__ == "__main__":

    PDF_INPUT = 'namePdf.pdf'               # Nombre del doc PDF de entrada
    PDF_OUTPUT = 'paginas_separadas.pdf'    # Nombre del nuevo doc PDF (páginas separadas)

    paginas_a_separar = [1, 3, 5]           # Números de las páginas que se quieren separar
                                            #(puedes cambiar esto según tus necesidades)
    # Llama a la función para separar las páginas
    separar_paginas(PDF_INPUT, PDF_OUTPUT, paginas_a_separar)

    print(f'Se han separado las páginas {paginas_a_separar} en el archivo {PDF_OUTPUT}.')
