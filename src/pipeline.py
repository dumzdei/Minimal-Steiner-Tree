import subprocess
import os
from validator import validate

def run_pipeline(input_json_path, cpp_executable_path="router", output_json_path="output.json"):
    """
    @brief Главный файл проекта
    @details
    1. Проверяет наличие входного файла
    2. Запускает C++ программу трассировки, передавая путь к входному JSON
    3. Ожидает, что C++ запишет результат в output_json_path
    4. Запускает валидатор для проверки корректности
    """
    
    if not os.path.exists(input_json_path):
        print(f"[Ошибка] Входной файл {input_json_path} не найден!")
        return False

    # 1) путь к входному JSON, 2) путь к выходному JSON
    cmd = [cpp_executable_path, input_json_path, output_json_path]
    
    print(f"Вызов модуля трассировки: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # Логи от C++ программы
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
    except Exception as e:
        print(f"[Ошибка] Не удалось запустить процесс трассировки: {e}")
        return False

    print("Запуск верификатора...")
    is_valid, message = validate(input_json_path, output_json_path)
    
    if is_valid:
        print(f"[УСПЕХ] {message}")
        return True
    else:
        print(f"[ПРОВАЛ ВЕРИФИКАЦИИ] {message}")
        return False

if __name__ == "__main__":
    input_file = "input/test_first.json" # Путь к исходному файлу
    cpp_binary = "./src/name"  # Путь к скомпилированному C++ файлу
    output_file = "output/output.json" # Путь к выходному файлу
    
    run_pipeline(input_file, cpp_binary, output_file)