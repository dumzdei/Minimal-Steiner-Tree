import argparse
import subprocess
from pathlib import Path

from validator.validator import validate


def run_pipeline(input_json_path, algorithm, output_json_path, cpp_executable_path="SteinerTree"):
    input_path = Path(input_json_path)
    output_path = Path(output_json_path)

    if not input_path.is_file():
        print(f"[Ошибка] Входной файл {input_path} не найден!")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [cpp_executable_path, str(input_path), str(output_path), algorithm]

    print(f"Вызов модуля трассировки для алгоритма '{algorithm}': {' '.join(cmd)}")
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
        "jobs",
        nargs="+",
        metavar="АРГУМЕНТ",
        help="Повторяющиеся тройки: входной_файл алгоритм выходной_файл.",
    )
    parser.add_argument(
        "--executable",
        default="SteinerTree",
        help="Путь к исполняемому C++-файлу (по умолчанию: SteinerTree).",
    )
    arguments = parser.parse_args()

    if len(arguments.jobs) % 3 != 0:
        parser.error("Передавайте аргументы тройками: входной_файл алгоритм выходной_файл.")

    return arguments, zip(*(iter(arguments.jobs),) * 3)


if __name__ == "__main__":
    arguments, jobs = parse_arguments()
    is_successful = True

    for input_file, algorithm, output_file in jobs:
        is_successful = run_pipeline(
            input_file, algorithm, output_file, arguments.executable
        ) and is_successful

    raise SystemExit(0 if is_successful else 1)