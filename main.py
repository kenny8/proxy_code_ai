"""
Claude Desktop - GUI приложение для запуска сервера и Claude Code
"""

import os
import subprocess
import sys
import threading
import tkinter as tkinter_std
import webbrowser
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog


class ClaudeDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка темы
        ctk.set_appearance_mode("dark")
        theme_path = Path(__file__).parent / "theme.json"
        if theme_path.exists():
            ctk.set_default_color_theme(str(theme_path))

        # Конфигурация окна
        self.title("Claude Desktop")
        self.geometry("720x640")
        self.minsize(600, 540)

        # Иконка окна
        self._icon_path = self._find_icon()
        if self._icon_path:
            self.iconbitmap(self._icon_path)

        # Пути
        self.SERVER_DIR = Path("D:/free-claude-code")
        self.proxy_dir = self.SERVER_DIR
        self.DEFAULT_CLAUDE_DIR = Path("D:/agent_work_claud/agent_workspace")
        self.selected_dir = self.DEFAULT_CLAUDE_DIR

        # Процесс и состояние
        self.server_process = None
        self.server_running = False
        self._animating = False
        self._dot_count = 0
        self._log_visible = False
        self._log_buffer = []
        self._log_thread = None

        # UI
        self.create_widgets()

    # ─── Построение интерфейса ─────────────────────────────────

    def create_widgets(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=(20, 12))

        # Ряд: слева — основное, справа — логи
        content_row = ctk.CTkFrame(main, fg_color="transparent")
        content_row.pack(fill="both", expand=True)

        left_area = ctk.CTkFrame(content_row, fg_color="transparent")
        left_area.pack(side="left", fill="both", expand=True)

        # Шапка
        self._build_header(left_area)

        # Карточка: Папки
        self._build_folder_card(left_area)

        # Карточка: Управление
        self._build_controls_card(left_area)

        # Карточка: Статус сервера
        self._build_status_card(left_area)

        # Панель логов (справа, скрыта по умолчанию)
        self._build_log_panel(content_row)

        # Статус-бар
        self._build_status_bar(main)

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="🚀 Claude Desktop",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Локальный сервер Claude Code",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(anchor="w", pady=(2, 0))

    def _build_folder_card(self, parent):
        card = ctk.CTkFrame(parent, border_width=1, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card,
            text="📁 Рабочие папки",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=16, pady=(14, 10))

        # Строка рабочей папки
        self.dir_entry = self._make_dir_row(
            card, "Рабочая папка:", str(self.selected_dir), self.choose_directory
        )

        # Строка папки прокси
        self.proxy_entry = self._make_dir_row(
            card, "Папка прокси:", str(self.proxy_dir), self.choose_proxy_directory
        )

        ctk.CTkLabel(card, text="", height=6, fg_color="transparent").pack()

    def _make_dir_row(self, parent, label, initial_value, command):
        """Создаёт строку: подпись + поле + кнопка выбора"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            row,
            text=label,
            width=110,
            anchor="w",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 8))

        entry = ctk.CTkEntry(
            row,
            font=ctk.CTkFont(size=11),
            height=34,
            state="disabled"
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        entry.configure(textvariable=ctk.StringVar(value=initial_value))

        btn = ctk.CTkButton(
            row,
            text="📁",
            width=38,
            height=34,
            command=command,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        btn.pack(side="left")

        return entry

    def _build_controls_card(self, parent):
        card = ctk.CTkFrame(parent, border_width=1, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card,
            text="🎮 Управление",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=16, pady=(14, 10))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        # Ряд: кнопка сервера + переключатель Debug
        server_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
        server_row.pack(fill="x", pady=(0, 8))

        # Кнопка сервера (переключатель)
        self.server_btn = ctk.CTkButton(
            server_row,
            text="▶  Запуск сервера",
            command=self.toggle_server,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48,
            corner_radius=10,
            fg_color="#059669",
            hover_color="#047857"
        )
        self.server_btn.pack(side="left", fill="x", expand=True)

        # Переключатель Debug
        debug_frame = ctk.CTkFrame(server_row, fg_color="transparent")
        debug_frame.pack(side="right", padx=(14, 0))

        ctk.CTkLabel(
            debug_frame,
            text="🐞 Debug",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(anchor="center")

        self.debug_switch = ctk.CTkSwitch(
            debug_frame,
            text="",
            width=38,
            height=20
        )
        self.debug_switch.select()  # По умолчанию debug включён
        self.debug_switch.pack(pady=(2, 0))

        # Кнопка Claude Code
        self.claude_btn = ctk.CTkButton(
            btn_frame,
            text="🤖  Claude Code",
            command=self.start_claude,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48,
            state="disabled",
            corner_radius=10
        )
        self.claude_btn.pack(fill="x", pady=(0, 8))

        # Админ-панель + Логи + Справка в ряд
        row2 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        row2.pack(fill="x")

        self.admin_btn = ctk.CTkButton(
            row2,
            text="🔗  Админ-панель",
            command=lambda: webbrowser.open("http://127.0.0.1:8082/admin"),
            font=ctk.CTkFont(size=13, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        )
        self.admin_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.log_btn = ctk.CTkButton(
            row2,
            text="📋  Логи",
            command=self.toggle_logs,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color="#334155",
            hover_color="#475569"
        )
        self.log_btn.pack(side="left", fill="x", expand=True, padx=(6, 6))

        self.help_btn = ctk.CTkButton(
            row2,
            text="?  Справка",
            command=self.show_help,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color="#334155",
            hover_color="#475569"
        )
        self.help_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _build_status_card(self, parent):
        card = ctk.CTkFrame(parent, border_width=1, corner_radius=12)
        card.pack(fill="x")

        ctk.CTkLabel(
            card,
            text="📊 Состояние сервера",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=16, pady=(14, 10))

        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=(0, 16))

        self.status_indicator = ctk.CTkLabel(
            status_row,
            text="⚫  Сервер не запущен",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        self.status_indicator.pack(side="left")

        self.status_port = ctk.CTkLabel(
            status_row,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#64748b"
        )
        self.status_port.pack(side="right")

    def _build_status_bar(self, parent):
        self._status_bar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._status_bar_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkFrame(self._status_bar_frame, height=1, fg_color="#1e1e30").pack(fill="x", pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            self._status_bar_frame,
            text="Готов к работе",
            font=ctk.CTkFont(size=10),
            text_color="#64748b"
        )
        self.status_label.pack(side="left")

    # ─── Выбор папок ──────────────────────────────────────────

    def choose_directory(self):
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
            self.status(f"📁 Рабочая папка: {directory}")

    def choose_proxy_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.proxy_dir,
            title="Выберите папку прокси"
        )
        if directory:
            self.proxy_dir = Path(directory)
            self.proxy_entry.configure(state="normal")
            self.proxy_entry.delete(0, "end")
            self.proxy_entry.insert(0, directory)
            self.proxy_entry.configure(state="disabled")
            self.status(f"📁 Папка прокси: {directory}")

    # ─── Сервер ───────────────────────────────────────────────

    def toggle_server(self):
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        if not self.proxy_dir.exists():
            self.error(f"Папка прокси не найдена: {self.proxy_dir}")
            return

        self.status("🟡 Запуск сервера...")
        self._update_status_indicator("🟡", "Запуск...", "#eab308")
        self.server_btn.configure(state="disabled")
        self._animating = True
        self._animate_dots()

        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

    def _run_server(self):
        try:
            self._clear_logs()

            log_level = "debug" if self.debug_switch.get() else "info"

            # Скрываем окно консоли uv на Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.server_process = subprocess.Popen(
                ["uv", "run", "uvicorn", "server:app",
                 "--host", "0.0.0.0", "--port", "8082",
                 "--log-level", log_level],
                cwd=str(self.proxy_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                startupinfo=startupinfo
            )

            self.server_running = True
            self.after(0, self._on_server_started)

            # Запускаем чтение логов в потоке
            self._log_thread = threading.Thread(target=self._read_server_logs, daemon=True)
            self._log_thread.start()

        except Exception as e:
            self.after(0, lambda: self.error(f"Ошибка запуска сервера: {e}"))
            self.after(0, lambda: self._set_server_stopped())

    def _on_server_started(self):
        self._animating = False
        self.server_btn.configure(
            text="⏹  Остановить сервер",
            state="normal",
            fg_color="#dc2626",
            hover_color="#b91c1c"
        )
        self.claude_btn.configure(state="normal")
        self._update_status_indicator("🟢", "Запущен • порт 8082", "#22c55e")
        self.status_port.configure(text="http://localhost:8082")
        self.status("🟢 Сервер запущен")

    def stop_server(self):
        if self.server_process and self.server_process.poll() is None:
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
        self._set_server_stopped()
        self.claude_btn.configure(state="disabled")
        self._update_status_indicator("🔴", "Остановлен", "#ef4444")
        self.status_port.configure(text="")
        self.status("🔴 Сервер остановлен")

    def _set_server_stopped(self):
        self._animating = False
        self.server_btn.configure(
            text="▶  Запуск сервера",
            state="normal",
            fg_color="#059669",
            hover_color="#047857"
        )

    def _animate_dots(self):
        if not self._animating:
            return
        count = self._dot_count % 3 + 1
        self._dot_count += 1
        dots = "." * count
        self._update_status_indicator("🟡", f"Запуск{dots}", "#eab308")
        self.after(500, self._animate_dots)

    # ─── Claude Code ──────────────────────────────────────────

    def start_claude(self):
        if not self.server_running:
            self.error("Сначала запустите сервер!")
            return

        if not self.selected_dir.exists():
            self.error(f"Папка не существует: {self.selected_dir}")
            return

        self.status("🤖 Запуск Claude Code...")

        cmd = [
            "powershell",
            "-NoExit",
            "-Command",
            f'$env:CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY="true"; $env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; cd "{self.selected_dir}"; claude'
        ]

        try:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status("🤖 Claude Code запущен")
        except Exception as e:
            self.error(f"Ошибка запуска Claude: {e}")

    # ─── Справка ──────────────────────────────────────────────

    def show_help(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Справка — Claude Desktop")
        help_window.geometry("720x620")
        help_window.after(100, help_window.focus)
        if self._icon_path:
            help_window.iconbitmap(self._icon_path)

        text_frame = ctk.CTkFrame(help_window, border_width=1)
        text_frame.pack(fill="both", expand=True, padx=16, pady=16)

        help_text = """=== КОМАНДЫ ЗАПУСКА ===

