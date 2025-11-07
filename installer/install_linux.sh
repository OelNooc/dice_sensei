#!/bin/bash

# DiceSensei - Instalador para Linux
# Ejecutar: chmod +x install_linux.sh && ./install_linux.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 
print_color() {
    echo -e "${2}${1}${NC}"
}

check_dependencies() {
    print_color "🔍 Verificando dependencias..." "$BLUE"
    
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v unzip &> /dev/null; then
        missing_deps+=("unzip")
    fi
    
    if command -v apt &> /dev/null; then
        pkg_manager="apt"
    elif command -v dnf &> /dev/null; then
        pkg_manager="dnf"
    elif command -v yum &> /dev/null; then
        pkg_manager="yum"
    else
        pkg_manager="unknown"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_color "❌ Dependencias faltantes: ${missing_deps[*]}" "$RED"
        if [ "$pkg_manager" = "apt" ]; then
            print_color "Instala las dependencias con:" "$YELLOW"
            print_color "sudo apt update && sudo apt install ${missing_deps[*]}" "$YELLOW"
        elif [ "$pkg_manager" = "dnf" ]; then
            print_color "Instala las dependencias con:" "$YELLOW"
            print_color "sudo dnf install ${missing_deps[*]}" "$YELLOW"
        elif [ "$pkg_manager" = "yum" ]; then
            print_color "Instala las dependencias con:" "$YELLOW"
            print_color "sudo yum install ${missing_deps[*]}" "$YELLOW"
        else
            print_color "Por favor instala manualmente: ${missing_deps[*]}" "$YELLOW"
        fi
        exit 1
    fi
    
    print_color "✅ Todas las dependencias están instaladas" "$GREEN"
}

install_ollama() {
    print_color "🤖 Instalando Ollama..." "$BLUE"
    
    if command -v ollama &> /dev/null; then
        print_color "✅ Ollama ya está instalado" "$GREEN"
        return 0
    fi
    
    print_color "📥 Descargando e instalando Ollama..." "$BLUE"
    
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        print_color "✅ Ollama instalado correctamente" "$GREEN"
        
        print_color "🚀 Iniciando servicio Ollama..." "$BLUE"
        systemctl --user enable ollama
        systemctl --user start ollama
        sleep 5
        return 0
    else
        print_color "❌ Error instalando Ollama" "$RED"
        print_color "Instala Ollama manualmente desde: https://ollama.ai/" "$YELLOW"
        return 1
    fi
}

create_install_dir() {
    local install_dir="$HOME/DiceSensei"
    
    print_color "📁 Creando directorio de instalación..." "$BLUE"
    
    if [ -d "$install_dir" ]; then
        print_color "🔄 Actualizando instalación existente..." "$YELLOW"
        rm -rf "$install_dir"
    fi
    
    mkdir -p "$install_dir"
    echo "$install_dir"
}

download_dicesensei() {
    local install_dir="$1"
    
    print_color "📥 Descargando DiceSensei..." "$BLUE"
    
    LATEST_URL="https://github.com/OelNooc/dice_sensei/releases/latest/download/dicesensei-linux.zip"
    
    if ! curl -L -o "/tmp/dicesensei-linux.zip" "$LATEST_URL"; then
        print_color "❌ Error descargando DiceSensei" "$RED"
        exit 1
    fi
    
    print_color "📦 Extrayendo archivos..." "$BLUE"
    
    if ! unzip -q "/tmp/dicesensei-linux.zip" -d "$install_dir"; then
        print_color "❌ Error extrayendo archivos" "$RED"
        exit 1
    fi
    
    rm "/tmp/dicesensei-linux.zip"
}

create_desktop_file() {
    local install_dir="$1"
    
    print_color "🎯 Creando acceso directo..." "$BLUE"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$HOME/.local/share/applications/dicesensei.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DiceSensei
Comment=Asistente de estudio inteligente
Exec=$install_dir/dicesensei
Icon=$install_dir/assets/icons/dicesensei.png
Terminal=false
Categories=Education;Office;
Keywords=education;ai;study;assistant;
StartupWMClass=DiceSensei
EOF
    
    chmod +x "$HOME/.local/share/applications/dicesensei.desktop"
    
    if [ -d "$HOME/Desktop" ]; then
        cp "$HOME/.local/share/applications/dicesensei.desktop" "$HOME/Desktop/"
        print_color "✅ Acceso directo creado en el escritorio" "$GREEN"
    fi
    
    if [ -d "$HOME/Escritorio" ]; then  # Español
        cp "$HOME/.local/share/applications/dicesensei.desktop" "$HOME/Escritorio/"
        print_color "✅ Acceso directo creado en el Escritorio" "$GREEN"
    fi
}

make_executable() {
    local install_dir="$1"
    
    print_color "🔧 Configurando permisos..." "$BLUE"
    
    chmod +x "$install_dir/dicesensei"
    
    find "$install_dir" -name "*.py" -exec chmod +x {} \;
    
    print_color "✅ Permisos configurados correctamente" "$GREEN"
}

main() {
    print_color "🎲 DiceSensei - Instalador para Linux" "$GREEN"
    print_color "======================================" "$GREEN"
    echo ""
    
    if [ "$EUID" -eq 0 ]; then
        print_color "⚠️  No ejecutes este script como root" "$YELLOW"
        print_color "   El instalador creará los archivos en tu directorio home" "$YELLOW"
        exit 1
    fi
    
    check_dependencies
    
    if ! install_ollama; then
        print_color "⚠️  Continuando sin Ollama, pero será necesario para usar DiceSensei" "$YELLOW"
    fi
    
    INSTALL_DIR=$(create_install_dir)
    
    download_dicesensei "$INSTALL_DIR"
    
    make_executable "$INSTALL_DIR"
    
    create_desktop_file "$INSTALL_DIR"
    
    print_color "" ""
    print_color "✅ ¡DiceSensei instalado correctamente!" "$GREEN"
    print_color "" ""
    print_color "🚀 Para iniciar DiceSensei:" "$BLUE"
    print_color "   • Busca 'DiceSensei' en tu menú de aplicaciones" "$BLUE"
    print_color "   • O ejecuta: $INSTALL_DIR/dicesensei" "$BLUE"
    print_color "" ""
    print_color "📚 Características:" "$YELLOW"
    print_color "   • Asistente de estudio offline" "$YELLOW"
    print_color "   • Soporta PDF, Word, Texto, Markdown" "$YELLOW"
    print_color "   • Actualizaciones automáticas" "$YELLOW"
    print_color "   • Completamente gratuito" "$YELLOW"
    print_color "" ""
    print_color "🤖 Ollama está instalado y configurado" "$BLUE"
    print_color "   Ejecuta 'ollama pull phi3.5:latest' para descargar el modelo recomendado" "$BLUE"
    print_color "" ""
    
    read -p "¿Quieres iniciar DiceSensei ahora? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_color "🚀 Iniciando DiceSensei..." "$BLUE"
        cd "$INSTALL_DIR" && ./dicesensei
    fi
}

main "$@"