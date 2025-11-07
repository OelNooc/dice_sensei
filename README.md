# 🎲 DiceSensei

**Asistente de Estudio Inteligente con IA Local**

DiceSensei es un asistente de estudio potenciado por inteligencia artificial que funciona **100% offline** en tu computadora. Procesa documentos PDF, Word, TXT y Markdown para ayudarte a estudiar de manera más eficiente.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Open Source](https://img.shields.io/badge/Open%20Source-100%25-green.svg)]()
[![No Telemetry](https://img.shields.io/badge/Telemetry-None-blue.svg)]()

---

## ✨ Características

- 🤖 **IA Local**: Powered by Ollama - tus datos nunca salen de tu computadora
- 📄 **Multi-formato**: Soporta PDF, Word (.docx), TXT y Markdown
- 💬 **Chat Inteligente**: Conversa sobre el contenido de tus documentos
- 📝 **Resúmenes**: Genera resúmenes automáticos de documentos largos
- 🎯 **Flashcards**: Crea tarjetas de estudio basadas en el contenido
- 🔍 **Búsqueda Semántica**: Encuentra información relevante instantáneamente
- 🚀 **Optimización Automática**: Se adapta a tu hardware (CPU/GPU)
- 🎨 **Interfaz Moderna**: UI limpia y fácil de usar
- 🔒 **Privacidad Total**: Sin telemetría, sin datos en la nube

---

## 📦 Instalación

### Windows

#### Opción 1: Script Firmado (Recomendado)

1. **Descarga los archivos**:
   - [`install_windows.ps1`](https://github.com/OelNooc/dice_sensei/releases/latest/download/install_windows.ps1)
   - [`DiceSensei_Certificate.cer`](https://github.com/OelNooc/dice_sensei/releases/latest/download/DiceSensei_Certificate.cer)

2. **Instala el certificado** (solo la primera vez):
   - Doble clic en `DiceSensei_Certificate.cer`
   - Clic en **"Instalar certificado"**
   - Selecciona **"Usuario actual"** → Siguiente
   - Elige **"Colocar todos los certificados en el siguiente almacén"**
   - Clic en **"Examinar"** → Selecciona **"Editores de confianza"**
   - Finalizar → Aceptar

3. **Ejecuta el instalador**:
   - Clic derecho en `install_windows.ps1`
   - Selecciona **"Ejecutar con PowerShell"**
   - Sigue las instrucciones en pantalla

#### Opción 2: Script BAT (Alternativa)

Si tu antivirus bloquea el instalador PowerShell:

1. Descarga [`install_windows.bat`](https://github.com/OelNooc/dice_sensei/releases/latest/download/install_windows.bat)
2. **Añade una excepción en tu antivirus**:
   - **Bitdefender**: Protección → Exclusiones → Añadir carpeta
   - **Windows Defender**: Seguridad de Windows → Protección contra virus → Administrar configuración → Exclusiones
3. Ejecuta `install_windows.bat` como Administrador

### macOS

```bash
curl -fsSL https://github.com/OelNooc/dice_sensei/raw/main/installer/install_macos.sh | bash
```

O descarga manualmente:
```bash
chmod +x install_macos.sh
./install_macos.sh
```

### Linux

```bash
curl -fsSL https://github.com/OelNooc/dice_sensei/raw/main/installer/install_linux.sh | bash
```

O descarga manualmente:
```bash
chmod +x install_linux.sh
./install_linux.sh
```

---

## ⚠️ Advertencia de Antivirus (Falsos Positivos)

Algunos antivirus pueden marcar los instaladores como sospechosos. **Esto es un falso positivo común** en scripts de instalación automáticos que:
- Descargan archivos desde internet
- Ejecutan PowerShell
- Instalan software (Python, Ollama)
- Modifican el PATH del sistema

### ¿Por qué es seguro?

- ✅ **Código 100% Open Source**: Puedes revisar cada línea de código
- ✅ **Sin ofuscación**: Código claro y legible
- ✅ **Sin telemetría**: No recopilamos ningún dato
- ✅ **Certificado firmado**: El instalador PowerShell está digitalmente firmado
- ✅ **VirusTotal**: [Ver análisis completo](#) *(actualizar con tu enlace)*

### Si tu antivirus lo bloquea:

**Bitdefender:**
1. Abre Bitdefender → **Protección** → **Antivirus**
2. Ve a **Configuración** → **Exclusiones**
3. Añade la carpeta del proyecto
4. Ejecuta el instalador

**Windows Defender:**
1. Abre **Seguridad de Windows**
2. Ve a **Protección contra virus y amenazas**
3. **Administrar configuración** → **Exclusiones**
4. Añade carpeta → Selecciona la ubicación del instalador

---

## 🚀 Uso Rápido

### 1. Primer inicio

```bash
# Windows
DiceSensei.bat

# macOS/Linux
python3 main.py
```

En el primer inicio, DiceSensei:
- Descargará el modelo de IA recomendado (phi3.5, ~2.2 GB)
- Configurará el entorno según tu hardware
- Esto puede tomar varios minutos

### 2. Cargar un documento

```
📄 → Seleccionar archivo → PDF/Word/TXT/MD
```

### 3. Hacer preguntas

```
💬 Chat: "¿Cuáles son los conceptos principales?"
📝 Resumir: Genera un resumen automático
🎯 Flashcards: Crea tarjetas de estudio
```

---

## 📋 Requisitos

### Mínimos
- **OS**: Windows 10/11, macOS 10.15+, o Linux (Ubuntu 20.04+)
- **RAM**: 8 GB
- **Almacenamiento**: 5 GB libres
- **CPU**: Intel i5/AMD Ryzen 5 o superior
- **Conexión**: Solo para instalación inicial

### Recomendados
- **RAM**: 16 GB o más
- **GPU**: NVIDIA (CUDA) o AMD (ROCm) para mejor rendimiento
- **Almacenamiento**: SSD con 10 GB libres

---

## 🛠️ Instalación Manual (Desarrolladores)

### 1. Clonar el repositorio

```bash
git clone https://github.com/OelNooc/dice_sensei.git
cd dice_sensei
```

### 2. Instalar Ollama

**Windows/macOS:**
```bash
# Descarga desde https://ollama.ai/
# O usa el instalador automático
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. Descargar modelo recomendado

```bash
ollama pull phi3.5:latest
```

### 4. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6. Ejecutar

```bash
python main.py
```

---

## 📚 Documentación

### Modelos de IA Soportados

DiceSensei funciona con modelos de Ollama:

| Modelo | Tamaño | RAM Mínima | Velocidad | Calidad |
|--------|--------|------------|-----------|---------|
| **phi3.5** | 2.2 GB | 8 GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| llama3.2 | 2 GB | 8 GB | ⚡⚡⚡ | ⭐⭐⭐ |
| mistral | 4.1 GB | 12 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| llama3.1 | 4.7 GB | 16 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |

**Recomendado**: `phi3.5:latest` (mejor balance velocidad/calidad)

### Cambiar de modelo

```bash
# Descargar otro modelo
ollama pull llama3.2

# Cambiar en DiceSensei
Configuración → Modelo → Seleccionar
```

---

## 🔧 Configuración Avanzada

### Archivos de configuración

```
config/
  ├── settings.json      # Configuración general
  ├── models.json        # Modelos disponibles
  └── version.json       # Versión actual
```

### Personalizar modelo

Edita `config/models.json`:

```json
{
  "selected_model": "phi3.5:latest",
  "temperature": 0.7,
  "context_length": 4096,
  "gpu_layers": -1
}
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! 

### Cómo contribuir

1. **Fork** el proyecto
2. Crea tu **feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit** tus cambios: `git commit -m 'Add: Amazing Feature'`
4. **Push** a la rama: `git push origin feature/AmazingFeature`
5. Abre un **Pull Request**

### Reportar bugs

Abre un [Issue](https://github.com/OelNooc/dice_sensei/issues) con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots (si aplica)
- Sistema operativo y versión

---

## 🐛 Solución de Problemas

### Ollama no se inicia

```bash
# Windows
Ejecuta como Administrador: Services → Busca "Ollama" → Iniciar

# macOS/Linux
systemctl restart ollama
```

### Error de memoria (OOM)

Usa un modelo más pequeño:
```bash
ollama pull phi3.5:latest  # Solo 2.2 GB
```

### GPU no detectada

Verifica drivers:
```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi
```

### Python no encontrado

Descarga desde [python.org](https://python.org) y marca "Add to PATH"

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**OelNooc**
- GitHub: [@OelNooc](https://github.com/OelNooc)
- Proyecto: [DiceSensei](https://github.com/OelNooc/dice_sensei)

---

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) - Motor de IA local
- [Phi-3.5](https://huggingface.co/microsoft/phi-3.5) - Modelo de Microsoft
- Comunidad Open Source

---

## ⭐ Roadmap

- [ ] Soporte para más formatos (EPUB, PowerPoint)
- [ ] Modo de estudio con temporizador Pomodoro
- [ ] Exportar notas y resúmenes
- [ ] Interfaz web opcional
- [ ] Modo colaborativo (compartir documentos)
- [ ] App móvil (Android/iOS)

---

## 📊 Estado del Proyecto

![GitHub last commit](https://img.shields.io/github/last-commit/OelNooc/dice_sensei)
![GitHub issues](https://img.shields.io/github/issues/OelNooc/dice_sensei)
![GitHub stars](https://img.shields.io/github/stars/OelNooc/dice_sensei)
![GitHub forks](https://img.shields.io/github/forks/OelNooc/dice_sensei)

---

<div align="center">

**¿Te gusta DiceSensei? Dale una ⭐ en GitHub!**

[Reportar Bug](https://github.com/OelNooc/dice_sensei/issues) · [Solicitar Feature](https://github.com/OelNooc/dice_sensei/issues) · [Documentación](#)

Made with ❤️ by [OelNooc](https://github.com/OelNooc)

</div>