from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
import os


class Command(BaseCommand):
    help = 'Generate PWA icons dari logo.png'

    def handle(self, *args, **kwargs):
        logo_path = os.path.join(
            settings.STATICFILES_DIRS[0], 'img', 'logo.png'
        )
        output_dir = os.path.join(
            settings.STATICFILES_DIRS[0], 'img', 'icons'
        )
        os.makedirs(output_dir, exist_ok=True)

        ukuran_list = [72, 96, 128, 144, 152, 192, 384, 512]

        try:
            img = Image.open(logo_path).convert('RGBA')
        except FileNotFoundError:
            # Buat icon default jika tidak ada logo
            img = Image.new('RGBA', (512, 512), '#1C1C1E')
            self.stdout.write(
                self.style.WARNING(
                    'logo.png tidak ditemukan, '
                    'membuat icon default hitam'
                )
            )

        for ukuran in ukuran_list:
            icon = img.resize((ukuran, ukuran), Image.LANCZOS)
            output_path = os.path.join(
                output_dir, f'icon-{ukuran}.png'
            )
            icon.save(output_path, 'PNG')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ icon-{ukuran}.png dibuat'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Semua icon PWA berhasil dibuat!')
        )