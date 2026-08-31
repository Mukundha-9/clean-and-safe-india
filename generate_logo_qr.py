import qrcode
from PIL import Image, ImageDraw, ImageOps

def create_perfect_circular_logo_qr(url, logo_path, output_path):
    # 1. Create QR code with Level H Error Correction (30% recovery)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 2. Base QR Image
    qr_img = qr.make_image(fill_color="#060911", back_color="#ffffff").convert('RGBA')
    qr_w, qr_h = qr_img.size

    # 3. Load Logo
    logo = Image.open(logo_path).convert('RGBA')
    
    # Crop to circular mask
    logo_size = int(qr_w * 0.22)
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Create circular mask for logo
    mask = Image.new('L', (logo_size, logo_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)
    
    circular_logo = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
    circular_logo.paste(logo, (0, 0), mask=mask)

    # 4. Create badge backing
    badge_size = logo_size + 20
    badge = Image.new('RGBA', (badge_size, badge_size), (0, 0, 0, 0))
    draw_badge = ImageDraw.Draw(badge)
    
    # Clean white circle with golden/emerald border
    draw_badge.ellipse((0, 0, badge_size - 1, badge_size - 1), fill=(255, 255, 255, 255), outline=(16, 185, 129, 255), width=5)
    
    # Paste circular logo in center of badge
    badge_offset = (badge_size - logo_size) // 2
    badge.paste(circular_logo, (badge_offset, badge_offset), circular_logo)

    # 5. Place on QR code center
    pos = ((qr_w - badge_size) // 2, (qr_h - badge_size) // 2)
    qr_img.paste(badge, pos, badge)

    qr_img.save(output_path, 'PNG', quality=100)
    print(f'Perfect circular logo QR generated: {output_path}')
    return qr_img

if __name__ == '__main__':
    url = 'https://magazines-bet-nor-barrel.trycloudflare.com'
    logo_file = r'C:\Users\Admin\.gemini\antigravity\scratch\clean-and-safe-india\assets\logo.png'
    out1 = r'C:\Users\Admin\.gemini\antigravity\scratch\clean-and-safe-india\assets\app_qr_with_logo.png'
    out2 = r'C:\Users\Admin\.gemini\antigravity\brain\a7193907-fa7b-4e78-81a1-50b728d263c2\app_qr_with_logo.png'
    create_perfect_circular_logo_qr(url, logo_file, out1)
    create_perfect_circular_logo_qr(url, logo_file, out2)
