# 🔍 Cómo Encontrar la Ruta de tu Repositorio en GitHub

## 📋 Opciones para Encontrar la URL

### Opción 1: Si ya tienes el repositorio en GitHub

1. **Ve a tu cuenta de GitHub** (github.com)
2. **Busca tu repositorio** en la lista de repositorios
3. **Haz clic en el repositorio**
4. **Haz clic en el botón verde "Code"**
5. **Copia la URL** que aparece (HTTPS o SSH)

La URL se verá así:
- HTTPS: `https://github.com/TU_USUARIO/NOMBRE_REPO.git`
- SSH: `git@github.com:TU_USUARIO/NOMBRE_REPO.git`

### Opción 2: Verificar si ya está configurado

Ejecuta este comando en la terminal:

```bash
git remote -v
```

Si ya tienes un remoto configurado, verás algo como:
```
origin  https://github.com/usuario/repo.git (fetch)
origin  https://github.com/usuario/repo.git (push)
```

### Opción 3: Si NO tienes el repositorio en GitHub aún

Necesitas crear el repositorio primero:

1. **Ve a GitHub.com** e inicia sesión
2. **Haz clic en el botón "+"** (arriba a la derecha)
3. **Selecciona "New repository"**
4. **Llena los datos**:
   - Repository name: `A_5_3_UNIR_WORD` (o el nombre que prefieras)
   - Description: "Combinador Profesional de Documentos Word"
   - Público o Privado (tu elección)
   - **NO marques** "Initialize with README" (ya tienes archivos)
5. **Haz clic en "Create repository"**
6. **Copia la URL** que GitHub te muestra

## 🔗 Conectar tu Repositorio Local con GitHub

Una vez que tengas la URL de GitHub, ejecuta estos comandos:

```bash
# Agregar el remoto (reemplaza con tu URL)
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

# Verificar que se agregó correctamente
git remote -v

# Subir el código
git branch -M main
git push -u origin main
```

## 📝 Ejemplo Completo

Si tu usuario de GitHub es `juanperez` y quieres llamar al repo `combinador-word`:

```bash
# 1. Crear el repositorio en GitHub (desde la web)

# 2. Conectar el repositorio local
git remote add origin https://github.com/juanperez/combinador-word.git

# 3. Verificar
git remote -v

# 4. Subir código
git add .
git commit -m "Initial commit: Combinador Profesional de Documentos Word"
git branch -M main
git push -u origin main
```

## ✅ Verificar la Conexión

Después de configurar, puedes verificar con:

```bash
# Ver la URL del remoto
git remote get-url origin

# O ver todos los detalles
git remote show origin
```

## 🚀 Para Streamlit Cloud

Una vez que tengas el repositorio en GitHub:

1. La URL será: `https://github.com/TU_USUARIO/NOMBRE_REPO`
2. Usa esta URL en Streamlit Cloud cuando te pida el repositorio
3. Streamlit Cloud detectará automáticamente `app.py` y `requirements.txt`

## 💡 Tips

- **HTTPS** es más fácil para principiantes (solo necesitas usuario/contraseña)
- **SSH** requiere configuración de llaves pero es más seguro
- Puedes cambiar la URL del remoto con: `git remote set-url origin NUEVA_URL`

---

**¿Necesitas ayuda?** Si tienes problemas, comparte el mensaje de error y te ayudo a resolverlo.
