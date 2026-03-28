"""Código para unir documentos PDF"""
from PyPDF2 import PdfReader, PdfWriter

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

if __name__ == "__main__":

    INPUT_1 = 'assets/documento_A.pdf'   # Nombre del primer archivo de ejemplo.
    INPUT_2 = 'assets/documento_B.pdf'   # Nombre del segundo archivo de ejemplo.
    INPUTS = [INPUT_1, INPUT_2]          # Lista entradas a la lista.
    NAME_OUTPUT = 'resultado_Union.pdf'  # nombre de documentos unidos.

    unir_pdf(INPUTS, NAME_OUTPUT)        # Llama a la función para unir los archivos PDF

    print(f"¡Los archivos {INPUTS} se han unido correctamente en {NAME_OUTPUT}!")
