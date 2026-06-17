import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from menu.models import (DetailPesanan, KategoriMenu, Meja, Menu, Pengaturan,
                         Pesanan)
from pelanggan.utils import get_client_ip, ip_diizinkan


def halaman_utama(request):
    return render(request, 'pelanggan/home.html')


def halaman_menu(request, nomor_meja):
    nomor_meja = nomor_meja.upper() if not nomor_meja.isdigit() else nomor_meja

    # Validasi meja
    try:
        meja = Meja.objects.get(nomor_meja=nomor_meja, is_aktif=True)
    except Meja.DoesNotExist:
        return render(request, 'pelanggan/meja_tidak_ditemukan.html', {
            'nomor_meja': nomor_meja
        })

    # ==============================
    # GATE WIFI (cek IP di splash)
    # ==============================
    try:
        setting = Pengaturan.get()
    except Exception:
        setting = None

    if setting and setting.wifi_aktif:
        ip_client = get_client_ip(request)
        if not ip_diizinkan(ip_client, setting.wifi_ip_range):
            return render(request, 'pelanggan/akses_ditolak.html', {
                'pesan': setting.pesan_wifi,
                'wifi_password': setting.wifi_password,
            })

    meja_lama = request.session.get('nomor_meja')

    if meja_lama and meja_lama != nomor_meja:
        # Pindah meja → reset semua
        request.session['keranjang']      = {}
        request.session['daftar_pesanan'] = []
        request.session['waktu_masuk']    = timezone.now().isoformat()
    elif not meja_lama:
        # Pertama kali scan
        request.session['waktu_masuk'] = timezone.now().isoformat()

    request.session['nomor_meja'] = nomor_meja

    if 'keranjang' not in request.session:
        request.session['keranjang'] = {}
    if 'daftar_pesanan' not in request.session:
        request.session['daftar_pesanan'] = []

    request.session.modified = True

    # ✅ Kirim session_key ke template untuk localStorage isolation
    return render(request, 'pelanggan/splash.html', {
        'nomor_meja' : nomor_meja,
        'nama_meja'  : meja.nama_meja,
        'session_key': request.session.session_key,
    })


def halaman_daftar_menu(request):
    nomor_meja = request.session.get('nomor_meja')
    if not nomor_meja:
        return redirect('pelanggan:utama')

    # DEBUG: cek session state
    import logging
    logging.warning(f"session_expired: {getattr(request, 'session_expired', 'NOT SET')}")
    logging.warning(f"waktu_masuk: {request.session.get('waktu_masuk')}")

    semua_kategori = KategoriMenu.objects.filter(is_aktif=True)
    semua_menu     = Menu.objects.filter(
        is_tersedia=True
    ).select_related('kategori')

    data_menu = []
    for item in semua_menu:
        data_menu.append({
            'id'          : item.id,
            'nama_menu'   : item.nama_menu,
            'deskripsi'   : item.deskripsi,
            'harga'       : item.harga,
            'harga_format': item.harga_format(),
            'foto'        : item.foto.url if item.foto else None,
            'kategori_id' : item.kategori.id if item.kategori else None,
            'is_unggulan' : item.is_unggulan,
        })

    data_kategori = []
    for kat in semua_kategori:
        data_kategori.append({
            'id'           : kat.id,
            'nama_kategori': kat.nama_kategori,
            'ikon'         : kat.ikon,
        })

    daftar_pesanan_aktif = []
    daftar_nomor         = request.session.get('daftar_pesanan', [])
    daftar_nomor_valid   = []

    for nomor in daftar_nomor:
        try:
            obj = Pesanan.objects.prefetch_related('detail').get(
                nomor_pesanan=nomor
            )
            daftar_pesanan_aktif.append(obj)
            daftar_nomor_valid.append(nomor)
        except Pesanan.DoesNotExist:
            pass

    request.session['daftar_pesanan'] = daftar_nomor_valid
    request.session.modified          = True

    return render(request, 'pelanggan/menu.html', {
        'nomor_meja'           : nomor_meja,
        'data_menu_json'       : json.dumps(data_menu),
        'data_kategori_json'   : json.dumps(data_kategori),
        'jumlah_keranjang'     : sum(
            item['jumlah']
            for item in request.session.get('keranjang', {}).values()
        ),
        'daftar_pesanan_aktif' : daftar_pesanan_aktif,
        'session_key'          : request.session.session_key,
    })


