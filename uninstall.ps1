# uninstall.ps1 — полное удаление SCPL для Windows

$InstallDir = "$env:USERPROFILE\.local\share\scpl"
$BinDir = "$env:USERPROFILE\.local\bin"
$ScplCmd = "$BinDir\scpl.bat"
$ConfigDir = "$env:USERPROFILE\.config\scpl"
$CacheDir = "$env:USERPROFILE\.cache\scpl"

Write-Host "[SCPL] Windows uninstallation" -ForegroundColor Cyan

# Удаляем основную директорию
if (Test-Path $InstallDir) {
    Write-Host "Removing $InstallDir ..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $InstallDir
    Write-Host "✓ Main directory removed" -ForegroundColor Green
} else {
    Write-Host "✗ Main directory not found" -ForegroundColor Red
}

# Удаляем исполняемый файл
if (Test-Path $ScplCmd) {
    Write-Host "Removing $ScplCmd ..." -ForegroundColor Yellow
    Remove-Item -Force $ScplCmd
    Write-Host "✓ Executable removed" -ForegroundColor Green
} else {
    Write-Host "✗ Executable not found" -ForegroundColor Red
}

# Удаляем конфиги
if (Test-Path $ConfigDir) {
    Write-Host "Removing $ConfigDir ..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $ConfigDir
    Write-Host "✓ Config directory removed" -ForegroundColor Green
}

# Удаляем кэш
if (Test-Path $CacheDir) {
    Write-Host "Removing $CacheDir ..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $CacheDir
    Write-Host "✓ Cache directory removed" -ForegroundColor Green
}

# Удаляем из PATH (пользовательский)
Write-Host ""
Write-Host "Do you want to remove $BinDir from system PATH?" -ForegroundColor Yellow
Write-Host "  1) Yes, remove from PATH"
Write-Host "  2) No, keep PATH as is"
$choice = Read-Host "Choose (1/2)"

if ($choice -eq "1") {
    # Получаем текущий PATH пользователя
    $oldPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    
    # Удаляем $BinDir из PATH
    $newPath = ($oldPath -split ';' | Where-Object { $_ -ne $BinDir }) -join ';'
    
    # Сохраняем изменения
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    
    # Обновляем для текущей сессии
    $env:Path = $newPath
    
    Write-Host "✓ PATH updated for current and future sessions" -ForegroundColor Green
    Write-Host "  You may need to restart terminal for changes to take effect" -ForegroundColor Yellow
}

# Удаляем пустую директорию bin
if ((Test-Path $BinDir) -and ((Get-ChildItem $BinDir -Force).Count -eq 0)) {
    Write-Host "Removing empty $BinDir ..." -ForegroundColor Yellow
    Remove-Item $BinDir -Force
    Write-Host "✓ Empty bin directory removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[SCPL] Uninstallation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Removed:" -ForegroundColor Cyan
Write-Host "  - $InstallDir"
Write-Host "  - $ScplCmd"
Write-Host "  - $ConfigDir"
Write-Host "  - $CacheDir"
Write-Host ""
Write-Host "Note: If you had libraries installed via MLIS, they were in libs/ subdirectory"
Write-Host "      and have been removed with the main directory."
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
