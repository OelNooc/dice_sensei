# DiceSensei - Instalador de Windows (Firmable)
# Requiere PowerShell 5.1 o superior

param(
    [switch]$NoAdmin
)

$Host.UI.RawUI.WindowTitle = "DiceSensei - Instalador de Windows"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "🎲 DiceSensei - Asistente de Estudio Inteligente" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin -and -not $NoAdmin) {
    Write-Host "⚠️  Ejecutando sin permisos de administrador..." -ForegroundColor Yellow
    Write-Host "   Algunas funciones pueden estar limitadas." -ForegroundColor Yellow
    Write-Host ""
}

$INSTALL_DIR = Join-Path $env:USERPROFILE "DiceSensei"
$TEMP_ZIP = Join-Path $env:TEMP "dicesensei-windows.zip"
$OLLAMA_INSTALLER = Join-Path $env:TEMP "OllamaSetup.exe"

Write-Host "📍 Directorio de instalación: $INSTALL_DIR" -ForegroundColor White
Write-Host ""

if (Test-Path $INSTALL_DIR) {
    Write-Host "🔄 Eliminando instalación previa..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $INSTALL_DIR -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Instalación anterior eliminada" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ No se pudo eliminar la instalación anterior." -ForegroundColor Red
        Write-Host "   Cierra DiceSensei si está ejecutándose y vuelve a intentar." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

try {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
    Write-Host "✅ Directorio de instalación creado" -ForegroundColor Green
}
catch {
    Write-Host "❌ No se pudo crear el directorio de instalación." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "📥 Descargando DiceSensei..." -ForegroundColor Cyan
try {
    Write-Host "   Descargando desde GitHub..." -ForegroundColor Gray
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri 'https://github.com/OelNooc/dice_sensei/releases/latest/download/dicesensei-windows.zip' -OutFile $TEMP_ZIP -ErrorAction Stop
    
    if (Test-Path $TEMP_ZIP) {
        Write-Host "   ✅ Descarga completada" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Error descargando DiceSensei: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Verifica tu conexión a internet." -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "📦 Extrayendo archivos..." -ForegroundColor Cyan
try {
    Expand-Archive -Path $TEMP_ZIP -DestinationPath $INSTALL_DIR -Force -ErrorAction Stop
    Write-Host "   ✅ Extracción completada" -ForegroundColor Green
    Remove-Item $TEMP_ZIP -Force -ErrorAction SilentlyContinue
}
catch {
    Write-Host "❌ Error extrayendo archivos: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "🤖 Verificando Ollama..." -ForegroundColor Cyan
$ollamaInstalled = $false
try {
    $null = ollama --version 2>$null
    $ollamaInstalled = $true
    Write-Host "   ✅ Ollama ya está instalado" -ForegroundColor Green
}
catch {
    Write-Host "   📥 Ollama no detectado, instalando..." -ForegroundColor Yellow
    
    try {
        Write-Host "   Descargando Ollama..." -ForegroundColor Gray
        Invoke-WebRequest -Uri 'https://ollama.ai/download/OllamaSetup.exe' -OutFile $OLLAMA_INSTALLER -ErrorAction Stop
        
        if (Test-Path $OLLAMA_INSTALLER) {
            Write-Host "   Instalando Ollama (puede tomar unos minutos)..." -ForegroundColor Gray
            $process = Start-Process -FilePath $OLLAMA_INSTALLER -ArgumentList '/S' -Wait -PassThru -ErrorAction Stop
            
            if ($process.ExitCode -eq 0) {
                Write-Host "   ✅ Ollama instalado correctamente" -ForegroundColor Green
            }
            else {
                Write-Host "   ⚠️  Ollama instalado con advertencias" -ForegroundColor Yellow
            }
            
            Remove-Item $OLLAMA_INSTALLER -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Host "   ⚠️  Error instalando Ollama: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   Puedes instalarlo manualmente desde: https://ollama.ai/" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🐍 Verificando Python..." -ForegroundColor Cyan
$pythonInstalled = $false
try {
    $null = python --version 2>$null
    $pythonInstalled = $true
    Write-Host "   ✅ Python ya está instalado" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Python no encontrado en el PATH" -ForegroundColor Yellow
    Write-Host "   Instalando Python automáticamente..." -ForegroundColor Yellow
    
    try {
        $pythonInstaller = Join-Path $env:TEMP "python_installer.exe"
        Write-Host "   Descargando Python 3.11.5..." -ForegroundColor Gray
        Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile $pythonInstaller -ErrorAction Stop
        
        if (Test-Path $pythonInstaller) {
            Write-Host "   Instalando Python..." -ForegroundColor Gray
            Start-Process -FilePath $pythonInstaller -ArgumentList '/quiet', 'InstallAllUsers=0', 'Include_launcher=0', 'PrependPath=1' -Wait -ErrorAction Stop
            Write-Host "   ✅ Python instalado" -ForegroundColor Green
            Remove-Item $pythonInstaller -Force -ErrorAction SilentlyContinue
            
            # Refrescar PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
        }
    }
    catch {
        Write-Host "   ❌ Error instalando Python: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Instala Python manualmente desde: https://python.org" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📦 Instalando dependencias de Python..." -ForegroundColor Cyan
Set-Location $INSTALL_DIR

try {
    Write-Host "   Actualizando pip..." -ForegroundColor Gray
    python -m pip install --upgrade pip --quiet 2>$null
    
    Write-Host "   Instalando paquetes requeridos..." -ForegroundColor Gray
    python -m pip install requests pypdf2 pypdf python-docx markdown psutil --quiet 2>$null
    Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Algunas dependencias no se pudieron instalar automáticamente" -ForegroundColor Yellow
    Write-Host "   Se intentarán instalar durante el primer inicio." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Creando accesos directos..." -ForegroundColor Cyan

$batPath = Join-Path $env:USERPROFILE "Desktop\DiceSensei.bat"
$batContent = @"
@echo off
chcp 65001 >nul
cd /d "$INSTALL_DIR"
echo Iniciando DiceSensei...
python main.py
pause
"@
Set-Content -Path $batPath -Value $batContent -Encoding UTF8
Write-Host "   ✅ Acceso directo creado (DiceSensei.bat)" -ForegroundColor Green

try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut((Join-Path $env:USERPROFILE "Desktop\DiceSensei.lnk"))
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "main.py"
    $Shortcut.WorkingDirectory = $INSTALL_DIR
    $iconPath = Join-Path $INSTALL_DIR "assets\icons\dicesensei.ico"
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = $iconPath
    }
    $Shortcut.Description = "DiceSensei - Asistente de Estudio Inteligente"
    $Shortcut.Save()
    Write-Host "   ✅ Acceso directo creado (DiceSensei.lnk)" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  No se pudo crear el acceso directo .lnk" -ForegroundColor Yellow
}

$configDir = Join-Path $INSTALL_DIR "config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

Write-Host ""
Write-Host "✅ ¡DiceSensei instalado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Ubicación: $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para iniciar DiceSensei:" -ForegroundColor Cyan
Write-Host "   • Doble clic en 'DiceSensei.bat' en tu escritorio" -ForegroundColor White
Write-Host "   • O ejecuta manualmente: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Características:" -ForegroundColor Cyan
Write-Host "   • Asistente de estudio con IA offline" -ForegroundColor White
Write-Host "   • Soporta PDF, Word, TXT, Markdown" -ForegroundColor White
Write-Host "   • Optimizado para tu hardware" -ForegroundColor White
Write-Host "   • Completamente gratuito" -ForegroundColor White
Write-Host ""
Write-Host "🤖 Ollama está instalado" -ForegroundColor Cyan
Write-Host "   Ejecuta 'ollama pull phi3.5:latest' para el modelo recomendado" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: En el primer inicio se descargarán los modelos" -ForegroundColor Yellow
Write-Host "   y se configurará el entorno (puede tomar varios minutos)." -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "¿Deseas iniciar DiceSensei ahora? (S/N)"
if ($response -match '^[Ss]$') {
    Write-Host ""
    Write-Host "🚀 Iniciando DiceSensei..." -ForegroundColor Green
    Set-Location $INSTALL_DIR
    python main.py
}
else {
    Write-Host ""
    Write-Host "Puedes iniciar DiceSensei desde los accesos directos en el escritorio." -ForegroundColor Cyan
}

Read-Host "Presiona Enter para salir"
# SIG # Begin signature block
# MIIFuwYJKoZIhvcNAQcCoIIFrDCCBagCAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUW58ayyi5sep1Tzq4gM53ScUd
# uxmgggM8MIIDODCCAiCgAwIBAgIQaCuysGAN2adPdvIcv1dN/jANBgkqhkiG9w0B
# AQsFADA0MQswCQYDVQQGEwJDTDETMBEGA1UECgwKRGljZVNlbnNlaTEQMA4GA1UE
# AwwHT2VsTm9vYzAeFw0yNTExMDcxNDQ2MDBaFw0yODExMDcxNDU2MDBaMDQxCzAJ
# BgNVBAYTAkNMMRMwEQYDVQQKDApEaWNlU2Vuc2VpMRAwDgYDVQQDDAdPZWxOb29j
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAze67l6/g+cu3nVO+FUIr
# jy886eXxqq1+pjEtx8Zpum8vgMiSvZ+MT7pgScsxFiUrLwGbc1IUSqtFF22LylGX
# QtcXPQmCmVoOsB4cc5akmcZkzBmSWofvyMmCYLth7SMF2iMVhNlbCJ7J0Q+NAEyl
# 9esCKNf59TmDGPIrBpEW7QqiWp47kadyxdwDJl+GXcIfbId6050Yo3nLMQWoUSuJ
# EIexInnLQ0X9Ci9gcl6Xvi3NvgdTjN6JH4hBXwScoIXp+IYNGmYmXTMPVC0LKlMg
# 9qLlNb0H8rE+Sq5kn+Dr6ppA85pdo5uwW6GO0Fze3tEY1N4R9MKo8K7B3CyLP8JB
# /QIDAQABo0YwRDAOBgNVHQ8BAf8EBAMCB4AwEwYDVR0lBAwwCgYIKwYBBQUHAwMw
# HQYDVR0OBBYEFEsaxiiH4vwcsiSncw2cuVCvdi/NMA0GCSqGSIb3DQEBCwUAA4IB
# AQCLlFWBR0A11fPzn5nzw7vR6+tTrrofI40ElMO9fqKjrf2uG4BH+i9lECMvL5W5
# hpy9VWEaCpDHiDWFH9rmdE+iRGnYcZW79cFKP/E2vM0M275BurPdqdKs2BaYA9Sn
# KWYcvxLG18GrW3cQdoA+LVr3vRRpxrz6IImTL/narqJPD6mKIFGzqq3Z3otVB6yv
# G15ajSHkJuBpc9kUE8szJnFGH5hgEDnLBzb/k+E9HYXI54Z/cnjPrbypU/cy9VaT
# ZyfRG6qgxgMemXWPnYdF4VDDLhzw9cHxp0RpCUclK5+kl6rEeASEZ7r9Km3J0Eap
# Xqik9AfClpL5/UR23h6wkkgRMYIB6TCCAeUCAQEwSDA0MQswCQYDVQQGEwJDTDET
# MBEGA1UECgwKRGljZVNlbnNlaTEQMA4GA1UEAwwHT2VsTm9vYwIQaCuysGAN2adP
# dvIcv1dN/jAJBgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZ
# BgkqhkiG9w0BCQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYB
# BAGCNwIBFTAjBgkqhkiG9w0BCQQxFgQUTZ3ZmRh//j+25eZ7HeSKOcgYMBAwDQYJ
# KoZIhvcNAQEBBQAEggEAeya3FxsHlauYeoVyCmEjKu5zWCELCl9RG+6BUTZFuyHq
# Wz0MXi4sjJW5uRjAG9CnlXy9lW/nWttyo6Mbm7Xrk8F5U1gmrwUswPHb8r+N0HQG
# zSCRUYVuPke0yA4UtLR1rUraFSeBGBT5et2KcWcD26a0MIOGFZ/ID7WpmMibzDeb
# QWg6BfKiSh/hNhGkjCGJdlknqv4Y+BHvSOkkMMsrGzv6020tkdvifbCi8i6Rf3oU
# qpv6Z4zKKWDIFBDDstU4B8HjwXPgb08krqB3iuDsd4OFGbkESu5e3o9c7UY5Sr93
# eDMJNPOmzcluVr+cRgjFyqOBdGjcHDS7UECzEJfaNw==
# SIG # End signature block
