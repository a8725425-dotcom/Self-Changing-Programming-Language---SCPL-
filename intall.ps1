# install.ps1 — установка SCPL на Windows
$Repo = "a8725425-dotcom/Self-Changing-Programming-Language---SCPL"
$InstallDir = "$env:USERPROFILE\.local\share\scpl"
$BinDir = "$env:USERPROFILE\.local\bin"
$ScplCmd = "$BinDir\scpl.bat"

Write-Host "[SCPL] Installing files to $InstallDir ..." -ForegroundColor Cyan

# Создаём папки
New-Item -ItemType Directory -Force -Path $InstallDir, $BinDir | Out-Null

# Скачиваем ZIP
$ZipPath = "$env:TEMP\scpl.zip"
Write-Host "[SCPL] Downloading..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $ZipPath
Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force
Remove-Item $ZipPath

# Убираем папку-обёртку
$ExtractedFolder = Get-ChildItem $InstallDir -Directory | Where-Object { $_.Name -like "Self-Changing-Programming-Language---SCPL*" }
if ($ExtractedFolder) {
    Move-Item "$($ExtractedFolder.FullName)\*" $InstallDir -Force
    Remove-Item $ExtractedFolder.FullName -Recurse
}

# Спрашиваем про PATH
Write-Host ""
Write-Host "Добавить CLI в PATH для быстрого доступа (команда 'scpl')?" -ForegroundColor Yellow
Write-Host "  1) Да (рекомендуется)"
Write-Host "  2) Нет, буду запускать через python"
$choice = Read-Host "Выберите (1/2)"

if ($choice -eq "2") {
    Write-Host ""
    Write-Host "[SCPL] Установка завершена без добавления в PATH." -ForegroundColor Green
    Write-Host "Запуск: python $InstallDir\scpl_cli.py repl"
    Write-Host ""
    Write-Host "Алиас (временный, на сессию):"
    Write-Host "  doskey scpl=python `$env:USERPROFILE\.local\share\scpl\scpl_cli.py `$*"
} else {
    # Создаём .bat обёртку
    @"
@echo off
python "$InstallDir\scpl_cli.py" %*
"@ | Out-File -FilePath $ScplCmd -Encoding ascii

    # Добавляем в PATH для текущей сессии
    $env:Path = "$BinDir;$env:Path"
    
    # Показываем, как добавить постоянно
    Write-Host ""
    Write-Host "[SCPL] Установка завершена!" -ForegroundColor Green
    Write-Host "Команда 'scpl' добавлена в PATH для текущего терминала." -ForegroundColor Green
    Write-Host ""
    Write-Host "Чтобы 'scpl' работал всегда, добавьте в PATH: $BinDir" -ForegroundColor Yellow
    Write-Host "В PowerShell это можно сделать командой (один раз):" -ForegroundColor Yellow
    Write-Host "  [Environment]::SetEnvironmentVariable('Path', `$env:Path + ';$BinDir', 'User')" -ForegroundColor White
    Write-Host ""
    Write-Host "Запуск: scpl repl"
}

Write-Host ""
Write-Host "Установленные файлы: $InstallDir" 
