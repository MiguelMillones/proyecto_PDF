"""Proyecto para foliar archivos .PDF, usando el modulo PyPDF2"""
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from copy import copy
from typing import Optional, Callable


def foliar_pdf(archivo_entrada, archivo_salida, inicio_folio,
               callback_progreso: Optional[Callable] = None):
    """
    Foliar PDF desde la última página hacia la primera
    
    Args:
        archivo_entrada: Ruta del PDF de entrada
        archivo_salida: Ruta del PDF de salida
        inicio_folio: Número inicial para el foliado
        callback_progreso: Función para actualizar progreso (current, total, message)
    """
    def actualizar_progreso(current, total, message=""):
        if callback_progreso:
            callback_progreso(current, total, message)

    try:
        actualizar_progreso(0, 1, "Abriendo archivo PDF...")

        # Abre el archivo PDF de entrada en modo de lectura binaria
        with open(archivo_entrada, 'rb') as file:
            pdf_reader = PdfReader(file) # Crea un objeto PDFReader
            pdf_writer = PdfWriter()     # Crea un objeto PDFWriter
            total_pages = len(pdf_reader.pages)

            actualizar_progreso(0, total_pages, f"Iniciando foliado de {total_pages} páginas...")

            # Generar números de folio (de abajo hacia arriba)
            folios = list(range(inicio_folio, inicio_folio + total_pages))[::-1]

            for idx, page in enumerate(pdf_reader.pages):  # páginas del PDF de entrada
                num_pagina = folios[idx]
                mensaje = f"Foliando página {idx + 1}/{total_pages} - Número: {num_pagina}"
                actualizar_progreso(idx + 1, total_pages, mensaje)

                page_origin = copy(page)                                # Obtén la página original
                page_size = page_origin.mediabox.upper_right      # Tamaño de página original
                w, h = page_size                                  # width, high original

                texto_num = str(num_pagina)
                font_h = 16                                       # tamaño de letra
                w_num = int(stringWidth(texto_num, "Times-Roman", font_h))
                h_num = font_h + 2                                  # altura de texto
                
                # crear PDF en memoria
                packet = BytesIO()
                pdf_num = canvas.Canvas(packet)
                pdf_num.setPageSize(page_size)
                pdf_num.setFont("Times-Roman",font_h)
                pdf_num.setFillColorRGB(0,0,0)

                if w>h:            # Página horizontal
                    x = float(w - 37 - h_num)                     # calcula coordenada X
                    y = float(36 + w_num)                         # calcula coordenada y
                    pdf_num.translate(x,y)                        # traslada eje cartesiano a (x,y)
                    pdf_num.rotate(-90)                           # rotar para posicionar el texto
                    pdf_num.drawString(0,0,texto_num)             # inserta el texto (número de folio)
                else:              # Página vertical
                    x = float(w - 37 - w_num)                     # calcula coordenada X
                    y = float(h - 36 - h_num)                     # calcula coordenada y
                    pdf_num.drawString(x,y,texto_num)             # inserta el texto (número de folio)
                
                pdf_num.save()                                    # guarda pdf con el texto

                #leer pdf en memoria y fusionar capas
                packet.seek(0)
                page_num_folio = PdfReader(packet)
                page_origin.merge_page(page_num_folio.pages[0])
                pdf_writer.add_page(page_origin)

                # Mantener UI responsiva
                if callback_progreso:
                    from PyQt6.QtWidgets import QApplication
                    QApplication.processEvents()
            
            actualizar_progreso(total_pages, total_pages, "Guardando archivo foliado...")

            # Abre un nuevo archivo PDF en modo de escritura binaria
            with open(archivo_salida, 'wb') as salida:
                # Escribe el contenido del objeto PDFWriter en el nuevo archivo PDF
                pdf_writer.write(salida)

        actualizar_progreso(1, 1, "¡Foliado completado!")    
        return True
    
    except Exception as e:
        print(f"Error al foliar el documento pdf: {e}")
        if callback_progreso:
            callback_progreso(0, 1, f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    PDF_ENTRADA = "assets/documento_C.pdf"             # Nombre del archivo PDF a foliar.
    PDF_SALIDA = "archivo_foliado.pdf"                 # Nombre del archivo PDF foliado.
    INICIO_FOLIO = 1000                                  # inicio de folio de abajo hacia arriba

    foliar_pdf(PDF_ENTRADA, PDF_SALIDA, INICIO_FOLIO)                        # Función para foliar pdf
    print(f'Se termino de foliar las páginas del archivo {PDF_ENTRADA}.')
