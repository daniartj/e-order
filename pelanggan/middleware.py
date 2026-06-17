import datetime

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from menu.models import Pengaturan
from pelanggan.utils import get_client_ip, ip_diizinkan


class SessionPelangganMiddleware(MiddlewareMixin):

    URL_BEBAS = [
        '/kasir/',
        '/admin/',
        '/static/',
        '/media/',
        '/',
        '/session-expired/',
        '/hapus-session/',
        '/reset-session/',
        '/api/status-pesanan/',
        '/akses-ditolak/',
        '/tutup/',
    ]

    URL_BUTUH_SESSION = [
        '/daftar-menu/',
        '/checkout/',
        '/proses-checkout/',
        '/simpan-keranjang/',
        '/api/session-status/',
    ]

    def process_request(self, request):
        print(f"[MIDDLEWARE HIT] path={request.path}")

        # Skip middleware session timer untuk akses kasir/admin saja.
        # Endpoint pelanggan (termasuk /api/session-status/) tetap harus dihitung.
        if request.user.is_authenticated and (
            request.path.startswith('/kasir/') or request.path.startswith('/admin/')
        ):
            print("[DEBUG MW] skip untuk kasir/admin karena request.user.is_authenticated=True")
            return None




        # Skip URL bebas
        for url in self.URL_BEBAS:
            if request.path.startswith(url):
                return None

        # Ambil pengaturan
        try:
            setting = Pengaturan.get()
        except Exception:
            setting = None

        # ==============================
        # CEK JAM OPERASIONAL
        # ==============================
        if setting and setting.cek_jam_operasional:
            jam_sekarang = timezone.localtime(
                timezone.now()
            ).time()
            if not (setting.jam_buka <= jam_sekarang <= setting.jam_tutup):
                return render(
                    request,
                    'pelanggan/tutup.html',
                    {
                        'jam_buka' : setting.jam_buka.strftime('%H:%M'),
                        'jam_tutup': setting.jam_tutup.strftime('%H:%M'),
                    }
                )

        # ==============================
        # CEK WIFI (hanya untuk /menu/)
        # ==============================
        if (setting and setting.wifi_aktif
                and request.path.startswith('/menu/')):
            ip_client = get_client_ip(request)
            if not ip_diizinkan(ip_client, setting.wifi_ip_range):
                return render(
                    request,
                    'pelanggan/akses_ditolak.html',
                    {
                        'pesan'         : setting.pesan_wifi,
                        'wifi_password': setting.wifi_password,
                    }
                )

        # ==============================
        # CEK SESSION
        # ==============================
        nomor_meja      = request.session.get('nomor_meja')
        waktu_masuk_str = request.session.get('waktu_masuk')

        butuh_session = any(
            request.path.startswith(url)
            for url in self.URL_BUTUH_SESSION
        )

        if request.path == '/api/session-status/':
            print(
                "[DEBUG MW SESSION STATUS]",
                "path=", request.path,
                "nomor_meja=", nomor_meja,
                "waktu_masuk_str=", waktu_masuk_str,
            )
        print(f"[DEBUG SESSION KEYS] nomor_meja={nomor_meja} waktu_masuk_str={waktu_masuk_str}")

        if not nomor_meja or not waktu_masuk_str:
            if butuh_session:
                return redirect('pelanggan:utama')
            return None


        try:
            import logging
            logging.warning("[DEBUG MW] waktu_masuk_str=%s", waktu_masuk_str)
            waktu_masuk = datetime.datetime.fromisoformat(waktu_masuk_str)

            if waktu_masuk.tzinfo is None:
                waktu_masuk = timezone.make_aware(waktu_masuk)

            selisih     = timezone.now() - waktu_masuk
            menit       = selisih.total_seconds() / 60
            BATAS_MENIT = setting.durasi_session if setting else 10

            import logging
            logging.warning(
                "[DEBUG SESSION] setting.durasi_session=%s waktu_masuk_str=%s menit=%.4f BATAS_MENIT=%s",
                getattr(setting, 'durasi_session', None),
                waktu_masuk_str,
                menit,
                BATAS_MENIT,
            )


            if menit >= BATAS_MENIT:
                # Hapus session
                for kunci in ['nomor_meja', 'waktu_masuk',
                              'keranjang', 'daftar_pesanan']:
                    if kunci in request.session:
                        del request.session[kunci]
                request.session.modified = True

                if (request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                        or 'application/json' in request.headers.get('Accept', '')):
                    return JsonResponse({
                        'status'         : 'error',
                        'session_expired': True,
                    }, status=401)

                return redirect('pelanggan:session_expired')

            request.session_expired = False
            request.sisa_menit      = max(0, BATAS_MENIT - menit)

        except Exception as e:
            import logging
            durasi_fallback = getattr(setting, 'durasi_session', None) if setting else None
            if durasi_fallback is None:
                durasi_fallback = 10

            logging.warning(
                "[DEBUG SESSION] exception=%s waktu_masuk_str=%s durasi_session=%s durasi_fallback=%s",
                repr(e),
                waktu_masuk_str,
                getattr(setting, 'durasi_session', None),
                durasi_fallback,
            )
            request.session_expired = False
            request.sisa_menit      = durasi_fallback


        return None