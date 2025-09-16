@echo off
echo 🚀 创建Echopolis桌面快捷方式...

set "current_dir=%~dp0"
set "desktop=%USERPROFILE%\Desktop"
set "shortcut_name=Echopolis 回声都市.lnk"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\%shortcut_name%'); $Shortcut.TargetPath = '%current_dir%start_app.bat'; $Shortcut.WorkingDirectory = '%current_dir%'; $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,21'; $Shortcut.Description = 'Echopolis 一键启动'; $Shortcut.Save()}"

if exist "%desktop%\%shortcut_name%" (
    echo ✅ 桌面快捷方式创建成功！
    echo 📍 位置: %desktop%\%shortcut_name%
    echo 💡 现在可以双击桌面上的"Echopolis 回声都市"图标启动游戏
) else (
    echo ❌ 快捷方式创建失败
)

pause