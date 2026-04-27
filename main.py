"""
Claude Desktop - GUI приложение для запуска сервера и Claude Code
"""

import os
import subprocess
import sys
import threading
import tkinter as tkinter_std
from pathlib import Path

import customtkinter as tk
from tkinter import filedialog


class ClaudeDesktopApp(tk.CTk):
    def __init__(self):
        super().__init__()

        # Конфигурация окна
        self.title("Claude Desktop")
        self.geometry("600x400")
        self.minsize(500, 350)

        # Путь к папке с сервером
        self.SERVER_DIR = Path("D:/free-claude-code")

        # По умолчанию выбранная папка дляClaude Code
        self.DEFAULT_CLAUDE_DIR = Path("D:/agent_work_claud/agent_workspace")

        # Текущая выбранная папка
        self.selected_dir = self.DEFAULT_CLAUDE_DIR

        # Ссылка на процесс сервера
        self.server_process = None

        # Индикатор запущен ли сервер
        self.server_running = False

        # Настройка внешнего вида
        tk.set_appearance_mode("dark")
        tk.set_default_color_theme("blue")

        # Создание UI
        self.create_widgets()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = tk.CTkFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.CTkLabel(
            main_frame,
            text="Claude Desktop",
            font=tk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Блок с папкой
        dir_frame = tk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 15))

        dir_label = tk.CTkLabel(
            dir_frame,
            text="Рабочая папка:",
            font=tk.CTkFont(size=12)
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        # Поле с путем к папке
        self.dir_entry = tk.CTkEntry(
            dir_frame,
            textvariable=tk.StringVar(value=str(self.selected_dir)),
            state="disabled",
            font=tk.CTkFont(size=11),
            height=30
        )
        self.dir_entry.pack(fill="x", pady=(0, 5))

        # Кнопка выбора папки
        self.choose_dir_btn = tk.CTkButton(
            dir_frame,
            text="Выбрать папку",
            command=self.choose_directory,
            font=tk.CTkFont(size=11),
            height=30,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.choose_dir_btn.pack(fill="x")

        # Блок с кнопками управления
        btn_frame = tk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 15))

        # Кнопка управления сервером (переключатель)
        self.server_btn = tk.CTkButton(
            btn_frame,
            text="Запуск сервера",
            command=self.toggle_server,
            font=tk.CTkFont(size=13, weight="bold"),
            height=45,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.server_btn.pack(fill="x", pady=(0, 10))

        # Кнопка запуска Claude
        self.claude_btn = tk.CTkButton(
            btn_frame,
            text="Запуск Claude",
            command=self.start_claude,
            font=tk.CTkFont(size=13, weight="bold"),
            height=45,
            state="disabled",
            fg_color="blue",
            hover_color="darkblue"
        )
        self.claude_btn.pack(fill="x", pady=(0, 10))

        # Кнопка Справка
        help_btn = tk.CTkButton(
            btn_frame,
            text="Справка",
            command=self.show_help,
            font=tk.CTkFont(size=13, weight="bold"),
            height=45,
            fg_color="gray",
            hover_color="darkgray"
        )
        help_btn.pack(fill="x")

        # Статус-бар
        self.status_label = tk.CTkLabel(
            main_frame,
            text="Готов к работе",
            font=tk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_label.pack(side="bottom", pady=(15, 0))

    def show_help(self):
        """Показать окно справки с возможностью копирования"""
        help_window = tk.CTkToplevel(self)
        help_window.title("Справка")
        help_window.geometry("700x600")

        # Текстовое поле с полосой прокрутки
        text_frame = tk.CTkFrame(help_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        help_text = """=== КОМАНДЫ ЗАПУСКА ===

1. ЗАПУСК СЕРВЕРА:
   Команда: cd D:/free-claude-code && uv run uvicorn server:app --host 0.0.0.0 --port 8082 --log-level debug
   Описание: Запускает UVicorn сервер на порту 8082 с debug-логированием
   Папка: D:/free-claude-code

2. ЗАПУСК CLAUDE CODE:
   Команда: $env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; cd "ПАПКА"; claude
   Описание: Запускает Claude Code с подключением к локальному серверу
   Переменные окружения:
     - ANTHROPIC_AUTH_TOKEN="freecc" - токен аутентификации
     - ANTHROPIC_BASE_URL="http://localhost:8082" - адрес локального сервера

=== ИСПОЛЬЗОВАНИЕ ПРИЛОЖЕНИЯ ===

1. Нажмите "Опуск сервера" - откроется окно PowerShell с запущенным сервером
2. (Опционально) Нажмите "Выбрать папку" чтобы изменить рабочую директорию
3. Нажмите "Запуск Claude" - откроется окно PowerShell с Claude Code
4. Нажмите "Остановить сервер" чтобы остановить сервер

=== ПРИМЕЧАНИЯ ===

- Сначала нужно запустить сервер, затем Claude
- Сервер работает на http://localhost:8082
- PowerShell окно с сервером можно закрыть вручную если кнопка не сработала
- Выделите текст мышкой и нажмите Ctrl+C чтобы скопировать"""

        # Создаем стандартный Text widget с поддержкой выделения
        scrollbar = tkinter_std.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tkinter_std.Text(
            text_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True)

        scrollbar.config(command=text_widget.yview)
        text_widget.insert("1.0", help_text)

        # Отключаем редактирование но оставляем возможность выделения
        text_widget.config(state="disabled")

    def choose_directory(self):
        """Открыть диалог выбора папки"""
        directory = filedialog.askdirectory(
            initialdir=self.selected_dir,
            title="Выберите папку для запуска Claude"
        )
        if directory:
            self.selected_dir = Path(directory)
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.dir_entry.configure(state="disabled")
            self.status("Папка изменена на: " + directory)

    def toggle_server(self):
        """Переключатель запуска/остановки сервера"""
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        """Запустить UVicorn сервер"""
        if not self.SERVER_DIR.exists():
            self.error(f"Папка сервера не найдена: {self.SERVER_DIR}")
            return

        self.status("Запуск сервера...")
        self.server_btn.configure(state="disabled")

        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

    def _run_server(self):
        """Внутренний метод запуска сервера"""
        try:
            # Создаем bat файл для запуска сервера
            bat_content = '''@echo off
cd /d D:\\free-claude-code
uv run uvicorn server:app --host 0.0.0.0 --port 8082 --log-level debug
pause
'''
            bat_path = self.SERVER_DIR / "start_server.bat"
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)

            # Запускаем bat в новом окне
            self.server_process = subprocess.Popen(
                str(bat_path),
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            self.server_running = True

            # Обновить UI в главном потоке
            self.after(0, self._on_server_started)

        except Exception as e:
            self.after(0, lambda: self.error(f"Ошибка запуска сервера: {e}"))
            self.after(0, lambda: self._set_server_btn_state(False))

    def _on_server_started(self):
        """Обновление UI после запуска сервера"""
        self.server_btn.configure(
            text="Остановить сервер",
            state="normal",
            fg_color="red",
            hover_color="darkred"
        )
        self.claude_btn.configure(state="normal")
        self.status("Сервер запущен на http://localhost:8082")

    def stop_server(self):
        """Остановить сервер"""
        if self.server_process and self.server_process.poll() is None:
            # На Windows используем taskkill для завершения дерева процессов
            if sys.platform == "win32":
                try:
                    proc_pid = self.server_process.pid
                    subprocess.run(
                        f'taskkill /F /T /PID {proc_pid}',
                        shell=True,
                        capture_output=True,
                        encoding='cp1251'
                    )
                except Exception as e:
                    print(f"taskkill error: {e}")
                    self.server_process.kill()
            else:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()

        self.server_running = False
        self.server_process = None

        self._set_server_btn_state(False)
        self.claude_btn.configure(state="disabled")
        self.status("Сервер остановлен")

    def _set_server_btn_state(self, running):
        """Установить состояние кнопки сервера"""
        self.server_btn.configure(
            text="Запуск сервера",
            state="normal",
            fg_color="green",
            hover_color="darkgreen"
        )

    def start_claude(self):
        """Запустить Claude Code в выбранной папке"""
        if not self.server_running:
            self.error("Сначала запустите сервер!")
            return

        if not self.selected_dir.exists():
            self.error(f"Папка не существует: {self.selected_dir}")
            return

        self.status("Запуск Claude Code...")

        # Запуск PowerShell окна с командой Claude
        cmd = [
            "powershell",
            "-NoExit",
            "-Command",
            f'$env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; cd "{self.selected_dir}"; claude'
        ]

        try:
            # Запуск с видимым окном
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status("Claude Code запущен")
        except Exception as e:
            self.error(f"Ошибка запуска Claude: {e}")

    def status(self, message):
        """Обновить статус в статус-баре"""
        self.status_label.configure(text=message)

    def error(self, message):
        """Показать сообщение об ошибке"""
        self.status(message)
        print(f"ERROR: {message}")

    def on_closing(self):
        """Обработка закрытия окна"""
        if self.server_running and self.server_process:
            self.server_process.terminate()
        self.destroy()


def main():
    app = ClaudeDesktopApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
