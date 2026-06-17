from menu.models import Pengaturan


def setting_kasir(request):
    """
    Make `setting` available in all kasir templates (used by notif audio loop).
    """
    try:
        return {'setting': Pengaturan.get()}
    except Exception:
        return {'setting': None}
