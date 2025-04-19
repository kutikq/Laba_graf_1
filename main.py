"""
Полная версия программы для работы с бинарными деревьями
с ограничением значений узлов до 1000 и всеми функциями:
- Создание случайных деревьев
- Ручной ввод деревьев
- Поиск поддеревьев с замером времени
- Визуализация
- Сохранение/загрузка из файла
"""

import random
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
import time

class Node:
    """Узел бинарного дерева со значением от 1 до 1000"""
    __slots__ = ['data', 'left', 'right']
    
    def __init__(self, data):
        if data is not None and (data < 1 or data > 1000):
            raise ValueError("Значение узла должно быть от 1 до 1000")
        self.data = data    # Значение узла (1-1000)
        self.left = None    # Левый потомок
        self.right = None   # Правый потомок

class BinaryTree:
    """Бинарное дерево с ограниченными значениями узлов (1-1000)"""
    
    MAX_NODE_VALUE = 1000  # Максимальное значение узла
    
    def __init__(self):
        self.root = None  # Корень дерева
        self._size = 0    # Количество узлов

    def get_size(self):
        """Возвращает количество узлов в дереве"""
        return self._size

    def create_random_tree(self, num_nodes, none_probability=0.2):
        """
        Создает случайное дерево с значениями узлов от 1 до 1000
        :param num_nodes: количество узлов
        :param none_probability: вероятность отсутствия узла
        """
        if num_nodes <= 0:
            raise ValueError("Количество узлов должно быть положительным")
        
        # Генерация значений от 1 до 1000
        values = []
        for _ in range(num_nodes):
            if random.random() < none_probability:
                values.append(None)
            else:
                values.append(random.randint(1, self.MAX_NODE_VALUE))
        
        # Корень не может быть None
        if values[0] is None:
            values[0] = random.randint(1, self.MAX_NODE_VALUE)
        
        # Построение дерева в ширину
        self.root = Node(values[0])
        self._size = 1 if values[0] is not None else 0
        nodes_queue = deque([self.root])
        current_index = 1
        
        while nodes_queue and current_index < num_nodes:
            current_node = nodes_queue.popleft()
            
            if current_node is None:
                current_index += 2
                continue
                
            # Левый потомок
            if current_index < num_nodes:
                if values[current_index] is not None:
                    current_node.left = Node(values[current_index])
                    self._size += 1
                    nodes_queue.append(current_node.left)
                else:
                    nodes_queue.append(None)
                current_index += 1
            
            # Правый потомок
            if current_index < num_nodes:
                if values[current_index] is not None:
                    current_node.right = Node(values[current_index])
                    self._size += 1
                    nodes_queue.append(current_node.right)
                else:
                    nodes_queue.append(None)
                current_index += 1
        
        self.save_to_file("generated_tree.txt")

    def find_subtree_with_root(self, root_value, blocked):
        """
        Находит поддерево с указанным корнем, не содержащее заблокированных узлов
        :param root_value: значение корня (1-1000)
        :param blocked: множество заблокированных значений
        :return: BinaryTree или None
        """
        start_time = time.perf_counter()
        
        # Проверка входных данных
        if root_value < 1 or root_value > self.MAX_NODE_VALUE:
            print(f"Ошибка: значение корня должно быть от 1 до {self.MAX_NODE_VALUE}")
            return None
            
        # Поиск узла
        target_node = self._find_node_by_value(self.root, root_value)
        if target_node is None:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"Поиск занял {elapsed:.3f} мс: узел {root_value} не найден")
            return None
        
        # Проверка что это не лист
        if target_node.left is None and target_node.right is None:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"Поиск занял {elapsed:.3f} мс: узел {root_value} является листом")
            return None
        
        # Проверка на заблокированные узлы
        if not self._is_valid_subtree(target_node, blocked):
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"Поиск занял {elapsed:.3f} мс: поддерево содержит заблокированные узлы")
            return None
        
        # Копирование поддерева
        subtree = BinaryTree()
        subtree.root = self._copy_subtree(target_node)
        subtree._size = self._calculate_size(subtree.root)
        
        # Проверка что поддерево не стало листом
        if subtree.root.left is None and subtree.root.right is None:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"Поиск занял {elapsed:.3f} мс: поддерево стало листом после удаления узлов")
            return None
            
        elapsed = (time.perf_counter() - start_time) * 1000
        print(f"Поиск занял {elapsed:.3f} мс: найдено поддерево с {subtree._size} узлами")
        return subtree

    def find_first_valid_subtree(self, blocked):
        """
        Находит первое валидное поддерево (обход в ширину)
        :param blocked: множество заблокированных значений
        :return: BinaryTree или None
        """
        start_time = time.perf_counter()
        
        if self.root is None:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"Поиск занял {elapsed:.3f} мс: дерево пустое")
            return None

        queue = deque([self.root])
        while queue:
            current_node = queue.popleft()
            
            # Пропускаем листья
            if current_node.left is None and current_node.right is None:
                continue
                
            # Проверяем поддерево
            is_valid = True
            size = 0
            validation_queue = deque([current_node])
            
            while validation_queue and is_valid:
                node = validation_queue.popleft()
                if node.data in blocked:
                    is_valid = False
                    break
                size += 1
                if node.left:
                    validation_queue.append(node.left)
                if node.right:
                    validation_queue.append(node.right)
            
            # Если поддерево валидно и не является листом
            if is_valid and size >= 2:
                subtree = BinaryTree()
                subtree.root = self._copy_subtree(current_node)
                subtree._size = size
                elapsed = (time.perf_counter() - start_time) * 1000
                print(f"Поиск занял {elapsed:.3f} мс: найдено поддерево с корнем {subtree.root.data}")
                return subtree
            
            # Добавляем потомков в очередь поиска
            if current_node.left:
                queue.append(current_node.left)
            if current_node.right:
                queue.append(current_node.right)
        
        elapsed = (time.perf_counter() - start_time) * 1000
        print(f"Поиск занял {elapsed:.3f} мс: валидное поддерево не найдено")
        return None

    def visualize(self, title="Бинарное дерево"):
        """Визуализирует дерево с помощью matplotlib"""
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
        
        # Настройка цветов
        node_colors = []
        labels = {}
        for node in G.nodes():
            node_data = G.nodes[node]['label']
            if G.out_degree(node) > 0:  # Внутренние узлы
                node_colors.append('skyblue')
            else:  # Листья
                node_colors.append('lightgreen')
            labels[node] = node_data
            
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, labels=labels, node_size=800,
                node_color=node_colors, font_size=10,
                arrows=False, edge_color='gray')
        plt.title(title)
        plt.show()

    def save_to_file(self, filename):
        """Сохраняет дерево в файл (префиксный обход)"""
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
        """Загружает дерево из файла"""
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

    # Вспомогательные методы
    def _is_valid_subtree(self, node, blocked):
        """Рекурсивная проверка валидности поддерева"""
        if node is None:
            return True
        if node.data in blocked:
            return False
        return (self._is_valid_subtree(node.left, blocked) and 
                (self._is_valid_subtree(node.right, blocked)))

    def _copy_subtree(self, node):
        """Глубокое копирование поддерева"""
        if node is None:
            return None
        new_node = Node(node.data)
        new_node.left = self._copy_subtree(node.left)
        new_node.right = self._copy_subtree(node.right)
        return new_node

    def _calculate_size(self, node):
        """Подсчет количества узлов в поддереве"""
        if node is None:
            return 0
        return 1 + self._calculate_size(node.left) + self._calculate_size(node.right)

    def _find_node_by_value(self, node, value):
        """Поиск узла по значению"""
        if node is None:
            return None
        if node.data == value:
            return node
        left_result = self._find_node_by_value(node.left, value)
        if left_result:
            return left_result
        return self._find_node_by_value(node.right, value)

