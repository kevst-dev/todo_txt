# `todo_txt` - Gestor de tareas avanzado para todo.txt

`todo_txt` es una herramienta de línea de comandos robusta, moderna y visualmente atractiva para gestionar tus tareas siguiendo el estándar [todo.txt](https://todotxt.org/). Está construida en **Python 3.14** utilizando `uv` y aprovecha la potencia de `rich` para la visualización y `lark` para un motor de búsqueda avanzado.

---

## 🚀 Características principales

- ✅ **Gestión completa**: `list`, `add`, `do`, `edit`, `archive`.
- 🔍 **Búsqueda avanzada**: Filtrado potente basado en expresiones booleanas (ej: `project == 'work' AND NOT done == True`).
- 📊 **Analíticas visuales**: Árboles jerárquicos de proyectos y contextos para entender tu carga de trabajo.
- 📝 **Gestión de notas**: Abre notas externas asociadas a tus tareas usando el tag `note:archivo.md`.
- 🛠️ **Basado en uv**: Entornos aislados, rápidos y fáciles de gestionar.

---

## 🛠️ Pre-requisitos

- [python](https://www.python.org/): Versión **3.14** o superior.
- [uv](https://github.com/astral-sh/uv): Administrador de proyectos ultrarrápido.
- [just](https://github.com/casey/just): (Opcional) Ejecutor de comandos para facilitar tareas comunes.

---

## 🏗️ Instalación

Clona el repositorio e instala las dependencias:

```bash
just install
```

Para instalar el comando `todo-txt` de forma global en tu sistema (usuario):

```bash
just install-tool
```

Esto te permitirá usar `todo-txt` desde cualquier directorio.

---

## 🕹️ Cómo utilizar

### Opciones Globales
Antes de cualquier subcomando, puedes especificar la ubicación de tus archivos de tareas:

- `--todo-file PATH`: Ruta al archivo `todo.txt` (por defecto: `./todo.txt`).
- `--done-file PATH`: Ruta al archivo `done.txt` (por defecto: `./done.txt`).

**Ejemplo con rutas personalizadas:**
```bash
todo-txt --todo-file ~/mis_tareas/trabajo.txt list
```

---

### 1. Gestión de Tareas
Añade, completa y edita tareas con facilidad:

```bash
# Añadir una tarea (con fecha automática)
todo-txt add "(A) Comprar café @supermercado +hogar"

# Listar tareas pendientes
todo-txt list

# Marcar tarea con ID 5 como completada
todo-txt do 5

# Editar el texto completo de una tarea
todo-txt edit 5 "2026-03-04 Comprar café premium @super +hogar"

# Archivar tareas completadas a done.txt
todo-txt archive
```

### 2. Motor de Búsqueda Avanzado
Utiliza el flag `--filter` para realizar búsquedas complejas:

```bash
todo-txt list --filter "project == 'uniandes' AND priority >= 'C'"
todo-txt list --filter "tag.due < '2026-12-31' AND NOT done == True"
```

### 3. Analíticas (`stats`)
Obtén un resumen de tu estructura de proyectos y contextos:

```bash
todo-txt stats summary
```
O con el alias:
```bash
todo-txt st
```

### 4. Notas
Si una tarea tiene el tag `note:mi_nota.md`, puedes abrirla con tu editor favorito (`$EDITOR`):

```bash
todo-txt note 12
```

---

## 🧪 Pruebas

Para ejecutar la suite completa de pruebas (Unitarias e Integración):

```bash
just test_unit
just test_integration
```

---

## 📜 Licencia

- GNU General Public License, Version 3.0, [LICENSE](LICENSE).

---

## ✍️ Autor

- **kevst-dev** (usuario GitHub)
