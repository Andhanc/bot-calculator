#!/bin/bash
# Скрипт для установки и настройки бота на сервере

echo "🚀 Начинаем установку бота..."

# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git

# Устанавливаем PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создаем пользователя и базу данных
echo "📦 Настройка PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE USER mainer_user WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE mainercrypto OWNER mainer_user;
GRANT ALL PRIVILEGES ON DATABASE mainercrypto TO mainer_user;
\q
EOF

# Создаем директорию для бота
BOT_DIR="/opt/mainercrypto"
sudo mkdir -p $BOT_DIR
sudo chown $USER:$USER $BOT_DIR

# Клонируем или копируем проект
echo "📥 Копирование файлов проекта..."
# Если используете git:
# git clone <your-repo-url> $BOT_DIR
# Или просто скопируйте файлы проекта в $BOT_DIR

# Создаем виртуальное окружение
cd $BOT_DIR
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r req.txt

# Создаем .env файл (нужно будет заполнить вручную)
if [ ! -f .env ]; then
    cat > .env <<EOF
BOT_TOKEN=your_bot_token_here
POSTGRES_USER=mainer_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=localhost
POSTGRES_NAME=mainercrypto
ADMIN_IDS=6177558353
EOF
    echo "⚠️  Не забудьте заполнить .env файл!"
fi

# Создаем systemd service
sudo tee /etc/systemd/system/mainercrypto.service > /dev/null <<EOF
[Unit]
Description=MainerCrypto Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
sudo systemctl daemon-reload

echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano $BOT_DIR/.env"
echo "2. Запустите бота: sudo systemctl start mainercrypto"
echo "3. Включите автозапуск: sudo systemctl enable mainercrypto"
echo "4. Проверьте статус: sudo systemctl status mainercrypto"
echo "5. Просмотрите логи: sudo journalctl -u mainercrypto -f"

