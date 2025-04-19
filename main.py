import random
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
import time

class Node:
    __slots__ = ['data', 'left', 'right']
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None
        self._size = 0

    def get_size(self):
        return self._size

    def create_random_tree(self, num_nodes, none_probability=0.2):
        start_time = time.time()
        if num_nodes <= 0:
            raise ValueError("Количество узлов должно быть положительным")
        
        values = []
        for _ in range(num_nodes):
            if random.random() < none_probability:
                values.append(None)
            else:
                values.append(random.randint(1, num_nodes))
        
        if values[0] is None:
            values[0] = random.randint(1, num_nodes)
        
        self.root = Node(values[0])
        self._size = 1 if values[0] is not None else 0
        nodes_queue = deque([self.root])
        current_index = 1
        
        while nodes_queue and current_index < num_nodes:
            current_node = nodes_queue.popleft()
            
            if current_node is None:
                current_index += 2
                continue
                
            if current_index < num_nodes:
                if values[current_index] is not None:
                    current_node.left = Node(values[current_index])
                    self._size += 1
                    nodes_queue.append(current_node.left)
                else:
                    nodes_queue.append(None)
                current_index += 1
            
            if current_index < num_nodes:
                if values[current_index] is not None:
                    current_node.right = Node(values[current_index])
                    self._size += 1
                    nodes_queue.append(current_node.right)
                else:
                    nodes_queue.append(None)
                current_index += 1
        
        elapsed = (time.time() - start_time) * 1_000_000
        print(f"Дерево создано за {elapsed:.3f} мкс")
        self.save_to_file("generated_tree.txt")

    def find_subtree_with_root(self, root_value, blocked):
        target_node = self._find_node_by_value(self.root, root_value)
        if target_node is None:
            print(f"Узел {root_value} не найден")
            return None
        
        if not self._is_valid_subtree(target_node, blocked):
            print(f"Поддерево с корнем {root_value} содержит заблокированные узлы")
            return None
        
        subtree = BinaryTree()
        subtree.root = self._copy_subtree(target_node)
        subtree._size = self._calculate_size(subtree.root)
        return subtree

    def find_first_valid_subtree(self, blocked):
        """
        Находит первое поддерево (в порядке обхода в ширину), которое:
        1. Не содержит ни одного заблокированного значения
        2. Является полным поддеревом
        Возвращает BinaryTree или None, если такого нет
        """
        if self.root is None:
            return None

        queue = deque([self.root])
        while queue:
            current_node = queue.popleft()
            
            # Проверяем, является ли текущий узел корнем валидного поддерева
            if current_node.data not in blocked:
                is_valid = True
                validation_queue = deque([current_node])
                
                # Проверяем все узлы в поддереве
                while validation_queue and is_valid:
                    node = validation_queue.popleft()
                    if node.data in blocked:
                        is_valid = False
                        break
                    if node.left:
                        validation_queue.append(node.left)
                    if node.right:
                        validation_queue.append(node.right)
                
                if is_valid:
                    # Создаем новое дерево
                    subtree = BinaryTree()
                    subtree.root = self._copy_subtree(current_node)
                    subtree._size = self._calculate_size(subtree.root)
                    return subtree
            
            # Добавляем потомков в очередь для поиска
            if current_node.left:
                queue.append(current_node.left)
            if current_node.right:
                queue.append(current_node.right)
        
        return None

    def _is_valid_subtree(self, node, blocked):
        if node is None:
            return True
        if node.data in blocked:
            return False
        return (self._is_valid_subtree(node.left, blocked) and 
                (self._is_valid_subtree(node.right, blocked)))

    def _copy_subtree(self, node):
        if node is None:
            return None
        new_node = Node(node.data)
        new_node.left = self._copy_subtree(node.left)
        new_node.right = self._copy_subtree(node.right)
        return new_node

    def _calculate_size(self, node):
        if node is None:
            return 0
        return 1 + self._calculate_size(node.left) + self._calculate_size(node.right)

    def _find_node_by_value(self, node, value):
        if node is None:
            return None
        if node.data == value:
            return node
        left_result = self._find_node_by_value(node.left, value)
        if left_result:
            return left_result
        return self._find_node_by_value(node.right, value)

    def visualize(self, title="Бинарное дерево"):
        if self.root is None:
            print("Дерево пустое")
            return
        if self._size > 100:
            print(f"Дерево слишком большое для визуализации ({self._size} узлов)")
            return
            
        plt.clf()
        G = nx.DiGraph()
        pos = {}
        node_ids = {}
        current_id = 1

        def _build_graph(node, x=0, y=0, dx=1):
            nonlocal current_id
            if node is None:
                return
            node_id = f"{node.data}_{current_id}"
            node_ids[node] = node_id
            current_id += 1
            pos[node_id] = (x, y)
            G.add_node(node_id, label=str(node.data))
            if node.left:
                left_id = f"{node.left.data}_{current_id}"
                G.add_edge(node_id, left_id)
                _build_graph(node.left, x-dx, y-1, dx/2)
            if node.right:
                right_id = f"{node.right.data}_{current_id}"
                G.add_edge(node_id, right_id)
                _build_graph(node.right, x+dx, y-1, dx/2)

        _build_graph(self.root)
        node_colors = []
        labels = {}
        for node in G.nodes():
            node_data = G.nodes[node]['label']
            if G.out_degree(node) > 0:
                node_colors.append('skyblue')
            else:
                node_colors.append('lightgreen')
            labels[node] = node_data
            
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, labels=labels, node_size=800,
                node_color=node_colors, font_size=10,
                arrows=False, edge_color='gray')
        plt.title(title)
        plt.show()

    def save_to_file(self, filename):
        if self.root is None:
            print("Нечего сохранять — дерево пустое")
            return
            
        with open(filename, "w", encoding="utf-8") as f:
            def _preorder(node):
                if node is None:
                    f.write("None\n")
                    return
                f.write(f"{node.data}\n")
                _preorder(node.left)
                _preorder(node.right)
            _preorder(self.root)
        print(f"Дерево сохранено в файл: {filename}")

    def load_from_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден.")
            return
            
        def _build_tree(iterator):
            try:
                value = next(iterator)
            except StopIteration:
                return None
            if value == "None":
                return None
            node = Node(int(value))
            self._size += 1
            node.left = _build_tree(iterator)
            node.right = _build_tree(iterator)
            return node
            
        self._size = 0
        self.root = _build_tree(iter(lines))
        print(f"Дерево загружено из файла: {filename} ({self._size} узлов)")