@require_POST
def simpan_keranjang(request):
    try:
        data      = json.loads(request.body)
        keranjang = data.get('keranjang', {})

        if not keranjang:
            return JsonResponse({
                'status': 'error',
                'pesan' : 'Keranjang kosong'
            }, status=400)

        request.session['keranjang'] = keranjang
        request.session.modified     = True

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'pesan' : str(e)
        }, status=400)


def halaman_checkout(request):
    nomor_meja = request.session.get('nomor_meja')
    keranjang  = request.session.get('keranjang', {})

    if not nomor_meja or not keranjang:
        return redirect('pelanggan:utama')

    total_harga = sum(
        item['harga'] * item['jumlah']
        for item in keranjang.values()
    )

    # ✅ Ambil pengaturan untuk QRIS
    try:
        from menu.models import Pengaturan
        pengaturan = Pengaturan.get()
    except Exception:
        pengaturan = None

    return render(request, 'pelanggan/checkout.html', {
        'nomor_meja' : nomor_meja,
        'keranjang'  : keranjang,
        'total_harga': total_harga,
        'pengaturan' : pengaturan,   # ✅ kirim ke template
    })


@require_POST
def proses_checkout(request):
    try:
        data         = json.loads(request.body)
        metode_bayar = data.get('metode_bayar', 'tunai')
        nomor_wa     = data.get('nomor_wa', '').strip()
        catatan      = data.get('catatan', '').strip()
        nomor_meja   = request.session.get('nomor_meja')
        keranjang    = request.session.get('keranjang', {})

        if not nomor_meja:
            return JsonResponse({
                'status': 'error',
                'pesan' : 'Sesi meja tidak ditemukan. Scan QR ulang.'
            }, status=400)

        if not keranjang:
            return JsonResponse({
                'status': 'error',
                'pesan' : 'Keranjang kosong.'
            }, status=400)

        try:
            meja = Meja.objects.get(nomor_meja=nomor_meja)
        except Meja.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'pesan' : f'Meja {nomor_meja} tidak ditemukan.'
            }, status=400)

        if nomor_wa:
            if nomor_wa.startswith('0'):
                nomor_wa = '62' + nomor_wa[1:]
            elif not nomor_wa.startswith('62'):
                nomor_wa = '62' + nomor_wa

        total_harga = sum(
            item['harga'] * item['jumlah']
            for item in keranjang.values()
        )

        pesanan = Pesanan(
            meja           = meja,
            nomor_whatsapp = nomor_wa if nomor_wa else None,
            status         = 'pending',
            metode_bayar   = metode_bayar,
            catatan        = catatan,
            total_harga    = total_harga,
            session_key    = request.session.session_key or '',
        )
        pesanan.save()

        for id_menu, item in keranjang.items():
            try:
                obj_menu = Menu.objects.get(id=int(id_menu))
            except Menu.DoesNotExist:
                obj_menu = None

            DetailPesanan(
                pesanan            = pesanan,
                menu               = obj_menu,
                nama_menu_snapshot = item['nama_menu'],
                harga_snapshot     = item['harga'],
                jumlah             = item['jumlah'],
                catatan_item       = '',
            ).save()

        request.session['keranjang'] = {}
        daftar_pesanan = request.session.get('daftar_pesanan', [])
        daftar_pesanan.append(pesanan.nomor_pesanan)
        request.session['daftar_pesanan'] = daftar_pesanan
        request.session.modified          = True
        # ✅ Kirim push notification ke kasir
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "[PUSH trigger pelanggan.checkout] Pesanan %s pending. meja=%s total=%s",
                pesanan.nomor_pesanan,
                nomor_meja,
                total_harga,
            )

            from kasir.push import kirim_push_semua_kasir
            item_str = ', '.join([
                f"{v['jumlah']}x {v['nama_menu']}"
                for v in keranjang.values()
            ])
            kirim_push_semua_kasir(
                judul = f'🔔 Pesanan Baru — Meja {nomor_meja}',
                isi   = f'{item_str}\nTotal: Rp {total_harga:,}',
                url   = '/kasir/dashboard/',
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("[PUSH trigger pelanggan.checkout] gagal kirim push. err=%s", e)

        from django.urls import reverse
        redirect_url = reverse(
            'pelanggan:pesanan_sukses',
            kwargs={'nomor_pesanan': pesanan.nomor_pesanan}
        )

        return JsonResponse({
            'status'       : 'ok',
            'redirect_url' : redirect_url,
            'nomor_pesanan': pesanan.nomor_pesanan,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'pesan' : 'Format data tidak valid.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'pesan' : f'Terjadi kesalahan: {str(e)}'
        }, status=500)


def pesanan_sukses(request, nomor_pesanan):
    try:
        pesanan = Pesanan.objects.prefetch_related('detail').get(
            nomor_pesanan=nomor_pesanan
        )
    except Pesanan.DoesNotExist:
        return redirect('pelanggan:utama')

    return render(request, 'pelanggan/sukses.html', {
        'pesanan'   : pesanan,
        'nomor_meja': request.session.get('nomor_meja', ''),
    })


def api_status_pesanan(request, nomor_pesanan):
    try:
        pesanan = Pesanan.objects.get(nomor_pesanan=nomor_pesanan)
        return JsonResponse({
            'status': pesanan.status,
            'label' : pesanan.get_status_display(),
        })
    except Pesanan.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'pesan' : 'Pesanan tidak ditemukan'
        }, status=404)


