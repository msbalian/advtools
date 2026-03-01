@echo off
setlocal
set DB_NAME=advtools
set DB_USER=postgres
set BACKUP_FILE=database_full_backup.sql

echo [+] Realizando backup total do banco %DB_NAME% (Schema + Dados)...
pg_dump -h localhost -U %DB_USER% -d %DB_NAME% > %BACKUP_FILE%

if %ERRORLEVEL% equ 0 (
    echo [OK] Backup realizado com sucesso em: %BACKUP_FILE%
) else (
    echo [ERRO] Falha ao realizar backup. Verifique se o PostgreSQL esta no PATH.
)
pause
