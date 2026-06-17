import requests
from django.conf import settings


class WhatsAppProvider:
    """
    Base class untuk WhatsApp provider.
    Ganti provider dengan mudah tanpa ubah kode lain.
    """
    def kirim(self, nomor: str, pesan: str) -> dict:
        raise NotImplementedError


class FonnteProvider(WhatsAppProvider):
    """
    Provider: Fonnte
    Dokumentasi: https://fonnte.com/docs
    Daftar gratis di: https://fonnte.com
    """
    API_URL = 'https://api.fonnte.com/send'

    def kirim(self, nomor: str, pesan: str) -> dict:
        try:
            response = requests.post(
                self.API_URL,
                headers={
                    'Authorization': settings.WHATSAPP_TOKEN
                },
                data={
                    'target'  : nomor,
                    'message' : pesan,
                    'countryCode': '62',
                },
                timeout=10
            )
            data = response.json()
            return {
                'sukses' : data.get('status', False),
                'pesan'  : data.get('detail', ''),
                'raw'    : data,
            }
        except requests.exceptions.Timeout:
            return {'sukses': False, 'pesan': 'Timeout: server tidak merespons'}
        except requests.exceptions.ConnectionError:
            return {'sukses': False, 'pesan': 'Gagal koneksi ke server WhatsApp'}
        except Exception as e:
            return {'sukses': False, 'pesan': str(e)}


class UltramsgProvider(WhatsAppProvider):
    """
    Provider: Ultramsg (backup)
    Dokumentasi: https://ultramsg.com/docs
    """
    def kirim(self, nomor: str, pesan: str) -> dict:
        try:
            instance_id = getattr(settings, 'ULTRAMSG_INSTANCE', '')
            token       = settings.WHATSAPP_TOKEN
            url         = f'https://api.ultramsg.com/{instance_id}/messages/chat'

            response = requests.post(
                url,
                data={
                    'token'  : token,
                    'to'     : f'+{nomor}',
                    'body'   : pesan,
                },
                timeout=10
            )
            data = response.json()
            return {
                'sukses': data.get('sent') == 'true',
                'pesan' : data.get('message', ''),
                'raw'   : data,
            }
        except Exception as e:
            return {'sukses': False, 'pesan': str(e)}


def get_provider() -> WhatsAppProvider:
    """
    Ambil provider sesuai settings.
    Mudah diganti tanpa ubah kode lain.
    """
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'fonnte')
    if provider == 'ultramsg':
        return UltramsgProvider()
    return FonnteProvider()


def kirim_notifikasi(nomor: str, pesan: str) -> dict:
    """
    Fungsi utama — panggil ini dari views.
    """
    if not nomor:
        return {'sukses': False, 'pesan': 'Nomor tidak tersedia'}

    if not getattr(settings, 'WHATSAPP_TOKEN', ''):
        return {'sukses': False, 'pesan': 'Token WhatsApp belum dikonfigurasi'}

    provider = get_provider()
    return provider.kirim(nomor, pesan)


def pesan_diproses(nomor_pesanan: str, nomor_meja: str) -> str:
    """Template pesan saat pesanan diproses."""
    return (
        f"*E-Order*\n\n"
        f"Halo! Pesanan Anda sedang diproses.\n\n"
        f"*No. Pesanan:* {nomor_pesanan}\n"
        f"*Meja:* {nomor_meja}\n\n"
        f"👨‍🍳 Dapur sedang menyiapkan pesanan Anda.\n"
        f"Mohon tunggu sebentar ya! 🙏"
    )


def pesan_selesai(nomor_pesanan: str, nomor_meja: str) -> str:
    """Template pesan saat pesanan selesai."""
    return (
        f"✅ *E-Order*\n\n"
        f"Pesanan Anda sudah siap!\n\n"
        f"*Nomor. Pesanan:* {nomor_pesanan}\n"
        f"*Meja:* {nomor_meja}\n\n"
        f"Silahkan dinikmati! 😊\n"
        f"Terima kasih sudah memesan di kafe kami. 🙏"
    )