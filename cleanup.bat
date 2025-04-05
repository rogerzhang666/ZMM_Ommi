@echo off
echo 正在清理项目结构...
rd /s /q "%~dp0%%USERPROFILE%%"
echo 清理完成！
pause
