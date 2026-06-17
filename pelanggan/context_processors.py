def session_pelanggan(request):
    SKIP_PATH = ['/kasir/', '/admin/', '/static/', '/media/']
    for path in SKIP_PATH:
        if request.path.startswith(path):
            return {
                'session_expired'   : False,
                'sisa_menit'        : 10,
                'nomor_meja_session': '',
            }

    # ✅ Baca durasi dari database sebagai default
    try:
        from menu.models import Pengaturan
        durasi = Pengaturan.get().durasi_session
    except Exception:
        durasi = 10

    return {
        'session_expired'   : getattr(request, 'session_expired', False),
        'sisa_menit'        : getattr(request, 'sisa_menit', durasi),
        'nomor_meja_session': request.session.get('nomor_meja', ''),
    }