import ipaddress


def is_ip_address(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ip_address(ip: str):
    ipaddress.ip_address(ip)
