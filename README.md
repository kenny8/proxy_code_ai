# Claude Desktop

GUI приложение для запуска локального сервера прокси и Claude Code через удобную кнопку-интерфейс.

## Описание

Это приложение позволяет запускать кастомный UVicorn сервер (прокси) и подключать к нему Claude Code через графический интерфейс, без необходимости работать с командной строкой.

## Особенности

- **Запуск сервера** —一键 запуск UVicorn сервера на `localhost:8082` с debug-логированием
- **Выбор рабочей папки** — возможность выбрать любую директорию для запуска Claude
- **Запуск Claude Code** — автоматический запуск Claude с настройкой переменных окружения
- **Остановка сервера** — корректное завершение процессов сервера
- **Справка** — все команды для копирования в одном месте

## Структура проекта

```
claude-desktop-app/
├── main.py           # Основное GUI приложение
├── requirements.txt  # Зависимости Python
├── build.spec        # Конфигурация PyInstaller для сборки .exe
├── icon.ico          # Иконка приложения
└── README.md         # Эта документация
```

## Требования

- Python 3.10 или выше
- uv (менеджер пакетов Python)
- claude CLI установлен globally

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt
```

## Запуск из исходного кода

```bash
python main.py
```

## Сборка в executable (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ClaudeDesktop" --icon=icon.ico main.py
```

Готовый `.exe` файл будет в папке `dist/ClaudeDesktop.exe`

## Использование

1. **Запуск сервера**
   - Нажми кнопку "Запуск сервера"
   - Откроется отдельное окно PowerShell с запущенным UVicorn сервером
   - Сервер работает на `http://localhost:8082`

2. **Выбор папки (опционально)**
   - По умолчанию используется `D:/agent_work_claud/agent_workspace`
   - Нажми "Выбрать папку" чтобы изменить рабочую директорию

3. **Запуск Claude Code**
   - Убедись что сервер запущен
   - Нажми "Запуск Claude"
   - Откроется окно PowerShell с запущенным Claude Code

4. **Остановка сервера**
   - Нажми "Остановить сервер" чтобы завершить работу сервера

## Команды которые использует приложение

### Запуск сервера
```bash
cd D:/free-claude-code && uv run uvicorn server:app --host 0.0.0.0 --port 8082 --log-level debug
```

### Запуск Claude
```powershell
$env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; cd "ПАПКА"; claude
```

## Переменные окружения

| Переменная | Значение | Описание |
|------------|----------|----------|
| `ANTHROPIC_AUTH_TOKEN` | `freecc` | Токен аутентификации |
| `ANTHROPIC_BASE_URL` | `http://localhost:8082` | Адрес локального прокси-сервера |

## Зависимости

- `customtkinter` — современная библиотека для GUI
- `packaging` — поддержка версий пакетов

## Ссылки

- Исходный код сервера: https://github.com/Alishahryar1/free-claude-code
- Репозиторий этого проекта: https://github.com/kenny8/proxy_code_ai

## Лицензия

MIT
