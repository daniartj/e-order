from django.urls import path

from . import views

app_name = 'kasir'

urlpatterns = [
    path('login/',     views.login_kasir,  name='login'),
    path('logout/',    views.logout_kasir, name='logout'),
    path('dashboard/', views.dashboard,    name='dashboard'),

    path('update-status/<str:nomor_pesanan>/',
         views.update_status,  name='update_status'),
    path('detail-pesanan/<str:nomor_pesanan>/',
         views.detail_pesanan, name='detail_pesanan'),
    path('api/daftar-pesanan/',
         views.api_daftar_pesanan, name='api_daftar_pesanan'),

    # Kelola Meja
    path('meja/',                    views.kelola_meja,    name='kelola_meja'),
    path('meja/tambah/',             views.tambah_meja,    name='tambah_meja'),
    path('meja/edit/<int:meja_id>/', views.edit_meja,      name='edit_meja'),
    path('meja/toggle/<int:meja_id>/',views.toggle_meja,   name='toggle_meja'),

    # Kelola Kategori
    path('kategori/',                        views.kelola_kategori,  name='kelola_kategori'),
    path('kategori/tambah/',                 views.tambah_kategori,  name='tambah_kategori'),
    path('kategori/edit/<int:kategori_id>/', views.edit_kategori,    name='edit_kategori'),
    path('kategori/toggle/<int:kategori_id>/',views.toggle_kategori, name='toggle_kategori'),

    # Kelola Menu
    path('menu/',                    views.kelola_menu,  name='kelola_menu'),
    path('menu/tambah/',             views.tambah_menu,  name='tambah_menu'),
    path('menu/edit/<int:menu_id>/', views.edit_menu,    name='edit_menu'),
    path('menu/toggle/<int:menu_id>/',views.toggle_menu, name='toggle_menu'),

    # Laporan Transaksi
    path('laporan/transaksi/hari-ini/',  views.lt_hari_ini,  name='lt_hari_ini'),
    path('laporan/transaksi/bulan-ini/', views.lt_bulan_ini, name='lt_bulan_ini'),
    path('laporan/transaksi/tahun-ini/', views.lt_tahun_ini, name='lt_tahun_ini'),
    path('laporan/transaksi/semua/',     views.lt_semua,     name='lt_semua'),

    # Laporan Penjualan
    path('laporan/penjualan/hari-ini/',  views.lp_hari_ini,  name='lp_hari_ini'),
    path('laporan/penjualan/bulan-ini/', views.lp_bulan_ini, name='lp_bulan_ini'),
    path('laporan/penjualan/tahun-ini/', views.lp_tahun_ini, name='lp_tahun_ini'),
    path('laporan/penjualan/semua/',     views.lp_semua,     name='lp_semua'),

    # QR Code
path('meja/qr/<int:meja_id>/',
     views.preview_qr,
     name='preview_qr'),

path('meja/qr/download/<int:meja_id>/',
     views.download_qr,
     name='download_qr'),
     
path('struk/<str:nomor_pesanan>/',
     views.cetak_struk,
     name='cetak_struk'),

# Pengaturan
path('pengaturan/',
     views.pengaturan,
     name='pengaturan'),

path('pengaturan/simpan/',
     views.simpan_pengaturan,
     name='simpan_pengaturan'),

path('pengaturan/ip-saya/',
     views.get_ip_saya,
     name='get_ip_saya'),
# Export Excel
path('export/transaksi/',
     views.export_transaksi_excel,
     name='export_transaksi'),

path('export/penjualan/',
     views.export_penjualan_excel,
     name='export_penjualan'),

# Push Notification
path('push/subscribe/',
     views.push_subscribe,
     name='push_subscribe'),

path('push/unsubscribe/',
     views.push_unsubscribe,
     name='push_unsubscribe'),

path('push/vapid-key/',
     views.push_vapid_public_key,
     name='push_vapid_key'),
]