1. ЗАПУСК СЕРВЕРА:
   Команда: cd D:/free-claude-code && uv run uvicorn server:app --host 0.0.0.0 --port 8082 --log-level debug
   Описание: Запускает UVicorn сервер на порту 8082 с debug-логированием
   Папка: D:/free-claude-code

2. ЗАПУСК CLAUDE CODE:
   Команда: $env:CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY="true"; $env:ANTHROPIC_AUTH_TOKEN="freecc"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; cd "ПАПКА"; claude
   Описание: Запускает Claude Code с подключением к локальному серверу
   Переменные окружения:
     - CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY="true" — обнаружение моделей шлюза
     - ANTHROPIC_AUTH_TOKEN="freecc" — токен аутентификации
     - ANTHROPIC_BASE_URL="http://localhost:8082" — адрес локального сервера

=== ИСПОЛЬЗОВАНИЕ ПРИЛОЖЕНИЯ ===

1. Нажмите "Запуск сервера" — откроется окно PowerShell с запущенным сервером
2. (Опционально) Выберите рабочую папку для Claude Code
3. (Опционально) Выберите папку прокси (по умолчанию D:/free-claude-code)
4. Нажмите "Claude Code" — откроется окно PowerShell с Claude Code
5. Нажмите "Остановить сервер" чтобы остановить сервер

