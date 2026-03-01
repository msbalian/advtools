@echo off
setlocal
set DB_NAME=advtools
set DB_USER=postgres
set BACKUP_FILE=database_full_backup.sql

if not exist %BACKUP_FILE% (
    echo [ERRO] Arquivo de backup nao encontrado: %BACKUP_FILE%
    pause
    exit /b 1
)

echo [!] ATENCAO: Isso ira sobrescrever os dados locais do banco %DB_NAME%.
set /p confirm="Deseja continuar? (S/N): "
if /i "%confirm%" neq "S" exit /b 0

echo [+] Restaurando banco %DB_NAME%...
psql -h localhost -U %DB_USER% -d %DB_NAME% < %BACKUP_FILE%

if %ERRORLEVEL% equ 0 (
    echo [OK] Restauracao concluida com sucesso!
) else (
    echo [ERRO] Falha ao restaurar banco.
)
pause