def manual_tree_creation_from_list():
    """Создает дерево из списка значений, введенного пользователем"""
    print("\nВведите значения узлов через запятую, используя 'None' для пропущенных узлов.")
    print("Пример: 1, 2, None, 3, 4")
    input_values = input("Введите список значений: ").strip()
    
    try:
        values = [None if val.strip().lower() == 'none' else int(val) 
                 for val in input_values.split(",")]
    except ValueError:
        print("Неверный ввод! Убедитесь, что вы ввели целые числа от 1 до 1000 или 'None'.")
        return None

    tree = BinaryTree()
    if not values:
        print("Список значений пуст. Дерево не создано.")
        return None

    # Проверка значений
    for val in values:
        if val is not None and (val < 1 or val > 1000):
            print(f"Ошибка: значение {val} должно быть от 1 до 1000")
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
    """Основная функция с интерфейсом командной строки"""
    print("Программа работы с бинарными деревьями (значения узлов 1-1000)")
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
                print(f"Создано дерево с {current_tree.get_size()} узлами")
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
            try:
                root_value = int(input("Введите значение корня (1-1000): "))
                if root_value < 1 or root_value > 1000:
                    print("Ошибка: значение должно быть от 1 до 1000")
                    continue
                blocked = list(map(int, input("Введите заблокированные вершины через пробел: ").split()))
                if any(x < 1 or x > 1000 for x in blocked):
                    print("Ошибка: значения должны быть от 1 до 1000")
                    continue
                subtree = current_tree.find_subtree_with_root(root_value, set(blocked))
                if subtree:
                    print(f"Найдено валидное поддерево с {subtree.get_size()} узлами")
                    if subtree.get_size() <= 100:
                        subtree.visualize(f"Поддерево с корнем {root_value}")
                else:
                    print("Валидное поддерево не найдено")
            except ValueError:
                print("Ошибка ввода! Введите целые числа от 1 до 1000")

        elif choice == '6':
            if current_tree is None:
                print("Дерево не загружено!")
                continue
            try:
                blocked = list(map(int, input("Введите заблокированные вершины через пробел: ").split()))
                if any(x < 1 or x > 1000 for x in blocked):
                    print("Ошибка: значения должны быть от 1 до 1000")
                    continue
                subtree = current_tree.find_first_valid_subtree(set(blocked))
                if subtree:
                    print(f"Найдено первое валидное поддерево с корнем {subtree.root.data}")
                    print(f"Размер поддерева: {subtree.get_size()} узлов")
                    if subtree.get_size() <= 100:
                        subtree.visualize(f"Валидное поддерево (корень {subtree.root.data})")
                else:
                    print("Валидное поддерево не найдено")
            except ValueError:
                print("Ошибка ввода! Введите целые числа от 1 до 1000")

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
            print("Некорректный ввод! Выберите пункт от 1 до 8.")

if __name__ == "__main__":
    main()