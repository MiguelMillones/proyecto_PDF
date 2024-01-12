"""Codigo para crear un documento PDF usando la libreria ReportLab 
y enumera las fuentes que siempre están disponibles"""
import random
from reportlab.pdfgen import canvas

# Cordenadas de ubicación de inicio de texto
X1 = 200
Y1 = 700
doc=canvas.Canvas("documento.pdf")                 # crea pdf, por defecto A4 (595.27pts,841.89pts)
for i,font in enumerate(doc.getAvailableFonts()):  # enumera y muetras las fuentes disponibles
    c = random.random()                            # valores aleatorios entre 0 y 1
    m = random.random()                            # valores aleatorios entre 0 y 1
    y = random.random()                            # valores aleatorios entre 0 y 1
    doc.setFont(font, 16)                          # tipo de letra y tamaño de texto
    doc.setFillColorRGB(c, m, y,1)                 # representar el color CMYK (C,M,Y,K)
    doc.drawString(X1, Y1, font )                  # ubicación del texto (x, y, "texto")
    doc.drawAlignedString(X1-20,Y1,f"{i+1}: ")     # alineación del texto (x, y, "texto")
    Y1=Y1-20                                       # reducir el eje Y para evitar sobre escritura

doc.save()                                         # Guardar documento