=== ПРИМЕЧАНИЯ ===

— Сначала нужно запустить сервер, затем Claude
— Сервер работает на http://localhost:8082
— Админ-панель: http://127.0.0.1:8082/admin
— PowerShell окно с сервером можно закрыть вручную, если кнопка не сработала
— Выделите текст мышкой и нажмите Ctrl+C чтобы скопировать"""

        scrollbar = ctk.CTkScrollbar(text_frame, orientation="vertical")
        scrollbar.pack(side="right", fill="y")

        text_widget = tkinter_std.Text(
            text_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            wrap="word",
            bg="#1a1a26",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            borderwidth=0,
            padx=14,
            pady=14
        )
        text_widget.pack(fill="both", expand=True)
        scrollbar.configure(command=text_widget.yview)

        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")

        # Явный обработчик Ctrl+C для копирования из disabled-состояния
        def _copy_help(event=None):
            try:
                text_widget.clipboard_clear()
                text_widget.clipboard_append(text_widget.selection_get())
            except tkinter_std.TclError:
                pass
            return "break"

        text_widget.bind("<Control-c>", _copy_help)
        text_widget.bind("<Control-C>", _copy_help)

    # ─── Логи ─────────────────────────────────────────────────

    def _build_log_panel(self, parent):
        self.log_frame = ctk.CTkFrame(parent, border_width=1, corner_radius=12, width=420)
        self.log_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.log_frame,
            text="📋 Логи сервера",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=14, pady=(14, 10))

        log_container = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        log_container.pack(fill="both", padx=14, pady=(0, 14))

        scrollbar = ctk.CTkScrollbar(log_container, orientation="vertical")
        scrollbar.pack(side="right", fill="y")

        self.log_text = tkinter_std.Text(
            log_container,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            wrap="word",
            bg="#0a0a0f",
            fg="#94a3b8",
            relief="flat",
            borderwidth=0,
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)
        scrollbar.configure(command=self.log_text.yview)

    def toggle_logs(self):
        self._log_visible = not self._log_visible
        cur_w = self.winfo_width()
        cur_h = self.winfo_height()

        if self._log_visible:
            self.log_frame.pack(side="right", fill="y", padx=(14, 0))
            self.geometry(f"{cur_w + 420}x{cur_h}")
            self._flush_log_buffer()
            self.log_btn.configure(text="📋  Скрыть логи",
                                   fg_color="#dc2626", hover_color="#b91c1c")
        else:
            self.log_frame.pack_forget()
            self.geometry(f"{max(720, cur_w - 420)}x{cur_h}")
            self.log_btn.configure(text="📋  Логи",
                                   fg_color="#334155", hover_color="#475569")

    def _append_log(self, line):
        if not line:
            return
        if self._log_visible and self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        else:
            self._log_buffer.append(line)

    def _flush_log_buffer(self):
        if not self.log_text:
            return
        self.log_text.configure(state="normal")
        for line in self._log_buffer:
            self.log_text.insert("end", line + "\n")
        if self._log_buffer:
            self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self._log_buffer = []

    def _clear_logs(self):
        self._log_buffer = []
        if self.log_text:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")

    def _read_server_logs(self):
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if line:
                    self.after(0, self._append_log, line.rstrip())
                else:
                    break
        except ValueError:
            pass

    # ─── Статус и утилиты ─────────────────────────────────────

    @staticmethod
    def _find_icon():
        """Найти icon.ico — в исходниках или в PyInstaller bundle"""
        if hasattr(sys, '_MEIPASS'):
            p = Path(sys._MEIPASS) / "icon.ico"
            if p.exists():
                return str(p)
        p = Path(__file__).parent / "icon.ico"
        return str(p) if p.exists() else None

    def _update_status_indicator(self, icon, text, color):
        self.status_indicator.configure(
            text=f"{icon}  {text}",
            text_color=color
        )

    def status(self, message):
        self.status_label.configure(text=message)

    def error(self, message):
        self.status_label.configure(text=message, text_color="#ef4444")
        self.after(5000, lambda: self.status_label.configure(text_color="#64748b"))

    def on_closing(self):
        if self.server_running and self.server_process:
            try:
                proc_pid = self.server_process.pid
                subprocess.run(
                    f'taskkill /F /T /PID {proc_pid}',
                    shell=True,
                    capture_output=True
                )
            except Exception:
                self.server_process.terminate()
        self.destroy()


def main():
    app = ClaudeDesktopApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()