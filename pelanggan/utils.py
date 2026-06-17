import ipaddress


def get_client_ip(request) -> str:
    """Ambil IP address pelanggan dari request."""
    # Cek X-Forwarded-For (jika pakai proxy/nginx)
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def ip_diizinkan(ip_client: str, ip_range_text: str) -> bool:
    """
    Cek apakah IP client ada dalam range yang diizinkan.
    ip_range_text: string dengan IP/CIDR per baris.
    """
    if not ip_range_text.strip():
        return True  # Tidak ada range → izinkan semua

    try:
        client = ipaddress.ip_address(ip_client)
    except ValueError:
        return False

    for baris in ip_range_text.strip().splitlines():
        baris = baris.strip()
        if not baris:
            continue
        try:
            # Cek apakah format CIDR (192.168.1.0/24)
            if '/' in baris:
                network = ipaddress.ip_network(baris, strict=False)
                if client in network:
                    return True
            else:
                # IP tunggal
                if client == ipaddress.ip_address(baris):
                    return True
        except ValueError:
            continue

    return False