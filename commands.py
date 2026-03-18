import os
from typing import Dict, Callable, Tuple, List
from file_manager import FileManager


class CommandHandler:
    """Класс обработчика команд файлового менеджера."""

    def __init__(self, file_manager: FileManager):
        """Инициализация обработчика со ссылкой на файловый менеджер."""
        self.fm = file_manager
        self.commands = self._register_commands()
        self.running = True

    def _register_commands(self) -> Dict[str, Callable]:
        """Доступные команды."""
        return {
            'help': self.cmd_help,
            'h': self.cmd_help,
            '?': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'q': self.cmd_exit,
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'touch': self.cmd_touch,
            'cat': self.cmd_cat,
            'read': self.cmd_cat,
            'write': self.cmd_write,
            'append': self.cmd_append,
            'rm': self.cmd_rm,
            'del': self.cmd_rm,
            'cp': self.cmd_cp,
            'copy': self.cmd_cp,
            'mv': self.cmd_mv,
            'move': self.cmd_mv,
            'ren': self.cmd_rename,
            'rename': self.cmd_rename,
            'info': self.cmd_info,
            'clear': self.cmd_clear,
            'cls': self.cmd_clear,
        }

    def parse_command(self, input_line: str) -> Tuple[str, List[str]]:
        """Разбор входной строки на команду и аргументы."""
        parts = input_line.strip().split()
        if not parts:
            return '', []
        command = parts[0].lower()
        args = parts[1:]
        return command, args

    def execute(self, input_line: str) -> str:
        """Выполнение команды и возврат результата."""
        command, args = self.parse_command(input_line)

        if not command:
            return ''

        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Ошибка выполнения команды: {e}"
        else:
            return f"Неизвестная команда: '{command}'. Введите 'help' для списка команд."

    def cmd_help(self, args: List[str]) -> str:
        """Вывод справки по командам."""
        help_text = """
КОМАНДЫ ФАЙЛОВОГО МЕНЕДЖЕРА
  НАВИГАЦИЯ                                                   
  pwd          - показать текущую директорию                  
  cd <dir>     - перейти в директорию (.. = на уровень выше)  
  ls [-a]      - показать содержимое (-a = включая скрытые)   

  ДИРЕКТОРИИ                                                  
  mkdir <name> - создать директорию                           
  rmdir <name> [-f] - удалить директорию (-f = с содержимым)  

  ФАЙЛЫ                                                       
  touch <name> - создать пустой файл                          
  cat <file>   - прочитать содержимое файла                   
  write <file> <text> - записать текст в файл                 
  append <file> <text> - дописать текст в файл                
  rm <file>    - удалить файл                                 
  cp <src> <dst> - скопировать файл/директорию                
  mv <src> <dst> - переместить файл/директорию                
 ren <old> <new> - переименовать файл/директорию             
  info <name>  - информация о файле/директории                

  ПРОЧЕЕ                                                      
  clear / cls  - очистить экран                               
  help / ?     - показать эту справку                         
  exit / q     - выйти из программы                           
"""
        return help_text


    def cmd_exit(self, args: List[str]) -> str:
        """Выход из программы."""
        self.running = False
        return "Завершение работы файлового менеджера."


    def cmd_clear(self, args: List[str]) -> str:
        """Очистка экрана."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ''


    def cmd_pwd(self, args: List[str]) -> str:
        """Показать текущую директорию."""
        return f"Текущая директория: /{self.fm.get_current_dir()}"


    def cmd_cd(self, args: List[str]) -> str:
        """Смена текущей директории."""
        if not args:
            return "Использование: cd <директория> (используйте '..' для перехода на уровень выше)"

        success, message = self.fm.change_directory(args[0])
        return message


    def cmd_ls(self, args: List[str]) -> str:
        """Вывод содержимого директории."""
        show_all = '-a' in args or '--all' in args
        success, items = self.fm.list_directory(show_all)

        if not success:
            return "Ошибка получения содержимого директории"

        if not items:
            return "Директория пуста"

        result = f"\n{'ТИП':<6} {'РАЗМЕР':>10}  {'ИЗМЕНЁН':<17}  ИМЯ\n"
        result += "─" * 60 + "\n"

        for item in items:
            type_str = "[DIR]" if item['type'] == 'dir' else "[FILE]"
            size_str = f"{item['size']:,} B" if isinstance(item['size'], int) else item['size']
            result += f"{type_str:<6} {size_str:>10}  {item['modified']:<17}  {item['name']}\n"

        result += "─" * 60 + f"\nВсего: {len(items)} элементов"
        return result


    def cmd_mkdir(self, args: List[str]) -> str:
        """Создание директории."""
        if not args:
            return "Использование: mkdir <имя_директории>"

        success, message = self.fm.create_directory(args[0])
        return message


    def cmd_rmdir(self, args: List[str]) -> str:
        """Удаление директории."""
        if not args:
            return "Использование: rmdir <имя_директории> [-f]"

        force = '-f' in args
        name = args[0] if args[0] != '-f' else (args[1] if len(args) > 1 else '')

        if not name:
            return "Использование: rmdir <имя_директории> [-f]"

        success, message = self.fm.delete_directory(name, force)
        return message


    def cmd_touch(self, args: List[str]) -> str:
        """Создание пустого файла."""
        if not args:
            return "Использование: touch <имя_файла>"

        success, message = self.fm.create_file(args[0])
        return message


    def cmd_cat(self, args: List[str]) -> str:
        """Чтение содержимого файла."""
        if not args:
            return "Использование: cat <имя_файла>"

        success, result = self.fm.read_file(args[0])
        if success:
            return f"─── {args[0]} ───\n{result}\n─── конец файла ───"
        return result


    def cmd_write(self, args: List[str]) -> str:
        """Запись в файл."""
        if len(args) < 2:
            return "Использование: write <имя_файла> <текст>"

        filename = args[0]
        content = ' '.join(args[1:])
        success, message = self.fm.write_file(filename, content)
        return message


    def cmd_append(self, args: List[str]) -> str:
        """Дописать в файл."""
        if len(args) < 2:
            return "Использование: append <имя_файла> <текст>"

        filename = args[0]
        content = ' '.join(args[1:])
        success, message = self.fm.write_file(filename, content, append=True)
        return message


    def cmd_rm(self, args: List[str]) -> str:
        """Удаление файла."""
        if not args:
            return "Использование: rm <имя_файла>"

        success, message = self.fm.delete_file(args[0])
        return message


    def cmd_cp(self, args: List[str]) -> str:
        """Копирование файла/директории."""
        if len(args) < 2:
            return "Использование: cp <источник> <назначение>"

        success, message = self.fm.copy_file(args[0], args[1])
        return message


    def cmd_mv(self, args: List[str]) -> str:
        """Перемещение файла/директории."""
        if len(args) < 2:
            return "Использование: mv <источник> <назначение>"

        success, message = self.fm.move_file(args[0], args[1])
        return message


    def cmd_rename(self, args: List[str]) -> str:
        """Переименование файла/директории."""
        if len(args) < 2:
            return "Использование: ren <старое_имя> <новое_имя>"

        success, message = self.fm.rename_file(args[0], args[1])
        return message


    def cmd_info(self, args: List[str]) -> str:
        """Информация о файле/директории."""
        if not args:
            return "Использование: info <имя_файла_или_директории>"

        success, info = self.fm.get_file_info(args[0])
        if not success:
            return f"Не удалось получить информацию о '{args[0]}'"

        result = f"\nИнформация о '{info['name']}'\n"
        result += f"  Тип:         {info['type']}\n"
        result += f"  Путь:        /{info['path']}\n"

        if info['type'] == 'файл':
            result += f"  Размер:      {info['size']:,} байт\n"
            result += f"  Расширение:  {info.get('extension', 'нет')}\n"
        else:
            result += f"  Размер:      {info['size']:,} байт\n"

        result += f"  Создан:      {info['created']}\n"
        result += f"  Изменён:     {info['modified']}\n"
        result += f"  Права:       {info['permissions']}"

        return result
