@echo off
echo ==========================================
echo GERANDO EXECUTAVEL DO ADVTOOLS (SAAS)
echo ==========================================

REM Limpa builds anteriores
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

REM Instala PyInstaller se nao tiver (silencioso)
pip install pyinstaller >nul 2>&1

REM Comando PyInstaller
REM --onefile: Gera um unico arquivo .exe
REM --noconsole: Remove a janela preta (Opcional, deixei sem para ver erros no inicio)
REM --add-data: Inclui pastas templates, static e modelos dentro do exe

echo Empacotando arquivos...
pyinstaller --name "ADVtools_SAAS" ^
 --add-data "templates;templates" ^
 --add-data "static;static" ^
 --add-data "modelos;modelos" ^
 --onefile app.py

echo.
echo ==========================================
echo SUCESSO! O arquivo esta na pasta 'dist'
echo ==========================================
pause
