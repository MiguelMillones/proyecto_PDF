"""Proyecto para foliar archivos .PDF, usando el modulo PyPDF2"""
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder

def foliar_pdf(archivo_entrada, archivo_salida):
    """Función para foliar un archivo pdf de entrada y crear nuevo archivo PDF de salida"""
    # Abre el archivo PDF de entrada en modo de lectura binaria
    with open(archivo_entrada, 'rb') as file:
        pdf_reader = PdfReader(file) # Crea un objeto PDFReader

        pdf_writer = PdfWriter()     # Crea un objeto PDFWriter

        # Recorre todas las páginas del PDF de entrada
        for num_pagina, page in enumerate(pdf_reader.pages):
            # Obtén la página original
            pagina_original = page

            pdf_writer.add_page(pagina_original)

            texto_foliacion = str(len(pdf_reader.pages)-num_pagina)
            font_h = 14
            w = len(texto_foliacion)+(12*len(texto_foliacion))
            h = font_h+2
            x = pagina_original.mediabox[2] - w - 37
            y = pagina_original.mediabox[3] - h - 36

            numtext = AnnotationBuilder.free_text(
                texto_foliacion,
                rect=(x, y, pagina_original.mediabox[2]-36, pagina_original.mediabox[3]-36),
                font= "Arial",
                bold = True,
                italic= True,
                font_size= str(font_h)+"pt",
                font_color= "000000",
                border_color= "ffffff",
                background_color= "ffffff",
            )

            pdf_writer.add_annotation(num_pagina,numtext) #Escribe el texto como comentario

        # Abre un nuevo archivo PDF en modo de escritura binaria
        with open(archivo_salida, 'wb') as salida:
            # Escribe el contenido del objeto PDFWriter en el nuevo archivo PDF
            pdf_writer.write(salida)

if __name__ == "__main__":
    PDF_ENTRADA = "documento.pdf" # Nombre del archivo PDF a foliar.
    PDF_SALIDA = "salida.pdf"     # Nombre del archivo PDF foliado.

    foliar_pdf(PDF_ENTRADA, PDF_SALIDA)
