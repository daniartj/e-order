from pywebpush import webpush, WebPushException
from django.conf import settings
from menu.models import PushSubscription
import json
import logging

logger = logging.getLogger(__name__)


def kirim_push_semua_kasir(
    judul: str,
    isi  : str,
    url  : str = '/kasir/dashboard/'
):
    subscriptions = PushSubscription.objects.all()

    if not subscriptions.exists():
        print('[PUSH] Tidak ada subscription')
        return

    private_key = settings.VAPID_PRIVATE_KEY
    if not private_key:
        print('[PUSH] VAPID_PRIVATE_KEY kosong')
        return

    data = json.dumps({
        'title': judul,
        'body' : isi,
        'url'  : url,
        'icon' : '/static/img/icons/icon-192.png',
        'badge': '/static/img/icons/icon-72.png',
    })

    gagal = []
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {
                        'p256dh': sub.p256dh,
                        'auth'  : sub.auth,
                    }
                },
                data              = data,
                vapid_private_key = private_key,
                vapid_claims      = settings.VAPID_CLAIMS,
                content_encoding  = 'aes128gcm',  # ✅ encoding terbaru
            )
            print(f'[PUSH] Terkirim ke {sub.user.username}')

        except WebPushException as e:
            print(f'[PUSH] WebPushException: {repr(e)}')
            if e.response and e.response.status_code in [404, 410]:
                gagal.append(sub.id)

        except Exception as e:
            print(f'[PUSH] Error: {e}')

    if gagal:
        PushSubscription.objects.filter(id__in=gagal).delete()
        print(f'[PUSH] Hapus {len(gagal)} subscription tidak valid')