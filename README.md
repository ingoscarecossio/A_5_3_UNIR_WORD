# 📄 Combinador Profesional de Documentos Word

Aplicación web de nivel productivo en Python usando Streamlit que permite combinar múltiples documentos Word (.docx) en un solo archivo, con preservación avanzada de formato y características profesionales.

## 🚀 Características Principales

### ✨ Funcionalidades Avanzadas

- ✅ **Carga Inteligente de Documentos**
  - Carga desde carpeta (modo local)
  - Carga de archivos individuales (múltiple selección)
  - Validación automática de archivos .docx
  - Análisis automático de documentos

- ✅ **Preservación Avanzada de Formato**
  - Preservación de estilos originales
  - Mantenimiento de imágenes y tablas
  - Conservación de estructura de párrafos
  - Preservación de formato de texto

- ✅ **Opciones Profesionales**
  - Agregar portada personalizada
  - Generar índice de contenidos automático
  - Saltos de página configurables
  - Líneas separadoras opcionales
  - Numeración de documentos

- ✅ **Interfaz Profesional**
  - Diseño moderno y responsivo
  - Barra de progreso en tiempo real
  - Estadísticas detalladas
  - Vista previa del orden final
  - Información detallada de cada documento

- ✅ **Robustez y Confiabilidad**
  - Manejo avanzado de errores
  - Validación de archivos corruptos
  - Logging detallado
  - Procesamiento optimizado
  - Manejo de memoria eficiente

## 📦 Instalación

### Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clona o descarga este repositorio**

```bash
git clone <repository-url>
cd A_5_3_UNIR_WORD
```

2. **Crea un entorno virtual (recomendado)**

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

3. **Instala las dependencias**

```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Inicio Rápido

1. **Ejecuta la aplicación**

```bash
streamlit run app.py
```

2. **La aplicación se abrirá automáticamente** en tu navegador (normalmente en `http://localhost:8501`)

### Guía de Uso Detallada

#### 1. Cargar Documentos

**Opción A: Desde Carpeta (Local)**
- Selecciona "📁 Desde carpeta (local)"
- Ingresa la ruta completa de la carpeta que contiene los archivos .docx
- La aplicación cargará y validará automáticamente todos los archivos .docx

**Opción B: Subir Archivos**
- Selecciona "📤 Subir archivos"
- Haz clic en "Browse files" y selecciona uno o varios archivos .docx
- Puedes seleccionar múltiples archivos a la vez

#### 2. Reordenar Documentos

- Usa los botones **↑** y **↓** para mover documentos arriba o abajo
- Usa el botón **❌** para eliminar documentos de la lista
- El orden se actualiza en tiempo real

#### 3. Configurar Opciones

En la barra lateral, puedes configurar:

- **Opciones de Combinación**:
  - Agregar salto de página entre documentos
  - Agregar línea separadora
  - Numerar documentos
  - Preservar estilos originales

- **Elementos Adicionales**:
  - Agregar portada personalizada
  - Agregar índice de contenidos

- **Opciones Avanzadas**:
  - Detener en caso de error
  - Analizar documentos automáticamente

#### 4. Combinar y Descargar

1. Ingresa el nombre del archivo final
2. Haz clic en "🧩 Combinar Documentos"
3. Espera a que se complete el proceso (verás una barra de progreso)
4. Descarga el archivo combinado usando el botón "💾 Descargar Documento Combinado"

## 📊 Características Técnicas

### Arquitectura

- **Código Modular**: Organizado en clases y funciones reutilizables
- **Manejo de Errores**: Sistema robusto de validación y manejo de excepciones
- **Optimización**: Procesamiento eficiente de memoria para archivos grandes
- **Logging**: Sistema de logging detallado para debugging

### Clases Principales

- **`DocumentInfo`**: Almacena y analiza información de documentos
- **`DocumentMerger`**: Clase principal para combinar documentos con opciones avanzadas

### Funciones de Utilidad

- Validación de archivos .docx
- Formateo de tamaños de archivo
- Análisis de documentos
- Preservación de estilos

## ⚠️ Limitaciones Conocidas

1. **Headers y Footers**: Los headers y footers complejos pueden no preservarse perfectamente
2. **Secciones**: Las secciones con diferentes configuraciones pueden requerir ajuste manual
3. **Numeraciones**: Las listas numeradas complejas pueden necesitar revisión
4. **Estilos Duplicados**: Estilos con el mismo nombre pero diferente definición pueden mezclarse

## 💡 Recomendaciones

- ✅ Revisa siempre el documento combinado en Word antes de usarlo en producción
- ✅ Guarda copias de los documentos originales
- ✅ Para documentos muy complejos, considera usar herramientas especializadas
- ✅ Cierra los archivos .docx en Word antes de combinarlos
- ✅ Verifica que los archivos no estén corruptos

## 🐛 Solución de Problemas

### Error: "No se encontraron archivos .docx"
- Verifica que la ruta de la carpeta sea correcta
- Asegúrate de que los archivos tengan la extensión .docx (no .doc)

### Error: "Archivo inválido"
- El archivo puede estar corrupto
- Verifica que el archivo no esté abierto en otro programa
- Intenta abrir el archivo en Word para verificar que esté intacto

### Error: "Error al combinar documentos"
- Verifica que todos los archivos sean válidos
- Revisa los logs para más detalles
- Intenta combinar menos documentos a la vez

### La aplicación es lenta
- Reduce el número de documentos a combinar
- Desactiva el análisis automático si no es necesario
- Cierra otras aplicaciones que consuman memoria

## 📝 Changelog

### Versión 2.0 (Actual)
- ✨ Interfaz completamente rediseñada
- ✨ Sistema de análisis automático de documentos
- ✨ Preservación avanzada de estilos
- ✨ Opciones de portada e índice
- ✨ Barra de progreso en tiempo real
- ✨ Estadísticas detalladas
- ✨ Manejo robusto de errores
- ✨ Logging avanzado
- ✨ Validación de archivos mejorada

### Versión 1.0
- Funcionalidad básica de combinación
- Interfaz simple
- Opciones básicas

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso libre.

## 👨‍💻 Autor

Desarrollado para uso profesional en entornos de producción.

## 🙏 Agradecimientos

- Streamlit por la excelente plataforma
- python-docx por la biblioteca de manipulación de Word
- La comunidad de código abierto

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o consulta la documentación.
