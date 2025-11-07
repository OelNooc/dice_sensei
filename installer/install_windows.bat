@echo off
chcp 65001 >nul
title DiceSensei - Instalador de Windows

setlocal EnableDelayedExpansion

echo.
echo 🎲 DiceSensei - Asistente de Estudio Inteligente
echo ================================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ejecutando sin permisos de administrador...
    echo    Algunas funciones pueden estar limitadas.
    echo.
)

set "INSTALL_DIR=%USERPROFILE%\DiceSensei"
set "TEMP_ZIP=%TEMP%\dicesensei-windows.zip"
set "OLLAMA_INSTALLER=%TEMP%\OllamaSetup.exe"

echo 📍 Directorio de instalacion: %INSTALL_DIR%
echo.

if exist "%INSTALL_DIR%" (
    echo 🔄 Eliminando instalacion previa...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
    if exist "%INSTALL_DIR%" (
        echo ❌ No se pudo eliminar la instalacion anterior.
        echo    Cierra DiceSensei si esta ejecutandose y vuelve a intentar.
        pause
        exit /b 1
    )
)

mkdir "%INSTALL_DIR%" 2>nul
if not exist "%INSTALL_DIR%" (
    echo ❌ No se pudo crear el directorio de instalacion.
    pause
    exit /b 1
)

echo 📥 Descargando DiceSensei...
powershell -Command "& {
    try {
        Write-Host '    Descargando desde GitHub...' -ForegroundColor Cyan
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri 'https://github.com/OelNooc/dice_sensei/releases/latest/download/dicesensei-windows.zip' -OutFile '%TEMP_ZIP%'
        if (Test-Path '%TEMP_ZIP%') {
            Write-Host '    ✅ Descarga completada' -ForegroundColor Green
        } else {
            Write-Host '    ❌ Error en la descarga' -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host '    ❌ Error: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}"

if errorlevel 1 (
    echo ❌ Error descargando DiceSensei
    echo    Verifica tu conexion a internet.
    pause
    exit /b 1
)

echo 📦 Extrayendo archivos...
powershell -Command "& {
    try {
        Write-Host '    Extrayendo archivos...' -ForegroundColor Cyan
        Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%INSTALL_DIR%' -Force
        Write-Host '    ✅ Extraccion completada' -ForegroundColor Green
    }
    catch {
        Write-Host '    ❌ Error extrayendo: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}"

if errorlevel 1 (
    echo ❌ Error extrayendo los archivos
    pause
    exit /b 1
)

if exist "%TEMP_ZIP%" del "%TEMP_ZIP%"

echo 🤖 Verificando Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo 📥 Ollama no detectado, instalando...
    powershell -Command "& {
        try {
            Write-Host '    Descargando Ollama...' -ForegroundColor Cyan
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri 'https://ollama.ai/download/OllamaSetup.exe' -OutFile '%OLLAMA_INSTALLER%'
            
            if (Test-Path '%OLLAMA_INSTALLER%') {
                Write-Host '    Instalando Ollama (esto puede tomar unos minutos)...' -ForegroundColor Cyan
                $process = Start-Process -FilePath '%OLLAMA_INSTALLER%' -ArgumentList '/S' -Wait -PassThru
                
                if ($process.ExitCode -eq 0) {
                    Write-Host '    ✅ Ollama instalado correctamente' -ForegroundColor Green
                } else {
                    Write-Host '    ⚠️  Ollama instalado con advertencias' -ForegroundColor Yellow
                }
            }
        }
        catch {
            Write-Host '    ⚠️  Error instalando Ollama: ' $_.Exception.Message -ForegroundColor Yellow
            Write-Host '    Puedes instalarlo manualmente desde: https://ollama.ai/' -ForegroundColor Yellow
        }
        finally {
            if (Test-Path '%OLLAMA_INSTALLER%') {
                Remove-Item '%OLLAMA_INSTALLER%' -Force
            }
        }
    }"
) else (
    echo ✅ Ollama ya esta instalado
)

echo 📦 Instalando dependencias de Python...
cd /d "%INSTALL_DIR%"

python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python no encontrado en el PATH
    echo    Instalando Python automaticamente...
    
    powershell -Command "& {
        try {
            $pythonInstaller = Join-Path $env:TEMP 'python_installer.exe'
            Write-Host '    Descargando Python...' -ForegroundColor Cyan
            Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile $pythonInstaller
            
            if (Test-Path $pythonInstaller) {
                Write-Host '    Instalando Python...' -ForegroundColor Cyan
                Start-Process -FilePath $pythonInstaller -ArgumentList '/quiet', 'InstallAllUsers=0', 'Include_launcher=0', 'PrependPath=1' -Wait
                Write-Host '    ✅ Python instalado' -ForegroundColor Green
                Remove-Item $pythonInstaller -Force
            }
        }
        catch {
            Write-Host '    ❌ Error instalando Python' -ForegroundColor Red
            Write-Host '    Instala Python manualmente desde: https://python.org' -ForegroundColor Yellow
        }
    }"
    
    for /f "skip=2 tokens=1-2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%c"
    set "PATH=%USER_PATH%;%PATH%"
)

