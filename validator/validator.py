import json
from collections import deque
from pathlib import Path


def read_json(path, file_kind):
    try:
        with Path(path).open("r", encoding="utf-8") as json_file:
            return True, json.load(json_file)
    except FileNotFoundError:
        return False, f"{file_kind} файл не найден: {path}"
    except UnicodeDecodeError as error:
        return False, f"{file_kind} файл не является UTF-8: {error}"
    except json.JSONDecodeError as error:
        return (
            False,
            f"Синтаксическая ошибка JSON в {file_kind.lower()} файле в строке {error.lineno}, "
            f"столбце {error.colno}: {error.msg}",
        )
    except OSError as error:
        return False, f"Не удалось прочитать {file_kind.lower()} файл: {error}"


def point_from_json(point, net_id):
    if not isinstance(point, dict) or not {"x", "y"}.issubset(point):
        return None, f"Сеть '{net_id}': точка должна содержать координаты x и y."

    x, y = point["x"], point["y"]
    if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return None, f"Сеть '{net_id}': координаты точки должны быть числами."

    return (x, y), None


def required_nets(input_data):
    if not isinstance(input_data, dict):
        return None, "Входной JSON должен быть словарем."

    if "nets" in input_data:
        input_nets = input_data["nets"]
    elif "terminals" in input_data:
        input_nets = [{"net_id": "DEFAULT_NET", "terminals": input_data["terminals"]}]
    else:
        return None, "Во входном JSON отсутствует 'nets' или 'terminals'."

    if not isinstance(input_nets, list):
        return None, "Поле 'nets' во входном JSON должно быть массивом."

    nets = {}
    for net in input_nets:
        if not isinstance(net, dict) or "net_id" not in net or "terminals" not in net:
            return None, "Каждая входная сеть должна содержать 'net_id' и 'terminals'."

        net_id = net["net_id"]
        terminals = net["terminals"]
        if not isinstance(net_id, str) or not isinstance(terminals, list):
            return None, "'net_id' должен быть строкой, а 'terminals' — массивом."
        if net_id in nets:
            return None, f"Во входном JSON повторяется net_id '{net_id}'."

        points = set()
        for terminal in terminals:
            point, error = point_from_json(terminal, net_id)
            if error:
                return None, error
            points.add(point)
        nets[net_id] = points

    return nets, None


def output_nets(output_data):
    if isinstance(output_data, list):
        return output_data, None
    if isinstance(output_data, dict) and "nets" in output_data and isinstance(output_data["nets"], list):
        return output_data["nets"], None
    return None, "Выходной JSON должен быть массивом сетей или объектом с массивом 'nets'."


def terminals_connected(required_terminals, edges, net_id):
    adjacency = {}
    for edge in edges:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
            return False, f"Сеть '{net_id}': каждое ребро должно содержать 'from' и 'to'."

        source, error = point_from_json(edge["from"], net_id)
        if error:
            return False, error
        target, error = point_from_json(edge["to"], net_id)
        if error:
            return False, error

        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)

    if len(required_terminals) <= 1:
        return True, None

    missing = required_terminals.difference(adjacency)
    if missing:
        return False, f"Сеть '{net_id}': терминалы отсутствуют в рёбрах: {sorted(missing)}."

    reached = set()
    queue = deque([next(iter(required_terminals))])
    while queue:
        point = queue.popleft()
        if point in reached:
            continue
        reached.add(point)
        queue.extend(adjacency[point] - reached)

    disconnected = required_terminals.difference(reached)
    if disconnected:
        return False, f"Сеть '{net_id}': терминалы не соединены: {sorted(disconnected)}."

    return True, None


def validate(input_json_path, output_json_path):
    input_ok, input_data = read_json(input_json_path, "Входной")
    if not input_ok:
        return False, input_data

    output_ok, output_data = read_json(output_json_path, "Выходной")
    if not output_ok:
        return False, output_data

    expected_nets, error = required_nets(input_data)
    if error:
        return False, error

    result_nets, error = output_nets(output_data)
    if error:
        return False, error

    seen_net_ids = set()
    for result_net in result_nets:
        if not isinstance(result_net, dict) or "edges" not in result_net:
            return False, "Каждая выходная сеть должна содержать 'edges'."

        net_id = result_net.get("net_id", "DEFAULT_NET")
        edges = result_net["edges"]
        if not isinstance(net_id, str) or not isinstance(edges, list):
            return False, "'net_id' должен быть строкой, а 'edges' — массивом."
        if net_id in seen_net_ids:
            return False, f"В выходном JSON повторяется net_id '{net_id}'."
        if net_id not in expected_nets:
            return False, f"Выходной JSON содержит неизвестную сеть '{net_id}'."

        seen_net_ids.add(net_id)
        is_connected, error = terminals_connected(expected_nets[net_id], edges, net_id)
        if not is_connected:
            return False, error

    missing_nets = set(expected_nets).difference(seen_net_ids)
    if missing_nets:
        return False, f"В выходном JSON отсутствуют сети: {sorted(missing_nets)}."

    return True, "Все сети из входного файла присутствуют, а их терминалы соединены."