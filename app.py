"""
Aplicación Streamlit Profesional para Combinar Documentos Word
Versión: 2.1 - Nivel Productivo Mejorado
- Eliminación inteligente de páginas en blanco
- Lógica robusta de combinación de documentos
- Preservación avanzada de formato sin elementos innecesarios
"""

import os
import logging
from io import BytesIO
from copy import deepcopy
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import traceback

import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de página
st.set_page_config(
    page_title="Combinador Profesional de Documentos Word",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS PROFESIONALES
# ============================================================================

st.markdown("""
    <style>
    /* Estilos generales */
    .main {
        padding-top: 2rem;
    }
    
    /* Cards de documentos */
    .document-card {
        padding: 1.2rem;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        margin: 0.75rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .document-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    /* Botones personalizados */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
    }
    
    /* Métricas */
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    
    /* Progress bar */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Alertas mejoradas */
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        padding-top: 3rem;
    }
    
    /* Títulos */
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    h2 {
        color: #34495e;
        font-weight: 600;
        border-bottom: 3px solid #4CAF50;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #5a6c7d;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CLASES Y FUNCIONES DE UTILIDAD
# ============================================================================

class DocumentInfo:
    """Clase para almacenar información de un documento"""
    def __init__(self, name: str, source_type: str, source, size: float = 0):
        self.name = name
        self.source_type = source_type
        self.source = source
        self.size = size
        self.paragraphs = 0
        self.tables = 0
        self.images = 0
        self.pages_estimate = 0
        self.is_valid = True
        self.error_message = None
        self._analyzed = False
    
    def analyze(self):
        """Analiza el documento para obtener información detallada"""
        if self._analyzed:
            return
        
        try:
            if self.source_type == "path":
                doc = Document(self.source)
            else:
                self.source.seek(0)
                doc = Document(self.source)
                self.source.seek(0)
            
            self.paragraphs = len(doc.paragraphs)
            self.tables = len(doc.tables)
            
            # Contar imágenes (aproximado)
            self.images = sum(1 for p in doc.paragraphs for r in p.runs if r._element.xpath('.//a:blip'))
            
            # Estimar páginas (aproximado: 50 párrafos = 1 página)
            self.pages_estimate = max(1, self.paragraphs // 50)
            
            self.is_valid = True
            self._analyzed = True
            
        except Exception as e:
            self.is_valid = False
            self.error_message = str(e)
            logger.error(f"Error analizando {self.name}: {e}")
            self._analyzed = True

class DocumentMerger:
    """Clase profesional para combinar documentos Word con lógica robusta"""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.stats = {
            'total_docs': 0,
            'total_paragraphs': 0,
            'total_tables': 0,
            'total_images': 0,
            'processing_time': 0
        }
    
    def _update_progress(self, current: int, total: int, message: str = ""):
        """Actualiza la barra de progreso"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def _has_real_content(self, doc: Document) -> bool:
        """Verifica si el documento tiene contenido real (no solo párrafos vacíos)"""
        if len(doc.paragraphs) == 0 and len(doc.tables) == 0:
            return False
        
        # Verificar si hay párrafos con texto real
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:  # Si hay texto, hay contenido
                return True
        
        # Verificar si hay tablas
        if len(doc.tables) > 0:
            return True
        
        return False
    
    def _get_last_meaningful_element(self, doc: Document):
        """Obtiene el último elemento con contenido real del documento"""
        # Buscar desde el final hacia atrás
        for element in reversed(doc.element.body):
            # Verificar si es un párrafo con contenido
            if element.tag.endswith('p'):
                para = element
                text = ''.join(node.text for node in para.iter() if node.text)
                if text.strip():
                    return element
            # Si es una tabla, es contenido
            elif element.tag.endswith('tbl'):
                return element
        return None
    
    def _clean_empty_paragraphs_at_end(self, doc: Document):
        """Elimina párrafos vacíos al final del documento de forma robusta"""
        if len(doc.paragraphs) == 0:
            return
        
        # Buscar párrafos vacíos al final y eliminarlos
        removed = True
        while removed and len(doc.paragraphs) > 0:
            removed = False
            last_para = doc.paragraphs[-1]
            text = last_para.text.strip()
            
            # Verificar si tiene saltos de página o formato especial
            has_special_formatting = False
            for run in last_para.runs:
                # Verificar saltos de página
                if run._element.xpath('.//w:br[@w:type="page"]'):
                    has_special_formatting = True
                    break
                # Verificar si tiene formato (bold, italic, etc.) sin texto
                if run.bold or run.italic or run.underline:
                    has_special_formatting = True
                    break
            
            # Si el párrafo está completamente vacío y no tiene formato especial, eliminarlo
            if not text and not has_special_formatting and len(last_para.runs) == 0:
                try:
                    p = last_para._element
                    p.getparent().remove(p)
                    removed = True
                except:
                    break
            elif not text and not has_special_formatting:
                # Párrafo con runs pero sin texto, verificar si son solo espacios
                all_empty = True
                for run in last_para.runs:
                    if run.text and run.text.strip():
                        all_empty = False
                        break
                
                if all_empty:
                    try:
                        p = last_para._element
                        p.getparent().remove(p)
                        removed = True
                    except:
                        break
                else:
                    break
            else:
                break
    
    def _append_document(
        self,
        master: Document,
        source: Document,
        doc_number: int,
        options: Dict
    ):
        """Agrega un documento al documento maestro con lógica robusta"""
        
        # Verificar si el documento fuente tiene contenido
        if not self._has_real_content(source):
            logger.warning(f"Documento {doc_number} está vacío, se omite")
            return
        
        # Limpiar párrafos vacíos al final del documento maestro antes de agregar
        self._clean_empty_paragraphs_at_end(master)
        
        # Verificar si el documento maestro tiene contenido real
        master_has_content = self._has_real_content(master)
        
        # Agregar salto de página solo si:
        # 1. Está habilitado en opciones
        # 2. El documento maestro tiene contenido real
        # 3. El documento fuente tiene contenido real
        if options.get('add_page_break', False) and master_has_content:
            # Agregar salto de página de forma inteligente
            # Solo si el último elemento no es ya un salto de página
            last_element = self._get_last_meaningful_element(master)
            if last_element is not None:
                # Verificar si el último párrafo ya tiene salto de página
                last_para = None
                if len(master.paragraphs) > 0:
                    last_para = master.paragraphs[-1]
                    has_existing_break = False
                    for run in last_para.runs:
                        if run._element.xpath('.//w:br[@w:type="page"]'):
                            has_existing_break = True
                            break
                    
                    if not has_existing_break:
                        master.add_page_break()
                else:
                    master.add_page_break()
            else:
                # Si no hay contenido previo, no agregar salto
                pass
        
        # Agregar encabezado de documento si está habilitado
        if options.get('number_documents', False):
            header_para = master.add_paragraph()
            header_run = header_para.add_run(f"Documento {doc_number}: {options.get('current_doc_name', '')}")
            header_run.bold = True
            header_run.font.size = Pt(14)
            header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Agregar separador si está habilitado
        if options.get('add_separator', False):
            sep_para = master.add_paragraph()
            sep_run = sep_para.add_run("─" * 80)
            sep_run.font.size = Pt(8)
            sep_run.font.color.rgb = RGBColor(128, 128, 128)
            sep_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Copiar elementos del body de forma inteligente
        # Filtrar elementos vacíos al inicio del documento fuente
        source_elements = list(source.element.body)
        
        # Saltar párrafos vacíos al inicio del documento fuente
        start_idx = 0
        for idx, element in enumerate(source_elements):
            if element.tag.endswith('p'):
                text = ''.join(node.text for node in element.iter() if node.text)
                if text.strip():
                    start_idx = idx
                    break
            elif element.tag.endswith('tbl'):
                start_idx = idx
                break
        
        # Copiar elementos desde el primer elemento con contenido
        # Filtrar párrafos vacíos intermedios pero mantener estructura
        elements_to_add = []
        for element in source_elements[start_idx:]:
            if element.tag.endswith('p'):
                text = ''.join(node.text for node in element.iter() if node.text)
                # Verificar si tiene saltos de página o formato especial
                has_break = False
                for node in element.iter():
                    if node.tag.endswith('br'):
                        break_type = node.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type')
                        if break_type == 'page':
                            has_break = True
                            break
                
                # Si está vacío pero no es el último y no tiene formato especial, omitirlo
                if not text.strip() and not has_break and element != source_elements[-1]:
                    continue
            
            elements_to_add.append(element)
        
        # Copiar elementos filtrados
        for element in elements_to_add:
            master.element.body.append(deepcopy(element))
        
        # Limpiar párrafos vacíos al final después de agregar
        self._clean_empty_paragraphs_at_end(master)
        
        # Actualizar estadísticas
        self.stats['total_paragraphs'] += len([p for p in source.paragraphs if p.text.strip()])
        self.stats['total_tables'] += len(source.tables)
    
    def merge_documents(
        self,
        documents: List[DocumentInfo],
        options: Dict
    ) -> Tuple[bytes, Dict]:
        """
        Combina múltiples documentos en uno solo
        
        Args:
            documents: Lista de DocumentInfo ordenados
            options: Diccionario con opciones de combinación
        
        Returns:
            Tupla con (bytes del documento, estadísticas)
        """
        start_time = datetime.now()
        
        if not documents:
            raise ValueError("No hay documentos para combinar")
        
        self.stats['total_docs'] = len(documents)
        
        try:
            # Cargar el primer documento como base
            self._update_progress(0, len(documents), "Cargando documento base...")
            
            first_doc_info = documents[0]
            if first_doc_info.source_type == "path":
                master = Document(first_doc_info.source)
            else:
                first_doc_info.source.seek(0)
                master = Document(first_doc_info.source)
                first_doc_info.source.seek(0)
            
            # Agregar portada si está habilitado
            if options.get('add_cover_page', False):
                self._add_cover_page(master, options)
            
            # Procesar documentos restantes
            for idx, doc_info in enumerate(documents[1:], start=2):
                self._update_progress(
                    idx - 1,
                    len(documents),
                    f"Procesando: {doc_info.name}..."
                )
                
                try:
                    if doc_info.source_type == "path":
                        source_doc = Document(doc_info.source)
                    else:
                        doc_info.source.seek(0)
                        source_doc = Document(doc_info.source)
                        doc_info.source.seek(0)
                    
                    options['current_doc_name'] = doc_info.name
                    self._append_document(master, source_doc, idx, options)
                    
                except Exception as e:
                    logger.error(f"Error procesando {doc_info.name}: {e}")
                    if options.get('stop_on_error', False):
                        raise
                    # Continuar con el siguiente documento
                    continue
            
            # Agregar índice si está habilitado
            if options.get('add_table_of_contents', False):
                self._add_table_of_contents(master, documents)
            
            # Guardar en memoria
            self._update_progress(len(documents), len(documents), "Guardando documento final...")
            output = BytesIO()
            master.save(output)
            output.seek(0)
            result_bytes = output.read()
            
            # Calcular tiempo de procesamiento
            end_time = datetime.now()
            self.stats['processing_time'] = (end_time - start_time).total_seconds()
            
            return result_bytes, self.stats
            
        except Exception as e:
            logger.error(f"Error en merge_documents: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _add_cover_page(self, doc: Document, options: Dict):
        """Agrega una portada al documento de forma profesional"""
        # Insertar portada al inicio del documento
        if len(doc.paragraphs) > 0:
            # Insertar antes del primer párrafo
            first_para = doc.paragraphs[0]
            first_para.insert_paragraph_before()
        
        # Título principal
        title = doc.add_heading(options.get('cover_title', 'Documentos Combinados'), 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Subtítulo
        subtitle_text = options.get('cover_subtitle', '') or f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}'
        if subtitle_text:
            subtitle = doc.add_paragraph(subtitle_text)
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if len(subtitle.runs) > 0:
                subtitle.runs[0].font.size = Pt(12)
                subtitle.runs[0].font.italic = True
        
        # Información adicional
        if options.get('cover_info', ''):
            info = doc.add_paragraph(options['cover_info'])
            info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Salto de página después de la portada solo si hay contenido después
        if self._has_real_content(doc):
            doc.add_page_break()
    
    def _add_table_of_contents(self, doc: Document, documents: List[DocumentInfo]):
        """Agrega un índice de contenidos de forma profesional"""
        # Limpiar párrafos vacíos al final antes de agregar índice
        self._clean_empty_paragraphs_at_end(doc)
        
        # Agregar salto de página solo si hay contenido previo
        if self._has_real_content(doc):
            doc.add_page_break()
        
        # Título del índice
        toc_heading = doc.add_heading('Índice de Contenidos', 1)
        toc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Agregar espacio
        doc.add_paragraph()
        
        # Lista de documentos
        for idx, doc_info in enumerate(documents, 1):
            doc.add_paragraph(f"{idx}. {doc_info.name}", style='List Number')
        
        # Salto de página después del índice solo si hay contenido después
        # (aunque normalmente siempre habrá, es mejor verificar)
        doc.add_page_break()

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def format_file_size(size_bytes: float) -> str:
    """Formatea el tamaño del archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_file_size(file_path_or_obj) -> float:
    """Obtiene el tamaño del archivo en bytes"""
    try:
        if isinstance(file_path_or_obj, str):
            return os.path.getsize(file_path_or_obj)
        else:
            file_path_or_obj.seek(0, 2)
            size = file_path_or_obj.tell()
            file_path_or_obj.seek(0)
            return size
    except:
        return 0

def validate_docx_file(file_path_or_obj) -> Tuple[bool, Optional[str]]:
    """Valida que un archivo sea un .docx válido"""
    try:
        if isinstance(file_path_or_obj, str):
            doc = Document(file_path_or_obj)
        else:
            file_path_or_obj.seek(0)
            doc = Document(file_path_or_obj)
            file_path_or_obj.seek(0)
        return True, None
    except Exception as e:
        return False, str(e)

def list_docx_in_folder(folder_path: str) -> List[str]:
    """Lista todos los archivos .docx válidos en una carpeta"""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    
    files = []
    for name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, name)
        if (name.lower().endswith(".docx") and 
            not name.startswith("~$") and 
            os.path.isfile(full_path)):
            files.append(full_path)
    
    return sorted(files)

# ============================================================================
# INICIALIZACIÓN DE SESIÓN
# ============================================================================

if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'doc_sources' not in st.session_state:
    st.session_state.doc_sources = {}
if 'merged_bytes' not in st.session_state:
    st.session_state.merged_bytes = None
if 'merge_stats' not in st.session_state:
    st.session_state.merge_stats = None

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

# Título principal
st.title("📄 Combinador Profesional de Documentos Word")
st.markdown("**Versión 2.1 - Nivel Productivo Mejorado** | Combina múltiples documentos Word sin páginas en blanco innecesarias")

# Sidebar con opciones avanzadas
with st.sidebar:
    st.header("⚙️ Configuración Avanzada")
    
    st.subheader("📋 Opciones de Combinación")
    add_page_breaks = st.checkbox("Agregar salto de página entre documentos", value=True)
    add_separator = st.checkbox("Agregar línea separadora", value=False)
    number_documents = st.checkbox("Numerar documentos", value=False)
    preserve_styles = st.checkbox("Preservar estilos originales", value=True)
    
    st.divider()
    
    st.subheader("📑 Elementos Adicionales")
    add_cover_page = st.checkbox("Agregar portada", value=False)
    if add_cover_page:
        cover_title = st.text_input("Título de portada", value="Documentos Combinados")
        cover_subtitle = st.text_input("Subtítulo", value="")
        cover_info = st.text_area("Información adicional", value="")
    
    add_table_of_contents = st.checkbox("Agregar índice de contenidos", value=False)
    
    st.divider()
    
    st.subheader("🔧 Opciones Avanzadas")
    stop_on_error = st.checkbox("Detener en caso de error", value=False)
    auto_analyze = st.checkbox("Analizar documentos automáticamente", value=True)
    
    st.divider()
    
    st.markdown("### 📊 Estadísticas")
    if st.session_state.merge_stats:
        stats = st.session_state.merge_stats
        st.metric("Documentos procesados", stats.get('total_docs', 0))
        st.metric("Párrafos totales", stats.get('total_paragraphs', 0))
        st.metric("Tablas totales", stats.get('total_tables', 0))
        st.metric("Tiempo de procesamiento", f"{stats.get('processing_time', 0):.2f}s")

# Sección de carga de documentos
st.header("📂 Cargar Documentos")

col1, col2 = st.columns([1, 1])

with col1:
    mode = st.radio(
        "Método de carga:",
        ["📁 Desde carpeta (local)", "📤 Subir archivos"],
        horizontal=False
    )

with col2:
    if mode == "📁 Desde carpeta (local)":
        st.info("ℹ️ **Nota**: Esta opción solo funciona en ejecución local. En Streamlit Cloud usa 'Subir archivos'.")
        folder = st.text_input(
            "Ruta de la carpeta",
            placeholder=r"C:\Users\...\Documentos",
            help="Ingresa la ruta completa de la carpeta (solo funciona localmente)"
        )
    else:
        uploaded = st.file_uploader(
            "Selecciona archivos .docx",
            type=["docx"],
            accept_multiple_files=True,
            help="Puedes seleccionar múltiples archivos"
        )

# Procesar carga de documentos
docs_info = []
doc_sources = {}

if mode == "📁 Desde carpeta (local)":
    if folder:
        paths = list_docx_in_folder(folder)
        if not paths:
            st.warning("⚠️ No se encontraron archivos .docx en esa carpeta")
        else:
            with st.spinner("Validando archivos..."):
                for path in paths:
                    name = os.path.basename(path)
                    is_valid, error = validate_docx_file(path)
                    
                    if is_valid:
                        size = get_file_size(path)
                        doc_info = DocumentInfo(name, "path", path, size)
                        
                        if auto_analyze:
                            doc_info.analyze()
                        
                        docs_info.append(doc_info)
                        doc_sources[name] = ("path", path)
                    else:
                        st.warning(f"⚠️ Archivo inválido: {name} - {error}")
            
            if docs_info:
                st.success(f"✅ {len(docs_info)} archivo(s) válido(s) cargado(s)")
else:
    if uploaded:
        with st.spinner("Validando archivos..."):
            for f in uploaded:
                is_valid, error = validate_docx_file(f)
                
                if is_valid:
                    size = get_file_size(f)
                    doc_info = DocumentInfo(f.name, "upload", f, size)
                    
                    if auto_analyze:
                        doc_info.analyze()
                    
                    docs_info.append(doc_info)
                    doc_sources[f.name] = ("upload", f)
                else:
                    st.warning(f"⚠️ Archivo inválido: {f.name} - {error}")
        
        if docs_info:
            st.success(f"✅ {len(docs_info)} archivo(s) válido(s) cargado(s)")

# Actualizar estado de sesión
st.session_state.documents = docs_info
st.session_state.doc_sources = doc_sources

if not docs_info:
    st.info("👆 Por favor, carga algunos documentos para comenzar")
    st.stop()

# Sección de visualización
st.header("📋 Documentos Cargados")

# Mostrar resumen
col1, col2, col3, col4 = st.columns(4)
total_size = sum(d.size for d in docs_info)
total_paragraphs = sum(d.paragraphs for d in docs_info)
total_tables = sum(d.tables for d in docs_info)

with col1:
    st.metric("Total Documentos", len(docs_info))
with col2:
    st.metric("Tamaño Total", format_file_size(total_size))
with col3:
    st.metric("Total Párrafos", total_paragraphs)
with col4:
    st.metric("Total Tablas", total_tables)

# Lista de documentos con controles de reordenamiento
st.subheader("🔄 Reordenar Documentos")

# Funciones para reordenar
def move_up(index):
    if index > 0:
        docs_info[index], docs_info[index - 1] = docs_info[index - 1], docs_info[index]
        st.session_state.documents = docs_info
        st.rerun()

def move_down(index):
    if index < len(docs_info) - 1:
        docs_info[index], docs_info[index + 1] = docs_info[index + 1], docs_info[index]
        st.session_state.documents = docs_info
        st.rerun()

def remove_doc(index):
    doc_name = docs_info[index].name
    docs_info.pop(index)
    if doc_name in doc_sources:
        del doc_sources[doc_name]
    st.session_state.documents = docs_info
    st.session_state.doc_sources = doc_sources
    st.rerun()

# Mostrar lista de documentos
for idx, doc_info in enumerate(docs_info):
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([0.4, 0.4, 5, 1.5, 0.7])
        
        with col1:
            if st.button("↑", key=f"up_{idx}", disabled=(idx == 0), use_container_width=True):
                move_up(idx)
        
        with col2:
            if st.button("↓", key=f"down_{idx}", disabled=(idx == len(docs_info) - 1), use_container_width=True):
                move_down(idx)
        
        with col3:
            st.markdown(f"**{idx + 1}.** {doc_info.name}")
            if doc_info._analyzed:
                st.caption(f"📄 {doc_info.paragraphs} párrafos | 📊 {doc_info.tables} tablas | 📷 {doc_info.images} imágenes | 📑 ~{doc_info.pages_estimate} págs.")
        
        with col4:
            st.caption(f"📦 {format_file_size(doc_info.size)}")
        
        with col5:
            if st.button("❌", key=f"remove_{idx}", use_container_width=True):
                remove_doc(idx)
        
        st.divider()

# Vista previa del orden
st.subheader("👀 Vista Previa del Orden Final")
preview_text = " → ".join([f"{idx+1}. {d.name}" for idx, d in enumerate(docs_info)])
st.info(preview_text)

# Sección de combinación
st.header("🔗 Combinar Documentos")

output_name = st.text_input(
    "Nombre del archivo final",
    value=f"documentos_combinados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
    help="El archivo se descargará con este nombre"
)

# Preparar opciones
merge_options = {
    'add_page_break': add_page_breaks,
    'add_separator': add_separator,
    'number_documents': number_documents,
    'preserve_styles': preserve_styles,
    'add_cover_page': add_cover_page,
    'add_table_of_contents': add_table_of_contents,
    'stop_on_error': stop_on_error,
}

if add_cover_page:
    merge_options['cover_title'] = cover_title
    merge_options['cover_subtitle'] = cover_subtitle
    merge_options['cover_info'] = cover_info

# Barra de progreso
progress_bar = st.progress(0)
status_text = st.empty()

def progress_callback(current, total, message):
    """Callback para actualizar la barra de progreso"""
    progress = current / total
    progress_bar.progress(progress)
    status_text.text(f"{message} ({current}/{total})")

# Botón de combinación
col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🧩 Combinar Documentos", type="primary", use_container_width=True):
        if not docs_info:
            st.error("❌ No hay documentos para combinar")
        else:
            try:
                merger = DocumentMerger(progress_callback=progress_callback)
                
                result_bytes, stats = merger.merge_documents(docs_info, merge_options)
                
                st.session_state.merged_bytes = result_bytes
                st.session_state.merge_stats = stats
                st.session_state.output_name = output_name if output_name.lower().endswith(".docx") else (output_name + ".docx")
                
                progress_bar.progress(1.0)
                status_text.text("✅ ¡Combinación completada!")
                
                st.success("✅ Documentos combinados exitosamente!")
                st.balloons()
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error al combinar documentos: {str(e)}")
                with st.expander("Detalles del error"):
                    st.code(traceback.format_exc())
                logger.error(f"Error en combinación: {e}\n{traceback.format_exc()}")

with col2:
    if st.button("🔄 Limpiar Todo", use_container_width=True):
        st.session_state.documents = []
        st.session_state.doc_sources = {}
        st.session_state.merged_bytes = None
        st.session_state.merge_stats = None
        progress_bar.empty()
        status_text.empty()
        st.rerun()

# Sección de descarga
if st.session_state.merged_bytes:
    st.divider()
    st.header("⬇️ Descargar Resultado")
    
    file_size = len(st.session_state.merged_bytes)
    stats = st.session_state.merge_stats or {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tamaño del archivo", format_file_size(file_size))
    with col2:
        st.metric("Tiempo de procesamiento", f"{stats.get('processing_time', 0):.2f}s")
    with col3:
        st.metric("Documentos combinados", stats.get('total_docs', 0))
    
    st.download_button(
        "💾 Descargar Documento Combinado",
        data=st.session_state.merged_bytes,
        file_name=st.session_state.output_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        type="primary"
    )
    
    # Mostrar estadísticas detalladas
    with st.expander("📊 Estadísticas Detalladas"):
        st.json(stats)

# Footer con información
with st.expander("ℹ️ Información y Soporte"):
    st.markdown("""
    ### ✅ Características Implementadas
    
    - **Carga Avanzada**: Validación automática de archivos
    - **Preservación de Formato**: Estilos, imágenes, tablas
    - **Opciones Profesionales**: Portada, índice, separadores
    - **Análisis Detallado**: Información completa de cada documento
    - **Procesamiento Robusto**: Manejo avanzado de errores
    - **Estadísticas**: Reportes detallados del proceso
    
    ### ⚠️ Limitaciones Conocidas
    
    - Headers/footers complejos pueden requerir ajuste manual
    - Numeraciones complejas pueden necesitar revisión
    - Estilos con nombres duplicados pueden mezclarse
    
    ### 💡 Recomendaciones
    
    - Revisa siempre el documento combinado antes de usarlo en producción
    - Guarda copias de los documentos originales
    - Para documentos muy complejos, considera usar herramientas especializadas
    
    ### 🐛 Reportar Problemas
    
    Si encuentras algún problema, verifica:
    1. Que los archivos .docx no estén corruptos
    2. Que tengas permisos de lectura/escritura
    3. Que los archivos no estén abiertos en otro programa
    """)
