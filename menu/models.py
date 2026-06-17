from django.db import models


class Meja(models.Model):
    """
    Representasi meja fisik di kafe.
    Setiap meja punya kode unik dan QR Code sendiri.
    """
    nomor_meja = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Nomor Meja'
    )
    nama_meja = models.CharField(
        max_length=50,
        verbose_name='Nama Meja',
        help_text='Contoh: Meja Sudut, Meja VIP'
    )
    kapasitas = models.PositiveIntegerField(
        default=4,
        verbose_name='Kapasitas (orang)'
    )
    is_aktif = models.BooleanField(
        default=True,
        verbose_name='Meja Aktif'
    )
    qr_code = models.ImageField(
        upload_to='qrcodes/',
        blank=True,
        null=True,
        verbose_name='QR Code'
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Meja'
        verbose_name_plural = 'Daftar Meja'
        ordering = ['nomor_meja']

    def __str__(self):
        return f'Meja {self.nomor_meja} — {self.nama_meja}'

    def get_url_menu(self):
        """URL yang di-encode ke dalam QR Code"""
        return f'/menu/{self.nomor_meja}/'


class KategoriMenu(models.Model):
    """
    Kategori pengelompokan menu.
    Contoh: Makanan, Minuman, Dessert, Snack
    """
    nama_kategori = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nama Kategori'
    )
    ikon = models.CharField(
        max_length=10,
        default='🍽️',
        verbose_name='Ikon Emoji',
        help_text='Gunakan emoji sebagai ikon kategori'
    )
    urutan = models.PositiveIntegerField(
        default=0,
        verbose_name='Urutan Tampil'
    )
    is_aktif = models.BooleanField(
        default=True,
        verbose_name='Kategori Aktif'
    )

    class Meta:
        verbose_name = 'Kategori Menu'
        verbose_name_plural = 'Kategori Menu'
        ordering = ['urutan', 'nama_kategori']

    def __str__(self):
        return f'{self.ikon} {self.nama_kategori}'


class Menu(models.Model):
    """
    Item menu yang tersedia di kafe.
    Punya foto, harga, kategori, dan status ketersediaan.
    """
    kategori = models.ForeignKey(
        KategoriMenu,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daftar_menu',
        verbose_name='Kategori'
    )
    nama_menu = models.CharField(
        max_length=100,
        verbose_name='Nama Menu'
    )
    deskripsi = models.TextField(
        blank=True,
        verbose_name='Deskripsi'
    )
    harga = models.PositiveIntegerField(
        verbose_name='Harga (Rp)'
    )
    foto = models.ImageField(
        upload_to='menu/',
        blank=True,
        null=True,
        verbose_name='Foto Menu'
    )
    is_tersedia = models.BooleanField(
        default=True,
        verbose_name='Tersedia'
    )
    is_unggulan = models.BooleanField(
        default=False,
        verbose_name='Menu Unggulan'
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Daftar Menu'
        ordering = ['kategori', 'nama_menu']

    def __str__(self):
        return f'{self.nama_menu} — Rp {self.harga:,}'

    def harga_format(self):
        """Format harga: 15000 → Rp 15.000"""
        return f'Rp {self.harga:,}'.replace(',', '.')


class Pesanan(models.Model):
    """
    Satu sesi pemesanan dari satu pelanggan.
    Dibuat saat pelanggan checkout.
    """

    STATUS_PILIHAN = [
        ('pending',  '⏳ Pending'),
        ('diproses', '👨‍🍳 Diproses'),
        ('selesai',  '✅ Selesai'),
        ('dibatal',  '❌ Dibatalkan'),
    ]

    METODE_BAYAR_PILIHAN = [
        ('tunai', '💵 Tunai'),
        ('qris',  '📱 QRIS'),
    ]

    meja = models.ForeignKey(
        Meja,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pesanan',
        verbose_name='Meja'
    )
    nomor_pesanan = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Nomor Pesanan',
        help_text='Auto-generate saat save'
    )
    nomor_whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Nomor WhatsApp'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_PILIHAN,
        default='pending',
        verbose_name='Status Pesanan'
    )
    metode_bayar = models.CharField(
        max_length=10,
        choices=METODE_BAYAR_PILIHAN,
        default='tunai',
        verbose_name='Metode Pembayaran'
    )
    catatan = models.TextField(
        blank=True,
        verbose_name='Catatan Pesanan'
    )
    total_harga = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Harga (Rp)'
    )
    # Simpan session key untuk identifikasi pelanggan
    session_key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Session Key'
    )
    waktu_pesan = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Pesan'
    )
    waktu_selesai = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Waktu Selesai'
    )

    class Meta:
        verbose_name = 'Pesanan'
        verbose_name_plural = 'Daftar Pesanan'
        ordering = ['-waktu_pesan']

    def __str__(self):
        return f'{self.nomor_pesanan} — Meja {self.meja} — {self.get_status_display()}'

    def total_format(self):
        """Format total: 45000 → Rp 45.000"""
        return f'Rp {self.total_harga:,}'.replace(',', '.')

    def save(self, *args, **kwargs):
        """
        Auto-generate nomor pesanan saat pertama dibuat.
        Format: ORD-20250101-0001
        """
        if not self.nomor_pesanan:
            import random

            from django.utils import timezone
            tanggal = timezone.now().strftime('%Y%m%d')
            angka_acak = random.randint(1000, 9999)
            self.nomor_pesanan = f'ORD-{tanggal}-{angka_acak}'
        super().save(*args, **kwargs)


