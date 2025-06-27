from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image
import io
import os
import time
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, RoundedModuleDrawer, CircleModuleDrawer
import requests

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_img_url = None
    if request.method == 'POST':
        # Only handle normal QR code generation
        data = request.form.get('data')
        logo = request.files.get('logo')
        logo_url = request.form.get('logo_url', '').strip()
        fg_color = request.form.get('fg_color', '#000000')
        bg_color = request.form.get('bg_color', '#ffffff')
        qr_style = request.form.get('qr_style', 'square')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        # Choose module drawer based on style
        if qr_style == 'rounded':
            module_drawer = RoundedModuleDrawer()
        elif qr_style == 'circle':
            module_drawer = CircleModuleDrawer()
        else:
            module_drawer = SquareModuleDrawer()
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer,
            fill_color=fg_color,
            back_color=bg_color
        ).convert('RGB')
        logo_img = None
        if logo and logo.filename:
            logo_path = os.path.join(UPLOAD_FOLDER, logo.filename)
            logo.save(logo_path)
            logo_img = Image.open(logo_path)
        elif logo_url:
            try:
                response = requests.get(logo_url, timeout=5)
                response.raise_for_status()
                logo_img = Image.open(io.BytesIO(response.content))
            except Exception as e:
                logo_img = None
        if logo_img:
            # Resize logo
            basewidth = int(img.size[0] / 4)
            wpercent = (basewidth / float(logo_img.size[0]))
            hsize = int((float(logo_img.size[1]) * float(wpercent)))
            logo_img = logo_img.resize((basewidth, hsize), Image.LANCZOS)
            # Calculate position
            pos = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
            img.paste(logo_img, pos, mask=logo_img if logo_img.mode == 'RGBA' else None)
        # Save QR code image to static folder
        qr_filename = f'qr_{int(time.time())}.png'
        qr_path = os.path.join('static', qr_filename)
        img.save(qr_path)
        qr_img_url = '/' + qr_path.replace('\\', '/')
        return render_template('index.html', qr_img_url=qr_img_url)
    return render_template('index.html', qr_img_url=None)

if __name__ == '__main__':
    app.run(debug=True) 