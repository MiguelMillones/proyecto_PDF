"""Proyecto para foliar archivos .PDF, usando el modulo PyPDF2"""
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

def foliar_pdf(archivo_entrada, archivo_salida):
    """Función para foliar un archivo pdf de entrada y crear nuevo archivo PDF de salida"""
    # Abre el archivo PDF de entrada en modo de lectura binaria
    with open(archivo_entrada, 'rb') as file:
        pdf_reader = PdfReader(file) # Crea un objeto PDFReader
        pdf_writer = PdfWriter()     # Crea un objeto PDFWriter

        for num_pagina, page in enumerate(pdf_reader.pages):  # páginas del PDF de entrada
            page_origin = page                                # Obtén la página original
            page_size = page_origin.mediabox.upper_right      # Tamaño de página original
            w, h = page_size                                  # width, high original

            texto_num = str(len(pdf_reader.pages)-num_pagina) # texto de número de folio
            font_h = 16                                       # tamaño de letra
            w_num = len(texto_num)+(12*len(texto_num))        # Ancho de número (texto)
            h_num = font_h+2                                  # altura de texto

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

if __name__ == "__main__":
    PDF_ENTRADA = "FICHAS DE TRABAJO.pdf"                      # Nombre del archivo PDF a foliar.
    PDF_SALIDA = "pdf_folio.pdf"                               # Nombre del archivo PDF foliado.

    foliar_pdf(PDF_ENTRADA, PDF_SALIDA)                        # Función para foliar pdf
