import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from validator.validator import validate


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIRECTORY = PROJECT_ROOT / ".venv"
VENV_PYTHON = VENV_DIRECTORY / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
GUI_PACKAGES = ("PyQt6", "matplotlib", "pyinstaller")
GUI_EXECUTABLE = PROJECT_ROOT / "SteinerTreeGUI" / "SteinerTreeGUI.exe"
DEFAULT_EXECUTABLE = PROJECT_ROOT / ("SteinerTree.exe" if sys.platform == "win32" else "SteinerTree")


def ensure_gui_environment():
    if not VENV_PYTHON.is_file():
        print("Создание виртуального окружения .venv...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(VENV_DIRECTORY)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
        except OSError as error:
            print(f"[Ошибка] Не удалось создать .venv: {error}")
            return False
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0 or not VENV_PYTHON.is_file():
            print("[Ошибка] Не удалось создать виртуальное окружение .venv.")
            return False

    print("Установка зависимостей GUI...")
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", *GUI_PACKAGES],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
    except OSError as error:
        print(f"[Ошибка] Не удалось установить зависимости GUI: {error}")
        return False
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        print("[Ошибка] Не удалось установить зависимости GUI.")
        return False
    return True


def launch_gui():
    if not ensure_gui_executable():
        return False
    try:
        subprocess.Popen([str(GUI_EXECUTABLE)], cwd=GUI_EXECUTABLE.parent)
    except OSError as error:
        print(f"[Ошибка] Не удалось запустить GUI: {error}")
        return False
    return True


def ensure_gui_executable():
    if GUI_EXECUTABLE.is_file():
        return True
    if not ensure_gui_environment():
        return False

    cmake = shutil.which("cmake")
    if cmake is None:
        print("[Ошибка] CMake не найден. Установите CMake 3.15 или новее и повторите запуск.")
        return False

    build_directory = PROJECT_ROOT / "build"
    commands = (
        [cmake, "-S", str(PROJECT_ROOT), "-B", str(build_directory)],
        [cmake, "--build", str(build_directory), "--target", "SteinerTreeGUI"],
    )
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=PROJECT_ROOT)
        except OSError as error:
            print(f"[Ошибка] Не удалось запустить CMake: {error}")
            return False

        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            print("[Ошибка] Не удалось автоматически собрать SteinerTreeGUI.")
            return False

    if not GUI_EXECUTABLE.is_file():
        print(f"[Ошибка] Сборка завершилась, но GUI не найден: {GUI_EXECUTABLE}")
        return False
    return True


def ensure_executable(executable_path):
    """Configures and incrementally builds the bundled C++ program when needed."""
    executable = Path(executable_path)
    if executable.is_file():
        return True

    cmake = shutil.which("cmake")
    if cmake is None:
        print("[Ошибка] CMake не найден. Установите CMake 3.15 или новее и повторите запуск.")
        return False

    build_directory = PROJECT_ROOT / "build"
    commands = (
        [cmake, "-S", str(PROJECT_ROOT), "-B", str(build_directory)],
        [cmake, "--build", str(build_directory), "--target", "SteinerTree"],
    )
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=PROJECT_ROOT)
        except OSError as error:
            print(f"[Ошибка] Не удалось запустить CMake: {error}")
            return False

        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            print("[Ошибка] Не удалось автоматически собрать SteinerTree.")
            return False

    if not executable.is_file():
        print(f"[Ошибка] Сборка завершилась, но исполняемый файл не найден: {executable}")
        return False
    return True


def run_pipeline(input_json_path, output_json_path, cpp_executable_path=DEFAULT_EXECUTABLE):
    input_path = Path(input_json_path)
    output_path = Path(output_json_path)
    executable_path = Path(cpp_executable_path)

    if not input_path.is_file():
        print(f"[Ошибка] Входной файл {input_path} не найден!")
        return False

    if not ensure_executable(executable_path):
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(executable_path), str(input_path), str(output_path)]

    print(f"Вызов модуля трассировки: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.stdout:
            print(f"[C++ STDOUT]:\n{result.stdout}")
        if result.stderr:
            print(f"[C++ STDERR]:\n{result.stderr}")

        if result.returncode != 0:
            print(f"[Ошибка] C++ программа завершилась с кодом ошибки {result.returncode}")
            return False

    except FileNotFoundError:
        print(f"[Ошибка] Не найден исполняемый файл C++ по пути: {cpp_executable_path}")
        return False
    except subprocess.TimeoutExpired:
        print("[Ошибка] Превышено время выполнения программы трассировки.")
        return False
    except OSError as error:
        print(f"[Ошибка] Не удалось запустить процесс трассировки: {error}")
        return False

    print("Проверка выходного JSON и связности терминалов...")
    is_valid, message = validate(input_path, output_path)

    if is_valid:
        print(f"[УСПЕХ] {message}")
        return True

    print(f"[ПРОВАЛ ВЕРИФИКАЦИИ] {message}")
    return False


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Запускает алгоритмы и проверяет их JSON-результаты."
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Запустить графический интерфейс.",
    )
    parser.add_argument(
        "jobs",
        nargs="*",
        metavar="АРГУМЕНТ",
        help="Повторяющиеся пары: входной_файл выходной_файл.",
    )
    parser.add_argument(
        "--executable",
        default=str(DEFAULT_EXECUTABLE),
        help="Путь к исполняемому C++-файлу; при отсутствии будет собран автоматически.",
    )
    arguments = parser.parse_args()

    if arguments.gui:
        if arguments.jobs:
            parser.error("Параметр --gui нельзя сочетать с заданиями.")
        return arguments, ()
    if not arguments.jobs or len(arguments.jobs) % 2 != 0:
        parser.error("Передавайте аргументы парами: входной_файл выходной_файл.")

    return arguments, zip(*(iter(arguments.jobs),) * 2)


if __name__ == "__main__":
    arguments, jobs = parse_arguments()
    if arguments.gui:
        raise SystemExit(0 if launch_gui() else 1)

    is_successful = True
    for input_file, output_file in jobs:
        is_successful = run_pipeline(
            input_file, output_file, arguments.executable
        ) and is_successful

    raise SystemExit(0 if is_successful else 1)