def manual_tree_creation_from_list():
    print("\nВведите значения узлов через запятую, используя 'None' для пропущенных узлов.")
    print("Пример: 1, 2, None, 3, 4")
    input_values = input("Введите список значений: ").strip()
    
    try:
        values = [None if val.strip().lower() == 'none' else int(val) 
                 for val in input_values.split(",")]
    except ValueError:
        print("Неверный ввод! Убедитесь, что вы ввели целые числа или 'None'.")
        return None

    tree = BinaryTree()
    if not values:
        print("Список значений пуст. Дерево не создано.")
        return None

    tree.root = Node(values[0]) if values[0] is not None else None
    if tree.root is None:
        print("Корень дерева не может быть None. Дерево не создано.")
        return None

    tree._size = 1
    queue = deque([tree.root])
    index = 1

    while queue and index < len(values):
        current_node = queue.popleft()

        if index < len(values) and values[index] is not None:
            current_node.left = Node(values[index])
            tree._size += 1
            queue.append(current_node.left)
        index += 1

        if index < len(values) and values[index] is not None:
            current_node.right = Node(values[index])
            tree._size += 1
            queue.append(current_node.right)
        index += 1

    print(f"Дерево создано. Количество узлов: {tree._size}")
    return tree

def main():
    print("Программа работы с бинарными деревьями")
    current_tree = None
    while True:
        print("\nГлавное меню:")
        print("1. Загрузить дерево из файла")
        print("2. Сгенерировать случайное дерево")
        print("3. Создать дерево вручную")
        print("4. Показать текущее дерево")
        print("5. Найти поддерево с указанным корнем")
        print("6. Найти первое валидное поддерево")
        print("7. Сохранить текущее дерево")
        print("8. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            filename = input("Введите имя файла: ")
            current_tree = BinaryTree()
            current_tree.load_from_file(filename)

        elif choice == '2':
            try:
                num_nodes = int(input("Количество узлов: "))
                none_prob = float(input("Вероятность None-узлов (0-1): "))
                current_tree = BinaryTree()
                current_tree.create_random_tree(num_nodes, none_prob)
                print(f"Создано дерево с {num_nodes} узлами")
                if input("Сохранить дерево в файл? (y/n): ").lower() == 'y':
                    filename = input("Введите имя файла: ")
                    current_tree.save_to_file(filename)
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            current_tree = manual_tree_creation_from_list()

        elif choice == '4':
            if current_tree is None:
                print("Дерево не загружено!")
                continue
            if current_tree.get_size() <= 100:
                current_tree.visualize()
            else:
                print("Визуализация доступна только для деревьев с ≤ 100 узлами")

        elif choice == '5':
            if current_tree is None:
                print("Дерево не загружено!")
                continue
            root_value = int(input("Введите значение корня поддерева: "))
            blocked = set(map(int, input("Введите заблокированные вершины через запятую: ").split(",")))
            subtree = current_tree.find_subtree_with_root(root_value, blocked)
            if subtree:
                print(f"Найдено валидное поддерево с {subtree.get_size()} узлами")
                if subtree.get_size() <= 100:
                    subtree.visualize(f"Поддерево с корнем {root_value}")
            else:
                print("Валидное поддерево не найдено")

        elif choice == '6':
            if current_tree is None:
                print("Дерево не загружено!")
                continue
            blocked = set(map(int, input("Введите заблокированные вершины через запятую: ").split(",")))
            subtree = current_tree.find_first_valid_subtree(blocked)
            if subtree:
                print(f"Найдено первое валидное поддерево с корнем {subtree.root.data} и {subtree.get_size()} узлами")
                if subtree.get_size() <= 100:
                    subtree.visualize(f"Валидное поддерево (корень {subtree.root.data})")
            else:
                print("Валидное поддерево не найдено")

        elif choice == '7':
            if current_tree is None:
                print("Нет дерева для сохранения!")
                continue
            filename = input("Введите имя файла: ")
            current_tree.save_to_file(filename)

        elif choice == '8':
            print("Выход из программы...")
            break

        else:
            print("Некорректный ввод!")

if __name__ == "__main__":
    main()