class DetailPesanan(models.Model):
    """
    Satu baris item dalam sebuah pesanan.
    Contoh: 2x Kopi Susu @ Rp 18.000 = Rp 36.000
    """
    pesanan = models.ForeignKey(
        Pesanan,
        on_delete=models.CASCADE,
        related_name='detail',
        verbose_name='Pesanan'
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.SET_NULL,
        null=True,
        related_name='detail_pesanan',
        verbose_name='Menu'
    )
    # Snapshot harga saat dipesan (harga menu bisa berubah)
    nama_menu_snapshot  = models.CharField(max_length=100, verbose_name='Nama Menu')
    harga_snapshot      = models.PositiveIntegerField(verbose_name='Harga Saat Pesan')
    jumlah              = models.PositiveIntegerField(default=1, verbose_name='Jumlah')
    subtotal            = models.PositiveIntegerField(default=0, verbose_name='Subtotal')
    catatan_item        = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Catatan Item',
        help_text='Contoh: tanpa es, gula sedikit'
    )

    class Meta:
        verbose_name = 'Detail Pesanan'
        verbose_name_plural = 'Detail Pesanan'

    def __str__(self):
        return f'{self.jumlah}x {self.nama_menu_snapshot} — Rp {self.subtotal:,}'

    def save(self, *args, **kwargs):
        """Auto-hitung subtotal = jumlah × harga"""
        self.subtotal = self.jumlah * self.harga_snapshot
        super().save(*args, **kwargs)

    def subtotal_format(self):
        return f'Rp {self.subtotal:,}'.replace(',', '.')
    
class Pengaturan(models.Model):
    """
    Pengaturan global aplikasi E-Order.
    Hanya ada 1 row (singleton).
    """
    # Info Kafe
    nama_kafe       = models.CharField(
        max_length=100,
        default='E-Order Café',
        verbose_name='Nama Kafe'
    )
    alamat_kafe     = models.TextField(
        blank=True,
        verbose_name='Alamat Kafe'
    )
    telp_kafe       = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Nomor Telepon'
    )
    footer_struk    = models.CharField(
        max_length=200,
        default='Terima kasih sudah berkunjung!',
        verbose_name='Footer Struk'
    )
    # Notifikasi Suara — tambah di dalam class Pengaturan
    notif_suara_pilihan = models.CharField(
        max_length=10,
        choices=[
            ('1', 'Suara 1'),
            ('2', 'Suara 2'),
            ('3', 'Suara 3'),],
        default='1',
        verbose_name='Pilihan Suara'
    )
    notif_volume = models.FloatField(
        default=0.8,
        verbose_name='Volume (0.0 - 1.0)'
)
    notif_loop = models.BooleanField(
        default=True,
        verbose_name='Loop saat ada pesanan pending'
)

    # Gambar QRIS
    gambar_qris     = models.ImageField(
        upload_to='pengaturan/',
        blank=True,
        null=True,
        verbose_name='Gambar QRIS'
    )

    # Pembatasan WiFi
    wifi_aktif      = models.BooleanField(
        default=False,
        verbose_name='Aktifkan Pembatasan WiFi'
    )
    wifi_ip_range   = models.TextField(
        blank=True,
        verbose_name='Range IP yang Diizinkan',
        help_text=(
            'Satu IP atau range per baris.\n'
            'Contoh:\n'
            '192.168.1.0/24\n'
            '192.168.1.100\n'
            '10.0.0.0/8'
        )
    )
    pesan_wifi      = models.CharField(
        max_length=200,
        default='Anda harus terhubung ke WiFi kafe untuk memesan.',
        verbose_name='Pesan Error WiFi'
    )

    wifi_password  = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Password WiFi'
    )

    # Session
    durasi_session  = models.PositiveIntegerField(
        default=1,
        verbose_name='Durasi Session (menit)'
    )

    # Jam Operasional
    jam_buka        = models.TimeField(
        default='08:00',
        verbose_name='Jam Buka'
    )
    jam_tutup       = models.TimeField(
        default='22:00',
        verbose_name='Jam Tutup'
    )
    cek_jam_operasional = models.BooleanField(
        default=False,
        verbose_name='Aktifkan Cek Jam Operasional'
    )

    diupdate_pada   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Pengaturan'
        verbose_name_plural = 'Pengaturan'

    def __str__(self):
        return f'Pengaturan — {self.nama_kafe}'

    @classmethod
    def get(cls):
        """Ambil pengaturan (singleton)."""
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
    
class PushSubscription(models.Model):
    """
    Simpan subscription push notification per kasir.
    """
    user       = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name='User'
    )
    endpoint   = models.TextField(
        unique=True,
        verbose_name='Endpoint'
    )
    p256dh     = models.TextField(verbose_name='p256dh Key')
    auth       = models.TextField(verbose_name='Auth Key')
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'

    def __str__(self):
        return f'Push — {self.user.username}'