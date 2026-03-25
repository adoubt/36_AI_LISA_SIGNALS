Вот полный, готовый к вставке Markdown для README, минималистичный и полностью ориентированный на Ubuntu:

````markdown
# LISA SIGNALS BOT

## Быстрый старт на Ubuntu

1. Подключиться к серверу через SSH.
2. Установить Python и Git:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git -y
````

3. Создать папку для бота и перейти в неё:

```bash
mkdir ~/bot
cd ~/bot
```

4. Клонировать репозиторий:

```bash
git clone https://github.com/adoubt/36_AI_LISA_SIGNALS.git .
```

5. Создать виртуальное окружение и активировать его:

```bash
python3 -m venv venv
source venv/bin/activate
```

6. Установить зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

7. Создать файл `.env` в корне папки бота с содержимым:

```env
PASSWORD=любой_пароль_для_админа
BOT_TOKEN=токен_бота
```

8. Запустить бота на фоне:

```bash
screen -S earnbot
python3 main.py
# Ctrl+A, D — отсоединиться, бот будет работать в фоне
```

## Обновление бота

1. Перейти в папку бота:

```bash
cd ~/bot
```

2. Остановить бота:

```bash
screen -r earnbot   # вернуться к сессии
Ctrl+C               # остановить процесс
```

3. Обновить репозиторий:

```bash
git pull
```

4. При необходимости обновить зависимости:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

5. Запустить бота снова:

```bash
screen -S earnbot
python3 main.py
```

## Вход в админку

Использовать команду в Telegram:

```text
/admin_hochu<ПАРОЛЬ>
```

