"""Proyecto para foliar archivos .PDF, usando el modulo PyPDF2"""
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

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

            page_size = pagina_original.mediabox.upper_right
            w, h = pagina_original.mediabox.upper_right
            x = float(w - 37)
            y = float(h - 36)

            texto_foliacion = str(len(pdf_reader.pages)-num_pagina)

            pdf_num=canvas.Canvas("numerofolio.pdf")
            pdf_num.setPageSize(page_size)
            pdf_num.setFont("Courier",14)
            pdf_num.setFillColorRGB(0,0,0,1)
            pdf_num.drawString(x,y,texto_foliacion)
            pdf_num.save()
            #pdf_num.showPage()
            
            with open('numerofolio.pdf', 'rb') as file2:
                num_folio = PdfReader(file2)
                page_num_folio = num_folio.pages[0]
                pagina_original.merge_page(page_num_folio)
                pdf_writer.add_page(pagina_original)
            #w = len(texto_foliacion)+(12*len(texto_foliacion))
            #h = font_h+2
            #x = pagina_original.mediabox[2] - w - 37
            #y = pagina_original.mediabox[3] - h - 36
            
            #pdf_writer.add_annotation(num_pagina,numtext) #Escribe el texto como comentario

        # Abre un nuevo archivo PDF en modo de escritura binaria
        with open(archivo_salida, 'wb') as salida:
            # Escribe el contenido del objeto PDFWriter en el nuevo archivo PDF
            pdf_writer.write(salida)

if __name__ == "__main__":
    PDF_ENTRADA = "FICHAS DE TRABAJO1.pdf" # Nombre del archivo PDF a foliar.
    PDF_SALIDA = "salida.pdf"     # Nombre del archivo PDF foliado.

    foliar_pdf(PDF_ENTRADA, PDF_SALIDA)
