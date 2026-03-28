"""Proyecto para foliar archivos .PDF, usando el modulo PyPDF2"""
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from copy import copy

def foliar_pdf(archivo_entrada, archivo_salida,inicio_folio):
    """Función para foliar un archivo pdf y crear nuevo archivo PDF de salida"""
    try:
        # Abre el archivo PDF de entrada en modo de lectura binaria
        with open(archivo_entrada, 'rb') as file:
            pdf_reader = PdfReader(file) # Crea un objeto PDFReader
            pdf_writer = PdfWriter()     # Crea un objeto PDFWriter

            fin_folio = len(pdf_reader.pages) + inicio_folio -1

            for _, page in enumerate(pdf_reader.pages):  # páginas del PDF de entrada
                page_origin = copy(page)                                # Obtén la página original
                page_size = page_origin.mediabox.upper_right      # Tamaño de página original
                w, h = page_size                                  # width, high original

                num_pagina =fin_folio
                texto_num = str(num_pagina)#str(len(pdf_reader.pages)-num_pagina) # texto de número de folio
                font_h = 16                                       # tamaño de letra
                #w_num = len(texto_num)+(12*len(texto_num))        # Ancho de número (texto)
                w_num = int(stringWidth(texto_num, "Times-Roman", font_h))
                h_num = font_h+2                                  # altura de texto
                fin_folio -=1
                
                # crear PDF en memoria
                packet = BytesIO()
                pdf_num = canvas.Canvas(packet)
                pdf_num.setPageSize(page_size)
                pdf_num.setFont("Times-Roman",font_h)
                pdf_num.setFillColorRGB(0,0,0)

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

                #leer pdf en memoria
                packet.seek(0)
                page_num_folio = PdfReader(packet)
                page_origin.merge_page(page_num_folio.pages[0])
                pdf_writer.add_page(page_origin)

            # Abre un nuevo archivo PDF en modo de escritura binaria
            with open(archivo_salida, 'wb') as salida:
                # Escribe el contenido del objeto PDFWriter en el nuevo archivo PDF
                pdf_writer.write(salida)
        return True
    
    except Exception as e:
        print(f"Error al foliar el documento pdf: {e}")
        return False

if __name__ == "__main__":
    PDF_ENTRADA = "assets/documento_C.pdf"             # Nombre del archivo PDF a foliar.
    PDF_SALIDA = "archivo_foliado.pdf"                 # Nombre del archivo PDF foliado.
    INICIO_FOLIO = 1000                                  # inicio de folio de abajo hacia arriba

    foliar_pdf(PDF_ENTRADA, PDF_SALIDA, INICIO_FOLIO)                        # Función para foliar pdf
    print(f'Se termino de foliar las páginas del archivo {PDF_ENTRADA}.')
