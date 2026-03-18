import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from config import CONFIG


class FileManager:
    """
    Класс файлового менеджера с изолированным рабочим пространством.
    Предотвращает выход пользователя за пределы рабочей директории.
    """


    def __init__(self):
        """Инициализация файлового менеджера с загрузкой конфигурации."""
        self.config = CONFIG
        self.work_dir = Path(self.config.get("working_directory", "./workspace")).resolve()
        self.current_dir = self.work_dir
        self._ensure_work_dir()


    def _ensure_work_dir(self) -> None:
        """Создание рабочей директории при необходимости."""
        self.work_dir.mkdir(parents=True, exist_ok=True)


    def _is_safe_path(self, path: Path) -> bool:
        """Проверка, что путь находится внутри рабочей директории."""
        try:
            resolved = path.resolve()
            return str(resolved).startswith(str(self.work_dir.resolve()))
        except Exception:
            return False


    def _resolve_path(self, path_str: str) -> Path:
        """Преобразование строкового пути в абсолютный"""
        path_str = path_str.strip()
        if path_str.startswith("~"):
            path_str = os.path.expanduser(path_str)

        path = Path(path_str)
        if not path.is_absolute():
            path = self.current_dir / path

        return path.resolve()


    def get_current_dir(self) -> str:
        """Получение относительного пути текущей директории."""
        try:
            return str(self.current_dir.relative_to(self.work_dir))
        except ValueError:
            return str(self.current_dir)

    def create_directory(self, name: str) -> Tuple[bool, str]:
        """Создание новой директории."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if path.exists():
            return False, f"Директория '{name}' уже существует"

        try:
            path.mkdir(parents=True)
            return True, f"Директория '{name}' успешно создана"
        except Exception as e:
            return False, f"Ошибка создания директории: {e}"


    def delete_directory(self, name: str, force: bool = False) -> Tuple[bool, str]:
        """Удаление директории."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not path.exists():
            return False, f"Директория '{name}' не найдена"

        if not path.is_dir():
            return False, f"'{name}' не является директорией"

        if path == self.work_dir:
            return False, "Невозможно удалить корневую рабочую директорию"

        try:
            if force or not any(path.iterdir()):
                shutil.rmtree(path)
                if self.current_dir == path or str(self.current_dir).startswith(str(path)):
                    self.current_dir = self.work_dir
                return True, f"Директория '{name}' успешно удалена"
            else:
                return False, f"Директория '{name}' не пуста. Используйте флаг -f для принудительного удаления"
        except Exception as e:
            return False, f"Ошибка удаления директории: {e}"


    def change_directory(self, name: str) -> Tuple[bool, str]:
        """Смена текущей директории."""
        if name == "..":
            new_dir = self.current_dir.parent
        elif name == "/" or name == "~":
            new_dir = self.work_dir
        else:
            new_dir = self._resolve_path(name)

        if not self._is_safe_path(new_dir):
            return False, "Ошибка: невозможно выйти за пределы рабочей директории"

        if not new_dir.exists():
            return False, f"Директория '{name}' не найдена"

        if not new_dir.is_dir():
            return False, f"'{name}' не является директорией"

        self.current_dir = new_dir
        return True, f"Текущая директория: {self.get_current_dir()}"


    def list_directory(self, show_all: bool = False) -> Tuple[bool, List[Dict]]:
        """Получение содержимого текущей директории."""
        items = []
        show_hidden = show_all or self.config.get("show_hidden_files", False)

        try:
            for item in self.current_dir.iterdir():
                if item.name.startswith('.') and not show_hidden:
                    continue

                stat = item.stat()
                items.append({
                    'name': item.name,
                    'type': 'dir' if item.is_dir() else 'file',
                    'size': stat.st_size if item.is_file() else '-',
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                })

            items.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
            return True, items
        except Exception as e:
            return False, []


    def create_file(self, name: str, content: str = "") -> Tuple[bool, str]:
        """Создание нового файла."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if path.exists():
            return False, f"Файл '{name}' уже существует"

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            encoding = self.config.get("encoding", "utf-8")
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return True, f"Файл '{name}' успешно создан"
        except Exception as e:
            return False, f"Ошибка создания файла: {e}"


    def read_file(self, name: str) -> Tuple[bool, str]:
        """Чтение содержимого файла."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not path.exists():
            return False, f"Файл '{name}' не найден"

        if not path.is_file():
            return False, f"'{name}' не является файлом"

        try:
            max_size = self.config.get("max_file_size_mb", 10) * 1024 * 1024
            if path.stat().st_size > max_size:
                return False, f"Файл слишком большой (максимум {self.config.get('max_file_size_mb', 10)} MB)"

            encoding = self.config.get("encoding", "utf-8")
            with open(path, 'r', encoding=encoding) as f:
                return True, f.read()
        except UnicodeDecodeError:
            return False, "Невозможно прочитать файл: не текстовый формат или неверная кодировка"
        except Exception as e:
            return False, f"Ошибка чтения файла: {e}"


    def write_file(self, name: str, content: str, append: bool = False) -> Tuple[bool, str]:
        """Запись в файл."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        try:
            mode = 'a' if append else 'w'
            encoding = self.config.get("encoding", "utf-8")
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            action = "обновлён" if append else "перезаписан"
            return True, f"Файл '{name}' {action}"
        except Exception as e:
            return False, f"Ошибка записи в файл: {e}"


    def delete_file(self, name: str) -> Tuple[bool, str]:
        """Удаление файла."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not path.exists():
            return False, f"Файл '{name}' не найден"

        if not path.is_file():
            return False, f"'{name}' не является файлом"

        try:
            path.unlink()
            return True, f"Файл '{name}' успешно удалён"
        except Exception as e:
            return False, f"Ошибка удаления файла: {e}"


    def copy_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Копирование файла или директории."""
        src = self._resolve_path(source)
        dst = self._resolve_path(destination)

        if not self._is_safe_path(src) or not self._is_safe_path(dst):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not src.exists():
            return False, f"Источник '{source}' не найден"

        try:
            if src.is_file():
                shutil.copy2(src, dst)
                return True, f"Файл '{source}' скопирован в '{destination}'"
            else:
                shutil.copytree(src, dst)
                return True, f"Директория '{source}' скопирована в '{destination}'"
        except Exception as e:
            return False, f"Ошибка копирования: {e}"


    def move_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Перемещение файла или директории."""
        src = self._resolve_path(source)
        dst = self._resolve_path(destination)

        if not self._is_safe_path(src) or not self._is_safe_path(dst):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not src.exists():
            return False, f"Источник '{source}' не найден"

        try:
            shutil.move(str(src), str(dst))
            return True, f"'{source}' перемещён в '{destination}'"
        except Exception as e:
            return False, f"Ошибка перемещения: {e}"


    def rename_file(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Переименование файла или директории."""
        src = self._resolve_path(old_name)
        dst = self._resolve_path(new_name)

        if not self._is_safe_path(src) or not self._is_safe_path(dst):
            return False, "Ошибка: путь выходит за пределы рабочей директории"

        if not src.exists():
            return False, f"'{old_name}' не найден"

        if dst.exists():
            return False, f"'{new_name}' уже существует"

        try:
            src.rename(dst)
            return True, f"'{old_name}' переименован в '{new_name}'"
        except Exception as e:
            return False, f"Ошибка переименования: {e}"


    def get_file_info(self, name: str) -> Tuple[bool, Dict]:
        """Получение информации о файле или директории."""
        path = self._resolve_path(name)

        if not self._is_safe_path(path):
            return False, {}

        if not path.exists():
            return False, {}

        try:
            stat = path.stat()
            info = {
                'name': path.name,
                'path': str(path.relative_to(self.work_dir)),
                'type': 'директория' if path.is_dir() else 'файл',
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'permissions': oct(stat.st_mode)[-3:]
            }

            if path.is_file():
                info['extension'] = path.suffix

            return True, info
        except Exception as e:
            return False, {}