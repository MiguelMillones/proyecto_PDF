
```markdown
# 📄 DocTriX — Herramienta Profesional de Gestión de Documentos PDF

**Aplicación profesional para manipulación de archivos PDF con interfaz gráfica moderna**

---

## 📌 Descripción

DocTriX es una aplicación desarrollada en Python que permite gestionar documentos PDF de manera 
profesional mediante una interfaz gráfica intuitiva y moderna. Ofrece operaciones esenciales 
para el manejo de documentos:

* ✂️ **Separar páginas** - Extrae páginas específicas de documentos PDF
* 🔗 **Unir documentos** - Combina múltiples PDF en un solo archivo
* 🔢 **Foliar documentos** - Numeración automática de páginas (soporte inverso)

### ✨ Características destacadas

- 🎨 **Interfaz moderna** - Diseñada con PyQt6 y estilos CSS personalizados
- 📊 **Barra de progreso** - Feedback visual durante operaciones largas
- 🖱️ **Drag & Drop** - Reorganización visual de documentos para unión
- 🔄 **Foliado inverso** - Numeración desde la última página hacia la primera
- 📐 **Orientación automática** - Detecta páginas horizontales/verticales
- 🚀 **Multiplataforma** - Funciona en Windows, Linux y macOS
- 📦 **Ejecutable standalone** - No requiere Python instalado

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11.0 | Lenguaje base |
| **PyQt6** | 6.4.2 | Interfaz gráfica |
| **PyPDF2** | 3.0.1 | Manipulación de PDFs |
| **ReportLab** | 4.0.8 | Generación de números de folio |
| **Pillow** | 10.2.0 | Manejo de imágenes |
| **PyInstaller** | 6.3.0 | Creación de ejecutables |

---

## 📦 Requisitos previos

- **Python 3.11.0** (recomendado estrictamente esta versión)
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

```bash
# Verificar versión de Python
python --version
# Debe mostrar: Python 3.11.0
```

---

## 📥 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/MiguelMillones/proyecto_PDF.git
cd proyecto_PDF
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv .venv

# Linux / macOS
python3 -m venv .venv
```

### 3. Activar entorno virtual

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python src/main.py
```

---

## 🚀 Uso de la aplicación

### 📄 Extraer páginas

1. Haz clic en "📂 Buscar archivo" y selecciona un PDF
2. En el campo "Páginas:", ingresa las páginas a extraer
   - **Individuales:** `1,3,5`
   - **Rangos:** `1-5`
   - **Combinación:** `1,3-5,7`
3. Haz clic en "✅ Extraer páginas"

### 🔗 Unir documentos

1. Haz clic en "📂 Seleccionar archivos" y elige múltiples PDFs
2. **Organiza el orden:**
   - Arrastra los items para reordenar
   - Usa los botones ⬆️/⬇️ para mover
   - Ordena automáticamente con A-Z/Z-A
3. Elimina archivos no deseados con 🗑️ o 🚮
4. Haz clic en "🔗 Unir documentos"

### 🔢 Foliar documentos

1. Haz clic en "📂 Buscar archivo" y selecciona un PDF
2. Ingresa el número inicial del foliado
3. Haz clic en "🔢 Foliar documento"
4. El foliado se aplica desde la última página hacia la primera

---

## 🏗️ Construcción del ejecutable

### Requisitos adicionales

```bash
pip install pyinstaller
```

### Método 1: Usando el script de construcción (Recomendado)

```bash
python build.py
```

El ejecutable se generará en la carpeta `dist/`.

### Método 2: Comando directo

#### Windows

```bash
pyinstaller --onefile --windowed --name "DocTriX" --icon "assets/icon.ico" --add-data "assets;assets" --add-data "src/pdf;pdf" --add-data "src/utils;utils" --paths "src" --hidden-import PyPDF2 --hidden-import reportlab --hidden-import PyQt6 --hidden-import pdf.extraer --hidden-import pdf.unir --hidden-import pdf.foliar --hidden-import utils.path_utils --collect-all reportlab src/main.py
```

#### Linux / macOS

```bash
pyinstaller --onefile --windowed --name "DocTriX" --add-data "assets:assets" --add-data "src/pdf:pdf" --add-data "src/utils:utils" --paths "src" --hidden-import PyPDF2 --hidden-import reportlab --hidden-import PyQt6 --hidden-import pdf.extraer --hidden-import pdf.unir --hidden-import pdf.foliar --hidden-import utils.path_utils --collect-all reportlab src/main.py
```

### Método 3: Usando archivo `.spec`

```bash
pyinstaller main.spec
```

### Resultado

```
PROYECTO_PDF/
└── dist/
    └── DocTriX.exe    # Windows
    └── DocTriX        # Linux/macOS
