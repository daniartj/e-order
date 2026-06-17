from django.urls import path

from . import views

app_name = 'pelanggan'

urlpatterns = [
    path('',
         views.halaman_utama,
         name='utama'),

    path('menu/<str:nomor_meja>/',
         views.halaman_menu,
         name='menu'),

    path('daftar-menu/',
         views.halaman_daftar_menu,
         name='daftar_menu'),

    path('simpan-keranjang/',
         views.simpan_keranjang,
         name='simpan_keranjang'),

    path('checkout/',
         views.halaman_checkout,
         name='checkout'),

    path('proses-checkout/',
         views.proses_checkout,
         name='proses_checkout'),

    path('pesanan-sukses/<str:nomor_pesanan>/',
         views.pesanan_sukses,
         name='pesanan_sukses'),

    path('api/status-pesanan/<str:nomor_pesanan>/',
         views.api_status_pesanan,
         name='api_status_pesanan'),

    path('api/session-status/',
         views.api_session_status,
         name='api_session_status'),

    path('hapus-session/',
         views.hapus_session,
         name='hapus_session'),

    path('reset-session/',
         views.reset_session,
         name='reset_session'),

    path('session-expired/',
         views.session_expired,
         name='session_expired'),
]