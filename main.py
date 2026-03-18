import os
import sys
from file_manager import FileManager
from commands import CommandHandler


def get_prompt(handler: CommandHandler) -> str:
    """Формирование строки приглашения."""
    current = handler.fm.get_current_dir()
    return f"fm:/{current}> "


def main():
    """Функция запуска файлового менеджера."""
    try:
        file_manager = FileManager()
        handler = CommandHandler(file_manager)
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        sys.exit(1)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Рабочая директория: {file_manager.work_dir}\n")

    while handler.running:
        try:
            user_input = input(get_prompt(handler))
            if user_input.strip():
                result = handler.execute(user_input)
                if result:
                    print(result)
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем")
            break
        except EOFError:
            print("\nВыход")
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())