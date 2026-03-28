# 📄 PDF-SUF — Herramienta de Gestión de Documentos PDF

Aplicación desarrollada en Python para la manipulación de archivos PDF mediante una interfaz gráfica intuitiva. Permite realizar operaciones esenciales como:

* ✂️ Separar páginas
* 🔗 Unir múltiples documentos
* 🔢 Foliar documentos (numeración automática)

---

## 🚀 Características

* Interfaz gráfica desarrollada con PyQt6
* Procesamiento eficiente de PDFs con PyPDF2
* Generación dinámica de contenido con ReportLab
* Soporte para foliado inverso (de abajo hacia arriba)
* Validación de entradas para evitar errores del usuario
* Código modular y escalable

---

## 🛠️ Tecnologías utilizadas

* Python 3.11.0
* PyPDF2
* ReportLab
* PyQt6

---

## 📦 Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

* Python **3.11.0**
  👉 Se recomienda usar esta versión para evitar incompatibilidades con librerías.

Puedes verificar tu versión con:

```bash
python --version
```

---

## 📥 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/MiguelMillones/proyecto_PDF.git
```

---

### 2. Ingresar al proyecto

```bash
cd proyecto_PDF
```

---

### 3. Crear entorno virtual

```bash
python -3.11 -m venv .venv
```

---

### 4. Activar entorno virtual

#### En Windows:

```bash
.venv\Scripts\activate
```

#### En Linux / macOS:

```bash
source .venv/bin/activate
```

---

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

Para ejecutar la aplicación:

```bash
python main.py
```

---

## 🧩 Funcionalidades

### ✂️ Separar páginas

Permite extraer páginas específicas de un documento PDF ingresando los números separados por comas.

---

### 🔗 Unir documentos

Permite seleccionar múltiples archivos PDF y combinarlos en un solo documento.

---

### 🔢 Foliar documentos

Agrega numeración automática a cada página:

* Soporta foliado normal o inverso
* Posicionamiento automático según orientación
* Configuración de fuente y tamaño

---

## 📁 Estructura del proyecto

```bash
proyecto_PDF/
│
├── src/                # Código fuente principal
├── assets/             # Archivos de prueba y recursos
├── requirements.txt    # Dependencias del proyecto
├── README.md           # Documentación
└── .gitignore
```

---

## ⚠️ Consideraciones

* El proyecto está optimizado para Python 3.11.0
* Versiones más recientes pueden generar incompatibilidades con algunas librerías
* Se recomienda usar entorno virtual para evitar conflictos

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

## 👨‍💻 Autor

**Miguel Millones**

Proyecto desarrollado como herramienta práctica para gestión documental en PDF.

---

## ⭐ Contribuciones

Las contribuciones son bienvenidas.
Puedes hacer un fork del repositorio y enviar un pull request.

---

## 📬 Contacto

Si tienes dudas o sugerencias, puedes abrir un issue en el repositorio.

---

💡 *Este proyecto puede evolucionar hacia una aplicación profesional instalable o una librería reutilizable.*


