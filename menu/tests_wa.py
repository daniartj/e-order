import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eorder.settings')

from menu.whatsapp import kirim_notifikasi, pesan_diproses

# Ganti dengan nomor WA Anda (tanpa +)
NOMOR_TEST = '6282245131370'

hasil = kirim_notifikasi(
    NOMOR_TEST,
    pesan_diproses('ORD-TEST-001', 'T01')
)

print('Sukses :', hasil['sukses'])
print('Pesan  :', hasil['pesan'])