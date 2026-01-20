"""
Archivo de configuración para la aplicación
"""

# Configuración de la aplicación
APP_NAME = "Combinador Profesional de Documentos Word"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Aplicación profesional para combinar documentos Word con preservación avanzada de formato"

# Límites de la aplicación
MAX_FILE_SIZE_MB = 100  # Tamaño máximo de archivo individual en MB
MAX_DOCUMENTS = 50  # Número máximo de documentos a combinar
MAX_TOTAL_SIZE_MB = 500  # Tamaño total máximo en MB

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configuración de procesamiento
DEFAULT_PAGE_BREAK = True
DEFAULT_PRESERVE_STYLES = True
DEFAULT_AUTO_ANALYZE = True

# Configuración de UI
SHOW_DETAILED_STATS = True
ENABLE_PROGRESS_BAR = True
SHOW_PREVIEW = True
