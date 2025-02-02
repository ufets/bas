import networkx as nx
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from models import Email,  IPResource

import networkx as nx
import matplotlib.pyplot as plt
from urllib.parse import urlparse

def get_root_domain(domain_name):
    """
    Возвращает корневой домен из полного имени домена.
    Например, для "sub.example.com" вернёт "example.com".
    """
    parts = domain_name.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])
    return domain_name

def visualize_data(session):
    """
    Визуализирует данные из базы данных в виде графа.

    Узлы:
        - IP-адреса
        - Доменные имена
        - Открытые порты
        - Email-адреса

    Ребра:
        - Связь между IP-адресами и доменами
        - Связь между IP-адресами и портами
        - Связь между доменами с одинаковым корневым доменом
    """
    # Создаем граф
    graph = nx.Graph()

    # Добавление узлов и ребер для IP-адресов и доменов
    ip_resources = session.query(IPResource).all()
    domain_root_map = {}

    for ip in ip_resources:
        graph.add_node(ip.ip_address, type='IP')

        # Связи IP-адресов с доменами
        for domain in ip.domains:
            graph.add_node(domain.name, type='Domain')
            graph.add_edge(ip.ip_address, domain.name)

            # Группируем домены по корневому домену
            root_domain = get_root_domain(domain.name)
            if root_domain not in domain_root_map:
                domain_root_map[root_domain] = []
            domain_root_map[root_domain].append(domain.name)

        # Связи IP-адресов с портами
        for port in ip.open_ports:
            port_node = f"{port.port_number}/{port.protocol}"
            graph.add_node(port_node, type='Port')
            graph.add_edge(ip.ip_address, port_node)

    # Добавление узлов и связей для email-адресов (если есть связи с доменами)
    emails = session.query(Email).all()
    for email in emails:
        graph.add_node(email.email_address, type='Email')

    # (Опционально) Добавляем связи email -> домены (если такая связь логична в вашей модели)
    # Здесь вы можете добавить логику связывания email с доменами, если нужно

    # Добавление связей между доменами с одинаковым корневым доменом
    for root_domain, domains in domain_root_map.items():
        center_node = f"Root: {root_domain}"
        graph.add_node(center_node, type='RootDomain')
        for domain in domains:
            graph.add_edge(center_node, domain)

    # Настройка отображения узлов по типу
    pos = nx.spring_layout(graph, k=1.2, iterations=200)  # Расположение узлов
    node_colors = []
    for node, attr in graph.nodes(data=True):
        if attr['type'] == 'IP':
            node_colors.append('lightblue')
        elif attr['type'] == 'Domain':
            node_colors.append('lightgreen')
        elif attr['type'] == 'Port':
            node_colors.append('orange')
        elif attr['type'] == 'Email':
            node_colors.append('pink')
        elif attr['type'] == 'RootDomain':
            node_colors.append('red')
        else:
            node_colors.append('gray')

    # Настройка размеров узлов
    node_sizes = []
    for node, attr in graph.nodes(data=True):
        if attr['type'] == 'IP':
            node_sizes.append(2000)
        elif attr['type'] == 'Domain':
            node_sizes.append(1500)
        elif attr['type'] == 'Port':
            node_sizes.append(1000)
        elif attr['type'] == 'Email':
            node_sizes.append(1200)
        elif attr['type'] == 'RootDomain':
            node_sizes.append(3000)
        else:
            node_sizes.append(800)

    # Рисуем граф
    plt.figure(figsize=(20, 15))
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=node_sizes,
        font_size=8,
        font_weight='bold',
        edge_color='gray'
    )
    plt.title("Network Visualization of IP Resources, Domains, Ports, and Emails")
    plt.show()