#!/bin/bash

# DiceSensei - Instalador para macOS
# Ejecutar: chmod +x install_macos.sh && ./install_macos.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

install_ollama_macos() {
    print_color "🤖 Instalando Ollama..." "$BLUE"
    
    if command -v ollama &> /dev/null; then
        print_color "✅ Ollama ya está instalado" "$GREEN"
        return 0
    fi
    
    print_color "📥 Descargando e instalando Ollama..." "$BLUE"
    
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        print_color "✅ Ollama instalado correctamente" "$GREEN"
        
        print_color "🚀 Iniciando Ollama..." "$BLUE"
        nohup ollama serve > /dev/null 2>&1 &
        sleep 5
        return 0
    else
        print_color "❌ Error instalando Ollama" "$RED"
        print_color "Instala Ollama manualmente desde: https://ollama.ai/" "$YELLOW"
        return 1
    fi
}

check_dependencies() {
    print_color "🔍 Verificando dependencias..." "$BLUE"
    
    if ! command -v curl &> /dev/null; then
        print_color "❌ curl no está instalado" "$RED"
        print_color "Instala curl con: brew install curl" "$YELLOW"
        exit 1
    fi
    
    if ! command -v unzip &> /dev/null; then
        print_color "❌ unzip no está instalado" "$RED"
        print_color "Instala unzip con: brew install unzip" "$YELLOW"
        exit 1
    fi
    
    print_color "✅ Todas las dependencias están instaladas" "$GREEN"
}

create_install_dir() {
    local install_dir="$HOME/Applications/DiceSensei"
    
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
    
    LATEST_URL="https://github.com/OelNooc/dice_sensei/releases/latest/download/dicesensei-macos.zip"
    
    if ! curl -L -o "/tmp/dicesensei-macos.zip" "$LATEST_URL"; then
        print_color "❌ Error descargando DiceSensei" "$RED"
        exit 1
    fi
    
    print_color "📦 Extrayendo archivos..." "$BLUE"
    
    if ! unzip -q "/tmp/dicesensei-macos.zip" -d "$install_dir"; then
        print_color "❌ Error extrayendo archivos" "$RED"
        exit 1
    fi
    
    rm "/tmp/dicesensei-macos.zip"
}

create_app_bundle() {
    local install_dir="$1"
    local app_dir="$HOME/Applications/DiceSensei.app"
    
    print_color "📦 Creando bundle de aplicación..." "$BLUE"
    
    rm -rf "$app_dir"
    mkdir -p "$app_dir/Contents/MacOS"
    mkdir -p "$app_dir/Contents/Resources"
    
    cat > "$app_dir/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>dicesensei</string>
    <key>CFBundleIconFile</key>
    <string>dicesensei.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.dicesensei.app</string>
    <key>CFBundleName</key>
    <string>DiceSensei</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF
    
    cp "$install_dir/dicesensei" "$app_dir/Contents/MacOS/"
    
    if [ -f "$install_dir/assets/icons/dicesensei.icns" ]; then
        cp "$install_dir/assets/icons/dicesensei.icns" "$app_dir/Contents/Resources/"
    fi
    
    cp -r "$install_dir/assets" "$app_dir/Contents/Resources/"
    cp -r "$install_dir/config" "$app_dir/Contents/Resources/"
    
    chmod +x "$app_dir/Contents/MacOS/dicesensei"
    
    print_color "✅ Aplicación creada en $app_dir" "$GREEN"
}

create_wrapper_script() {
    local install_dir="$1"
    
    cat > "$install_dir/start_dicesensei.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" && ./dicesensei
EOF
    
    chmod +x "$install_dir/start_dicesensei.sh"
}

main() {
    print_color "🎲 DiceSensei - Instalador para macOS" "$GREEN"
    print_color "======================================" "$GREEN"
    echo ""
    
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        print_color "🔍 Detectada arquitectura Apple Silicon" "$BLUE"
    elif [ "$ARCH" = "x86_64" ]; then
        print_color "🔍 Detectada arquitectura Intel" "$BLUE"
    else
        print_color "⚠️  Arquitectura no soportada: $ARCH" "$YELLOW"
    fi
    
    check_dependencies
    
    INSTALL_DIR=$(create_install_dir)
    
    download_dicesensei "$INSTALL_DIR"
    
    chmod +x "$INSTALL_DIR/dicesensei"
    
    create_app_bundle "$INSTALL_DIR"
    
    create_wrapper_script "$INSTALL_DIR"
    
    print_color "" ""
    print_color "✅ ¡DiceSensei instalado correctamente!" "$GREEN"
    print_color "" ""
    print_color "🚀 Para iniciar DiceSensei:" "$BLUE"
    print_color "   • Abre Launchpad y busca 'DiceSensei'" "$BLUE"
    print_color "   • O abre Finder → Applications → DiceSensei.app" "$BLUE"
    print_color "   • O ejecuta: open $HOME/Applications/DiceSensei.app" "$BLUE"
    print_color "" ""
    print_color "📚 Características:" "$YELLOW"
    print_color "   • Asistente de estudio offline" "$YELLOW"
    print_color "   • Interfaz nativa de macOS" "$YELLOW"
    print_color "   • Actualizaciones automáticas" "$YELLOW"
    print_color "   • Soporte multi-idioma" "$YELLOW"
    print_color "" ""
    
    read -p "¿Quieres abrir DiceSensei ahora? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_color "🚀 Abriendo DiceSensei..." "$BLUE"
        open "$HOME/Applications/DiceSensei.app"
    fi
}

main "$@"