@echo off
chcp 65001 >nul
echo Добавление файлов в индекс...
git add handlers/client.py utils/coin_service.py utils/calculator.py utils/ai_service.py
echo Создание коммита...
git commit -m "Удалена строка с курсом доллара из сообщений бота"
echo Получение изменений с удаленного репозитория...
git pull --rebase origin main
if %errorlevel% neq 0 (
    echo Ошибка при pull. Возможно есть конфликты. Разрешите их и выполните: git rebase --continue
    pause
    exit /b 1
)
echo Отправка изменений на GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo Ошибка при push. Проверьте статус: git status
    pause
    exit /b 1
)
echo Успешно отправлено на GitHub!
pause
