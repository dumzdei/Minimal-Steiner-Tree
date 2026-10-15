import json
import networkx as nx

def validate(input_json_path, output_json_path):
    """
    @brief Проверяет корректность построенных деревьев Штейнера
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
            
        nets_terminals = {}
        if "nets" in input_data:
            for net in input_data["nets"]:
                net_id = net["net_id"]
                terminals = {(t["x"], t["y"]) for t in net["terminals"]}
                nets_terminals[net_id] = terminals
        else:
            # Упрощенный формат без для первого теста
            terminals = {(t["x"], t["y"]) for t in input_data["terminals"]}
            nets_terminals["DEFAULT_NET"] = terminals

        with open(output_json_path, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
            
        # Ожидается, что в выводе либо список цепей, либо одна общая корневая структура
        # Поддерживаются оба формата: список объектов цепей или словарь с ключом "nets"
        if isinstance(output_data, list):
            output_nets = output_data
        elif isinstance(output_data, dict) and "nets" in output_data:
            output_nets = output_data["nets"]
 
    except Exception as e:
        return False, f"Ошибка чтения файлов: {e}"

    output_nets_dict = {net.get("net_id", "DEFAULT_NET"): net for net in output_nets}

    grand_total_length = 0

    for net_id, required_terminals in nets_terminals.items():
        if net_id not in output_nets_dict:
            return False, f"Ошибка: для цепи '{net_id}' отсутствуют результаты!"
        
        net_result = output_nets_dict[net_id]
        edges = net_result.get("edges", [])
        
        G = nx.Graph()
        net_length = 0

        # Проверка ребер цепи
        for edge in edges:
            p1 = (edge["from"]["x"], edge["from"]["y"])
            p2 = (edge["to"]["x"], edge["to"]["y"])
            
            x1, y1 = p1
            x2, y2 = p2
            
            # Проверка на прямоугольность (Manhattan routing)
            if x1 != x2 and y1 != y2:
                return False, f"Цепь '{net_id}': ребро из {p1} в {p2} не является горизонтальным или вертикальным!"
                
            length = abs(x1 - x2) + abs(y1 - y2)
            net_length += length
            G.add_edge(p1, p2, weight=length)

        # Проверка на отсутствие циклов
        if not nx.is_forest(G):
            return False, f"Цепь '{net_id}': граф содержит циклы!"

        # Проверка, что все обязательные терминалы этой цепи присутствуют в графе
        for t in required_terminals:
            if t not in G:
                return False, f"Цепь '{net_id}': терминал {t} отсутствует в построенном дереве!"

        # Проверка связности терминалов внутри цепи
        if len(required_terminals) > 1:
            first_term = list(required_terminals)[0]
            for t in required_terminals:
                if not nx.has_path(G, first_term, t):
                    return False, f"Цепь '{net_id}': терминал {t} не соединен с остальными терминалами этой цепи!"

        grand_total_length += net_length

    return True, f"Успех! Все цепи корректны. Общая суммарная длина проводников: {grand_total_length}"