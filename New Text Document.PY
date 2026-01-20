# app.py
import os
from io import BytesIO
from copy import deepcopy
import streamlit as st
import pandas as pd
from docx import Document

st.set_page_config(page_title="Unir DOCX con orden", layout="wide")

st.title("🔗 Unir documentos Word (.docx) con orden personalizado")

st.markdown(
    "- Modo A: **Ruta de carpeta** (ideal si lo corres local)\n"
    "- Modo B: **Subir archivos** (sirve en local y en la nube)\n"
)

mode = st.radio("¿Cómo quieres cargar los Word?", ["Ruta de carpeta (local)", "Subir archivos"], horizontal=True)

add_page_breaks = st.checkbox("Agregar salto de página entre documentos", value=True)

def list_docx_in_folder(folder_path: str):
    if not folder_path or not os.path.isdir(folder_path):
        return []
    files = []
    for name in os.listdir(folder_path):
        if name.lower().endswith(".docx") and not name.startswith("~$"):
            files.append(os.path.join(folder_path, name))
    files.sort()
    return files

def append_doc(master: Document, src: Document, add_page_break: bool):
    """
    Merge simple: copia el body XML de src y lo pega en master.
    Preserva bastante del formato, pero:
      - Headers/footers y secciones complejas pueden no quedar perfectos.
      - Estilos con el mismo nombre pueden 'chocar' (típico de Word).
    """
    if add_page_break and len(master.paragraphs) > 0:
        master.add_page_break()

    # Copiar elementos del body
    for element in src.element.body:
        master.element.body.append(deepcopy(element))

def merge_docx(paths_in_order, add_page_break: bool) -> bytes:
    if not paths_in_order:
        raise ValueError("No hay documentos para unir.")

    # Documento base: el primero
    master = Document(paths_in_order[0])

    # Resto
    for p in paths_in_order[1:]:
        src = Document(p)
        append_doc(master, src, add_page_break)

    out = BytesIO()
    master.save(out)
    out.seek(0)
    return out.read()

def merge_docx_uploaded(files_in_order, add_page_break: bool) -> bytes:
    if not files_in_order:
        raise ValueError("No hay documentos para unir.")

    # Guardar en memoria temporalmente (Document necesita path o file-like; file-like funciona)
    first = files_in_order[0]
    master = Document(first)

    for f in files_in_order[1:]:
        src = Document(f)
        append_doc(master, src, add_page_break)

    out = BytesIO()
    master.save(out)
    out.seek(0)
    return out.read()

# ---------------- UI: cargar docs ----------------
docs = []
doc_sources = {}  # name -> (type, payload)

if mode == "Ruta de carpeta (local)":
    folder = st.text_input("Ruta de la carpeta", placeholder=r"C:\Users\...\Documentos\words")
    if folder:
        paths = list_docx_in_folder(folder)
        if not paths:
            st.warning("No encontré .docx en esa carpeta (o la ruta no existe).")
        else:
            for p in paths:
                name = os.path.basename(p)
                docs.append(name)
                doc_sources[name] = ("path", p)

else:
    uploaded = st.file_uploader("Sube uno o varios .docx", type=["docx"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            docs.append(f.name)
            doc_sources[f.name] = ("upload", f)

if not docs:
    st.stop()

st.subheader("1) Define el orden")

# Tabla editable con orden
df = pd.DataFrame({"archivo": docs, "orden": list(range(1, len(docs) + 1))})
st.caption("Edita la columna **orden** (1,2,3...). Luego clic en **Previsualizar orden**.")
edited = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "orden": st.column_config.NumberColumn("orden", min_value=1, step=1),
        "archivo": st.column_config.TextColumn("archivo", disabled=True),
    },
    key="order_table",
)

colA, colB = st.columns([1, 2])
with colA:
    preview = st.button("👀 Previsualizar orden", use_container_width=True)

# Validación y orden final
def compute_order(table: pd.DataFrame):
    t = table.copy()
    if t["orden"].isna().any():
        raise ValueError("Hay valores vacíos en 'orden'.")
    # Evitar duplicados para que no haya “empates” raros
    if t["orden"].duplicated().any():
        raise ValueError("Hay órdenes duplicadas. Cada archivo debe tener un número único.")
    t = t.sort_values("orden", ascending=True)
    return t["archivo"].tolist()

if preview:
    try:
        ordered_names = compute_order(edited)
        st.success("Orden listo ✅")
        st.write(ordered_names)
    except Exception as e:
        st.error(str(e))

st.subheader("2) Unir y descargar")

output_name = st.text_input("Nombre del archivo final", value="unido.docx")

if st.button("🧩 Unir documentos", type="primary", use_container_width=True):
    try:
        ordered_names = compute_order(edited)

        # Construir la lista en orden (paths o archivos subidos)
        if mode == "Ruta de carpeta (local)":
            ordered_paths = [doc_sources[n][1] for n in ordered_names]
            merged_bytes = merge_docx(ordered_paths, add_page_breaks)
        else:
            ordered_files = [doc_sources[n][1] for n in ordered_names]  # UploadedFile es file-like
            merged_bytes = merge_docx_uploaded(ordered_files, add_page_breaks)

        st.success("Listo. Documento unido ✅")
        st.download_button(
            "⬇️ Descargar DOCX unido",
            data=merged_bytes,
            file_name=output_name if output_name.lower().endswith(".docx") else (output_name + ".docx"),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error: {e}")

with st.expander("Limitaciones (para que no te sorprenda Word)"):
    st.markdown(
        "- Unir por XML del body preserva mucho formato, pero **headers/footers, secciones, numeraciones complejas** pueden no quedar perfectas.\n"
        "- Si tus documentos tienen estilos con el mismo nombre pero diferente definición, Word puede “mezclar” resultados.\n"
        "- Si necesitas unión 100% fiel con secciones complejas, conviene usar `docxcompose` (lib extra) y un pipeline más estricto."
    )
