# recon.py
from models import IPResource, init_db
from sqlalchemy.orm import declarative_base
import logging, sys
from visualisators.graph import visualize_data
from visualisators.web_graph import generate_graph_data
from active.active_recon import active_recon
from passive.passive_recon import passive_recon

# Базовый класс для ORM
Base = declarative_base()
# Отключение логов SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

if __name__ == "__main__":
    # Инициализация базы данных
    Session = init_db()
    session = Session()

    target_domain = sys.argv[1]
    target = IPResource.create(session, domain_name=target_domain)
    
    passive_recon(session, target)
    active_recon(session, target)
    generate_graph_data(session, target_domain, "assets.json")
    session.close()



    # for resource in session.query(IPResource).all():
    #     print(resource)
    #     print(resource.domains)
    #     print(resource.open_ports)

    #visualize_data(session)
    # Генерация данных для графа
    #graph_data = get_graph_data(session)

    # Сохранение данных в JSON (для использования на клиенте)
    # with open('graph_data.json', 'w') as f:
    #     json.dump(graph_data, f)
    # Генерация дампа