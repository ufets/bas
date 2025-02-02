from sqlalchemy import Column, Integer, String, Table, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import logging
from passive.dns import dns_lookup

# Отключение логов SQLAlchemy
logging.basicConfig()
logging.disable(logging.CRITICAL)

# Базовый класс для ORM
Base = declarative_base()

# Ассоциативная таблица для связи IP и доменных имен
ip_domain_table = Table(
    'ip_domain', Base.metadata,
    Column('ip_id', Integer, ForeignKey('ip_resources.id'), primary_key=True),
    Column('domain_id', Integer, ForeignKey('domains.id'), primary_key=True)
)

class IPResource(Base):
    __tablename__ = 'ip_resources'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, unique=True, nullable=False)

    # Relationships
    domains = relationship("Domain", secondary=ip_domain_table, back_populates="ips")
    open_ports = relationship("Port", back_populates="ip")
    whois_data = Column(String)  # JSON or string with WHOIS information
    raw_dns_records = Column(String)  # JSON or string with raw DNS records
    certificates = Column(String)  # JSON or string with certificates

    def __repr__(self):
        return f"<IPResource(ip_address='{self.ip_address}')>"

    @classmethod
    def create(cls, session, ip_address=None, domain_name=None):
        if not ip_address and not domain_name:
            raise ValueError("Either ip_address or domain_name must be provided.")

        if domain_name:
            # Simulate DNS lookup to get IP address
            ip_address = dns_lookup(domain_name, record_type="A")[0]

        existing_ip = session.query(cls).filter_by(ip_address=ip_address).first()
        if existing_ip:
            if domain_name and domain_name not in [d.name for d in existing_ip.domains]:
                existing_ip.add_domain(session, domain_name)
            return existing_ip

        ip_resource = cls(ip_address=ip_address)
        if domain_name:
            domain = session.query(Domain).filter_by(name=domain_name).first()
            if not domain:
                domain = Domain(name=domain_name)
                session.add(domain)
            ip_resource.domains.append(domain)

        session.add(ip_resource)
        session.commit()
        return ip_resource

    def add_domain(self, session, domain_name):
        domain = session.query(Domain).filter_by(name=domain_name).first()
        if not domain:
            domain = Domain(name=domain_name)
            session.add(domain)
        if domain not in self.domains:
            self.domains.append(domain)
        session.commit()

class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Отношения
    ips = relationship("IPResource", secondary=ip_domain_table, back_populates="domains")

    def __repr__(self):
        return f"<Domain(name='{self.name}')>"

    @classmethod
    def create(cls, session, name):
        existing_domain = session.query(cls).filter_by(name=name).first()
        if existing_domain:
            return existing_domain

        domain = cls(name=name)
        session.add(domain)
        session.commit()
        return domain

class Port(Base):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    port_number = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)
    state = Column(String, nullable=False)
    info = Column(String, nullable=True)  # Обновленное поле для информации сервиса
    
    ip_id = Column(Integer, ForeignKey('ip_resources.id'))
    ip = relationship("IPResource", back_populates="open_ports")

    def __repr__(self):
        return f"<Port(port_number={self.port_number}, protocol='{self.protocol}', state='{self.state}', info='{self.info}')>"

    @classmethod
    def create(cls, session, ip, port_number, protocol, state, info):
        port = cls(port_number=port_number, protocol=protocol, ip=ip, state=state, info=info)
        session.add(port)
        session.commit()
        return port


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Email(email_address='{self.email_address}')>"

    @classmethod
    def create(cls, session, email_address: str):

        try:
            existing_email = session.query(cls).filter_by(email_address=email_address).first()
            if existing_email:
                return existing_email

            email = cls(email_address=email_address)
            session.add(email)
            session.commit()
            return email
        except Exception as e:
            session.rollback()  # Откат транзакции в случае ошибки
            return None

# Инициализация SQLite базы данных
def init_db(db_path="sqlite:///recon_data.db"):
    engine = create_engine(db_path, echo=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
    
def update_ip_domain_association(session, ip_address, domain_name):
  ip_resource = IPResource.create(session, ip_address=ip_address)
  domain = Domain.create(session, name=domain_name)

  if domain not in ip_resource.domains:
    ip_resource.domains.append(domain)

  session.commit()