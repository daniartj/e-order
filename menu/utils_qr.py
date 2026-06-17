from io import BytesIO

import qrcode
import qrcode.image.svg
from PIL import Image, ImageDraw


def generate_qr_bytes(url: str, ukuran: int = 300) -> bytes:
    """
    Generate QR Code dari URL.
    Return bytes gambar PNG.
    """
    qr = qrcode.QRCode(
        version           = 1,
        error_correction  = qrcode.constants.ERROR_CORRECT_H,
        box_size          = 10,
        border            = 4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color  = '#1C1C1E',
        back_color  = 'white'
    )

    # Resize ke ukuran yang diinginkan
    img = img.resize((ukuran, ukuran), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()


def generate_qr_dengan_label(
    url         : str,
    nomor_meja  : str,
    nama_kafe   : str = 'E-Order',
    ukuran      : int = 400,
) -> bytes:
    """
    Generate QR Code lengkap dengan label:
    - Nama kafe di atas
    - QR Code di tengah
    - Nomor meja di bawah
    - Instruksi scan di bawahnya
    """
    # --- Buat QR Code ---
    qr = qrcode.QRCode(
        version           = 1,
        error_correction  = qrcode.constants.ERROR_CORRECT_H,
        box_size          = 10,
        border            = 3,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color = '#1C1C1E',
        back_color = 'white'
    ).convert('RGB')

    qr_size = ukuran - 40
    qr_img  = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # --- Buat canvas total ---
    tinggi_total = ukuran + 160
    canvas = Image.new('RGB', (ukuran, tinggi_total), '#FFFFFF')
    draw   = ImageDraw.Draw(canvas)

    # --- Background header ---
    draw.rectangle(
        [(0, 0), (ukuran, 70)],
        fill='#1C1C1E'
    )

    # --- Teks nama kafe ---
    try:
        # Coba pakai font sistem
        from PIL import ImageFont
        font_judul = ImageFont.truetype(
            'arial.ttf', 28
        )
        font_meja  = ImageFont.truetype('arial.ttf', 36)
        font_kecil = ImageFont.truetype('arial.ttf', 18)
    except Exception:
        # Fallback ke font default
        font_judul = ImageFont.load_default()
        font_meja  = ImageFont.load_default()
        font_kecil = ImageFont.load_default()

    # Nama kafe (header putih)
    teks_kafe = f'☕ {nama_kafe}'
    bbox      = draw.textbbox((0, 0), teks_kafe, font=font_judul)
    lebar_teks = bbox[2] - bbox[0]
    draw.text(
        ((ukuran - lebar_teks) // 2, 20),
        teks_kafe,
        fill='white',
        font=font_judul
    )

    # --- Paste QR di tengah ---
    posisi_qr = ((ukuran - qr_size) // 2, 80)
    canvas.paste(qr_img, posisi_qr)

    # --- Background footer ---
    y_footer = 80 + qr_size + 10
    draw.rectangle(
        [(0, y_footer), (ukuran, tinggi_total)],
        fill='#F9FAFB'
    )

    # Teks nomor meja
    teks_meja = f'Meja {nomor_meja}'
    bbox      = draw.textbbox((0, 0), teks_meja, font=font_meja)
    lebar     = bbox[2] - bbox[0]
    draw.text(
        ((ukuran - lebar) // 2, y_footer + 10),
        teks_meja,
        fill='#1C1C1E',
        font=font_meja
    )

    # Instruksi scan
    teks_scan = 'Scan untuk memesan'
    bbox      = draw.textbbox((0, 0), teks_scan, font=font_kecil)
    lebar     = bbox[2] - bbox[0]
    draw.text(
        ((ukuran - lebar) // 2, y_footer + 60),
        teks_scan,
        fill='#6B7280',
        font=font_kecil
    )

    # Teks URL kecil
    teks_url = url
    try:
        font_url = ImageFont.truetype('arial.ttf', 14)
    except Exception:
        font_url = font_kecil
    bbox     = draw.textbbox((0, 0), teks_url, font=font_url)
    lebar    = bbox[2] - bbox[0]
    draw.text(
        ((ukuran - lebar) // 2, y_footer + 90),
        teks_url,
        fill='#9CA3AF',
        font=font_url
    )

    # --- Return sebagai bytes ---
    buffer = BytesIO()
    canvas.save(buffer, format='PNG', dpi=(300, 300))
    buffer.seek(0)
    return buffer.getvalue()