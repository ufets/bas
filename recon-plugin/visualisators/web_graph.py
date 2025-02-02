import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import IPResource, Domain, Email  # Ваши модели


def generate_graph_data(session, root_domain_name, output_file):
    data = {
        "ips": [],
        "domains": [],
        "emails": [],
        "connections": []
    }

    # Уникальные ID для предотвращения дублирования
    ip_ids = set()
    domain_ids = set()
    email_ids = set()

    # Находим корневой домен
    root_domain = session.query(Domain).filter_by(name=root_domain_name).first()
    if not root_domain:
        raise ValueError(f"Root domain '{root_domain_name}' not found in the database.")

    # Добавляем корневой домен
    root_id = f"domain{root_domain.id}"
    data["domains"].append({
        "id": root_id,
        "name": root_domain.name
    })
    domain_ids.add(root_id)

    # Рекурсивное добавление активов
    def add_assets_from_domain(domain, parent_id):
        domain_id = f"domain{domain.id}"
        if domain_id not in domain_ids:
            data["domains"].append({
                "id": domain_id,
                "name": domain.name
            })
            domain_ids.add(domain_id)

        # Связь с родительским доменом
        if parent_id:
            data["connections"].append({
                "source": parent_id,
                "target": domain_id
            })

        # Связи домена с IP
        for ip in domain.ips:
            ip_id = f"ip{ip.id}"
            if ip_id not in ip_ids:
                data["ips"].append({
                    "id": ip_id,
                    "ip_address": ip.ip_address
                })
                ip_ids.add(ip_id)

            # Связь домен → IP
            data["connections"].append({
                "source": domain_id,
                "target": ip_id
            })

        # Связи домена с email
        emails = session.query(Email).filter(Email.email_address.contains(domain.name)).all()
        for email in emails:
            email_id = f"email{email.id}"
            if email_id not in email_ids:
                data["emails"].append({
                    "id": email_id,
                    "email_address": email.email_address
                })
                email_ids.add(email_id)

            # Связь домен → email
            data["connections"].append({
                "source": domain_id,
                "target": email_id
            })

        # Рекурсивно добавляем поддомены (связи на уровне БД)
        child_domains = session.query(Domain).filter(Domain.name.like(f"%.{domain.name}")).all()
        for child_domain in child_domains:
            add_assets_from_domain(child_domain, domain_id)

    # Стартуем от корневого домена
    add_assets_from_domain(root_domain, None)

    # Сохраняем данные в файл
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Graph data saved to {output_file}")