$ws = New-Object -ComObject WScript.Shell
$startup = $ws.SpecialFolders("Startup")
$shortcutPath = Join-Path $startup "WeatherTrayApp.lnk"
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "c:\Users\anuru\Desktop\OIBSIP\WeatherTrayApp\start_weather.pyw"
$shortcut.WorkingDirectory = "c:\Users\anuru\Desktop\OIBSIP\WeatherTrayApp"
$shortcut.Description = "Weather Tray App - System Tray Weather"
$shortcut.Save()
Write-Host "Startup shortcut created at: $shortcutPath"