def api_session_status(request):
    """
    API untuk cek status session pelanggan (untuk polling real-time).
    """
    from menu.models import Pengaturan
    setting = None
    try:
        setting = Pengaturan.get()
    except Exception:
        setting = None

    durasi_menit = getattr(setting, 'durasi_session', 10)

    nomor_meja = request.session.get('nomor_meja', '')
    waktu_masuk_str = request.session.get('waktu_masuk')

    session_expired = False
    sisa_menit = durasi_menit

    if waktu_masuk_str:
        try:
            waktu_masuk = timezone.datetime.fromisoformat(waktu_masuk_str)  # type: ignore[attr-defined]
        except Exception:
            # fallback: parsing tanpa timezone info
            try:
                waktu_masuk = datetime.datetime.fromisoformat(waktu_masuk_str)
            except Exception:
                waktu_masuk = None

        if waktu_masuk is not None:
            try:
                if waktu_masuk.tzinfo is None:
                    waktu_masuk = timezone.make_aware(waktu_masuk)
                selisih = timezone.now() - waktu_masuk
                menit = selisih.total_seconds() / 60
                if menit >= durasi_menit:
                    session_expired = True
                    sisa_menit = 0
                else:
                    session_expired = False
                    sisa_menit = max(0, durasi_menit - menit)
            except Exception:
                # biarkan default durasi_menit
                session_expired = getattr(request, 'session_expired', False)
                sisa_menit = getattr(request, 'sisa_menit', durasi_menit)

    # Jika middleware sudah menghitung, utamakan nilai middleware
    session_expired = getattr(request, 'session_expired', session_expired)
    sisa_menit = getattr(request, 'sisa_menit', sisa_menit)

    return JsonResponse({
        'session_expired': session_expired,
        'sisa_menit'     : sisa_menit,
        'nomor_meja'     : nomor_meja,
    })


@require_POST
def hapus_session(request):
    for kunci in ['nomor_meja', 'waktu_masuk',
                  'keranjang', 'daftar_pesanan']:
        if kunci in request.session:
            del request.session[kunci]
    request.session.modified = True
    return JsonResponse({'status': 'ok'})


@require_POST
def reset_session(request):
    """Reset timer.
    Untuk menjaga popup tetap bisa muncul lagi, ubah waktu_masuk ke sekarang
    (bukan menghapusnya)."""
    request.session['waktu_masuk'] = timezone.now().isoformat()
    request.session.modified = True
    return JsonResponse({'status': 'ok'})


def session_expired(request):
    return render(request, 'pelanggan/session_expired.html')