echo     Actualizando pip...
python -m pip install --upgrade pip --quiet

echo     Instalando paquetes requeridos...
python -m pip install requests pypdf2 pypdf python-docx markdown psutil --quiet

if errorlevel 1 (
    echo ⚠️  Algunas dependencias no se pudieron instalar automaticamente
    echo    Se intentaran instalar durante el primer inicio.
)

echo 🎯 Creando accesos directos...

echo @echo off > "%USERPROFILE%\Desktop\DiceSensei.bat"
echo chcp 65001 >nul >> "%USERPROFILE%\Desktop\DiceSensei.bat"
echo cd /d "%INSTALL_DIR%" >> "%USERPROFILE%\Desktop\DiceSensei.bat"
echo echo Iniciando DiceSensei... >> "%USERPROFILE%\Desktop\DiceSensei.bat"
echo python main.py >> "%USERPROFILE%\Desktop\DiceSensei.bat"
echo pause >> "%USERPROFILE%\Desktop\DiceSensei.bat"

powershell -Command "& {
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\DiceSensei.lnk')
        $Shortcut.TargetPath = 'python'
        $Shortcut.Arguments = 'main.py'
        $Shortcut.WorkingDirectory = '%INSTALL_DIR%'
        $Shortcut.IconLocation = '%INSTALL_DIR%\assets\icons\dicesensei.ico'
        $Shortcut.Description = 'DiceSensei - Asistente de Estudio Inteligente'
        $Shortcut.Save()
        Write-Host '    ✅ Acceso directo creado (DiceSensei.lnk)' -ForegroundColor Green
    }
    catch {
        Write-Host '    ⚠️  No se pudo crear el acceso directo .lnk' -ForegroundColor Yellow
    }
}"

echo # DiceSensei Launcher > "%USERPROFILE%\Desktop\DiceSensei.ps1"
echo Set-Location -Path "%INSTALL_DIR%" >> "%USERPROFILE%\Desktop\DiceSensei.ps1"
echo python main.py >> "%USERPROFILE%\Desktop\DiceSensei.ps1"
echo Read-Host 'Presiona Enter para salir' >> "%USERPROFILE%\Desktop\DiceSensei.ps1"

echo.
echo ✅ ¡DiceSensei instalado correctamente!
echo.
echo 📁 Ubicacion: %INSTALL_DIR%
echo.
echo 🚀 Para iniciar DiceSensei:
echo    • Doble clic en "DiceSensei.bat" en tu escritorio
echo    • O ejecuta manualmente: python main.py
echo.
echo 📚 Caracteristicas:
echo    • Asistente de estudio con IA offline
echo    • Soporta PDF, Word, TXT, Markdown
echo    • Optimizado para tu hardware
echo    • Completamente gratuito
echo.
echo 🤖 Ollama esta instalado
echo    Ejecuta "ollama pull phi3.5:latest" para el modelo recomendado
echo.
echo ⚠️  IMPORTANTE: En el primer inicio se descargaran los modelos
echo    y se configurara el entorno (puede tomar varios minutos).
echo.

if not exist "%INSTALL_DIR%\config" mkdir "%INSTALL_DIR%\config"

echo ¿Deseas iniciar DiceSensei ahora? (S/N)
choice /C SN /N /M "Selecciona una opcion"
if errorlevel 2 (
    echo.
    echo Puedes iniciar DiceSensei desde los accesos directos en el escritorio.
    pause
    exit /b 0
)

echo.
echo 🚀 Iniciando DiceSensei...
cd /d "%INSTALL_DIR%"
python main.py

pause