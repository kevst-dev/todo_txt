# Muestra la lista de comandos disponibles
default:
    @just --list

# Instalar dependencias del proyecto
install:
    @echo "🚀 Creating virtual environment using uv"
    @uv sync
    @uv run pre-commit install

check: install
    uv export --format requirements-txt > requirements.txt

    @echo "🚀 Checking lock file consistency with 'pyproject.toml'"
    @uv lock --locked

    @echo "🚀 Linting code: Running pre-commit"
    @uv run pre-commit run --all-files

# Ejecutar pruebas
test_unit *args:
    @echo "🚀 Testing code: Running pytest"
    @uv run pytest tests/unit {{args}}

test_integration *args:
    @echo "🚀 Testing code: Running pytest"
    @uv run pytest tests/integration {{args}}

# Instalar el comando todo-txt globalmente en el sistema/usuario
install-tool:
    @echo "🚀 Installing todo-txt tool using uv"
    @uv tool install --editable .

# Ejecutar entorno de desarrollo
run *args:
    @echo "🚀 Running development cli"
    @uv run todo-txt {{args}}
