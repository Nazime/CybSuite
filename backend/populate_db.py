from main import Host, Service, engine, SessionLocal
import random
from ipaddress import IPv4Address

def generate_random_ip():
    # Generate a random IP address (excluding reserved ranges)
    while True:
        ip = str(IPv4Address(random.randint(0x01000000, 0xFFFFFFFF)))
        # Skip private IP ranges
        if not (ip.startswith('10.') or ip.startswith('172.16.') or ip.startswith('192.168.')):
            return ip

def populate_database():
    db = SessionLocal()

    # Common protocols and their typical ports
    common_services = [
        ('tcp', 80),    # HTTP
        ('tcp', 443),   # HTTPS
        ('tcp', 22),    # SSH
        ('tcp', 21),    # FTP
        ('tcp', 25),    # SMTP
        ('tcp', 53),    # DNS
        ('tcp', 3306),  # MySQL
        ('tcp', 5432),  # PostgreSQL
        ('tcp', 8080),  # Alternative HTTP
        ('udp', 53),    # DNS
        ('udp', 161),   # SNMP
        ('udp', 123),   # NTP
    ]

    try:
        # Create 20 hosts
        for _ in range(20):
            # Create host
            host = Host(ip=generate_random_ip())
            db.add(host)
            db.flush()  # To get the host ID

            # Generate 5-10 random services for this host
            num_services = random.randint(5, 10)
            selected_services = random.sample(common_services, num_services)

            # Add services for this host
            for protocol, port in selected_services:
                service = Service(
                    host_id=host.id,
                    port=port,
                    protocol=protocol
                )
                db.add(service)

        db.commit()
        print("Database populated successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables (if they don't exist)
    from main import Base
    Base.metadata.create_all(bind=engine)

    # Populate the database
    populate_database()