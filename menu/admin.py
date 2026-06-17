from django.contrib import admin

from .models import (DetailPesanan, KategoriMenu, Meja, Menu, Pengaturan,
                     Pesanan)


# ==============================
# INLINE: Detail Pesanan di dalam Pesanan
# ==============================
class DetailPesananInline(admin.TabularInline):
    model = DetailPesanan
    extra = 0
    readonly_fields = ['subtotal', 'nama_menu_snapshot', 'harga_snapshot']
    fields = [
        'menu', 'nama_menu_snapshot', 'harga_snapshot',
        'jumlah', 'subtotal', 'catatan_item'
    ]


# ==============================
# ADMIN: MEJA
# ==============================
@admin.register(Meja)
class MejaAdmin(admin.ModelAdmin):
    list_display  = ['nomor_meja', 'nama_meja', 'kapasitas', 'is_aktif']
    list_filter   = ['is_aktif']
    search_fields = ['nomor_meja', 'nama_meja']
    readonly_fields = ['qr_code']


# ==============================
# ADMIN: KATEGORI MENU
# ==============================
@admin.register(KategoriMenu)
class KategoriMenuAdmin(admin.ModelAdmin):
    list_display = ['ikon', 'nama_kategori', 'urutan', 'is_aktif']
    list_editable = ['urutan', 'is_aktif']
    ordering = ['urutan']


# ==============================
# ADMIN: MENU
# ==============================
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display  = [
        'nama_menu', 'kategori', 'harga_format',
        'is_tersedia', 'is_unggulan'
    ]
    list_filter   = ['kategori', 'is_tersedia', 'is_unggulan']
    list_editable = ['is_tersedia', 'is_unggulan']
    search_fields = ['nama_menu']


# ==============================
# ADMIN: PESANAN
# ==============================
@admin.register(Pesanan)
class PesananAdmin(admin.ModelAdmin):
    list_display  = [
        'nomor_pesanan', 'meja', 'status',
        'metode_bayar', 'total_format', 'waktu_pesan'
    ]
    list_filter   = ['status', 'metode_bayar']
    search_fields = ['nomor_pesanan', 'nomor_whatsapp']
    readonly_fields = ['nomor_pesanan', 'waktu_pesan', 'session_key']
    inlines = [DetailPesananInline]


# ==============================
# ADMIN: DETAIL PESANAN
# ==============================
@admin.register(DetailPesanan)
class DetailPesananAdmin(admin.ModelAdmin):
    list_display = [
        'pesanan', 'nama_menu_snapshot',
        'jumlah', 'harga_snapshot', 'subtotal'
    ]
    readonly_fields = ['subtotal']


@admin.register(Pengaturan)
class PengaturanAdmin(admin.ModelAdmin):
    list_display = ['nama_kafe', 'wifi_aktif', 'durasi_session']