```

**Tamaño del ejecutable:** ~81 MB (optimizado)

---

## 📁 Estructura del proyecto

```
PROYECTO_PDF/
│
├── src/                        # Código fuente principal
│   ├── main.py                 # Punto de entrada
│   ├── pdf/                    # Módulos PDF
│   │   ├── extraer.py          # Extracción de páginas
│   │   ├── unir.py             # Unión de documentos
│   │   └── foliar.py           # Foliado de páginas
│   └── utils/                  # Utilidades
│       └── path_utils.py       # Manejo de rutas
│
├── assets/                     # Recursos
│   ├── estilos.css             # Estilos de la interfaz
│   ├── icon.ico                # Icono (Windows)
│   └── icon.png                # Icono (Linux/macOS)
│
├── build.py                    # Script de construcción
├── main.spec                   # Configuración PyInstaller
├── requirements.txt            # Dependencias
├── .gitignore                  # Archivos ignorados
└── README.md                   # Documentación
```

---

## ⚠️ Solución de problemas

### Error: `ModuleNotFoundError: No module named 'pdf'`

**Solución:** Asegúrate de ejecutar desde la raíz del proyecto:

```bash
cd PROYECTO_PDF
python src/main.py
```

### Error: `ImportError: cannot import name 'canvas' from 'reportlab.pdfgen'`

**Solución:** Reinstala ReportLab y reconstruye:

```bash
pip uninstall reportlab -y
pip install reportlab==4.0.8
pyinstaller main.spec --clean
```

### El ejecutable no se abre o da error

**Solución:** Ejecuta desde la terminal para ver el error:

```bash
dist\DocTriX.exe 2> error.log
type error.log
```

### El programa se congela durante el procesamiento

La aplicación incluye barra de progreso para operaciones largas. Si el PDF es muy grande (100+ MB), puede tardar varios minutos. La barra de progreso mostrará el avance.

---

## 🔧 Mantenimiento

### Limpiar archivos de construcción

```bash
# Windows
rmdir /s /q build dist
del *.spec

# Linux/macOS
rm -rf build dist
rm *.spec
```

### Actualizar dependencias

```bash
pip install --upgrade -r requirements.txt
```

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**.  
Consulta el archivo `LICENSE` para más detalles.

```
MIT License

Copyright (c) 2024 Miguel Millones

Permission is hereby granted, free of charge, to any person obtaining a copy
...
```

---

## 👨‍💻 Autor

**Miguel Millones**

- GitHub: [@MiguelMillones](https://github.com/MiguelMillones)
- Email: miguelmillones22@gmail.com
- Proyecto: [proyecto_PDF](https://github.com/MiguelMillones/proyecto_PDF)

---

## ⭐ Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un **Fork** del proyecto
2. Crea una rama para tu función (`git checkout -b feature/nueva-funcion`)
3. Realiza tus cambios y haz **commit** (`git commit -m 'Añadir nueva función'`)
4. Sube los cambios (`git push origin feature/nueva-funcion`)
5. Abre un **Pull Request**

---

## 📬 Contacto

- **Issues:** [GitHub Issues](https://github.com/MiguelMillones/proyecto_PDF/issues)
- **Email:** miguelmillones22@gmail.com

---

## 🙏 Agradecimientos

- PyQt6 por la excelente biblioteca de interfaz gráfica
- PyPDF2 por el manejo robusto de PDFs
- ReportLab por la generación de documentos PDF
- Comunidad de Python por el soporte continuo

---

## 📊 Estadísticas del proyecto

| Métrica | Valor |
|---------|-------|
| Versión | 2.1.0 |
| Tamaño ejecutable (Windows) | ~81 MB |
| Líneas de código | ~1,500 |
| Tiempo de desarrollo | ~3 meses |
| Lenguaje | Python 3.11.0 |

---

<div align="center">

**⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub ⭐**

*Hecho con ❤️ y Python*

</div>
```