from flask import Flask, render_template, request, send_from_directory, url_for, jsonify, send_file
import qrcode
from io import BytesIO
import base64
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_img_bytes(data):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def generate_qr_img(data):
    buf = generate_qr_img_bytes(data)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

def is_upi_id(text):
    upi_pattern = r'^[\w.-]+@[\w.-]+$'
    forbidden = [
        '@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com', '@protonmail.com',
        '.com', '.net', '.org', '.edu', '.gov', '.co.in', '.ac.in', '.io', '.me', '.info', '.biz', '.xyz', '.co'
    ]
    text = text.strip().lower()
    if not re.match(upi_pattern, text):
        return False
    for f in forbidden:
        if text.endswith(f):
            return False
    return True

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/qrcode', methods=['POST'])
def api_qrcode():
    data = request.json.get('data', '').strip()
    upi_name = request.json.get('upi_name', '').strip()
    amount = request.json.get('amount', '').strip()
    response_type = request.args.get('type', 'base64')  # 'base64' or 'png'
    # UPI QR
    if is_upi_id(data):
        upi_url = f"upi://pay?pa={data}"
        if upi_name:
            upi_url += f"&pn={upi_name}"
        if amount:
            upi_url += f"&am={amount}"
        upi_url += "&cu=INR"
        qr_buf = generate_qr_img_bytes(upi_url)
    else:
        qr_buf = generate_qr_img_bytes(data)
    if response_type == 'png':
        return send_file(qr_buf, mimetype='image/png')
    else:
        img_base64 = base64.b64encode(qr_buf.getvalue()).decode('utf-8')
        return jsonify({"qr_image": f"data:image/png;base64,{img_base64}"})

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_img = None
    input_data = ''
    upi_name = ''
    amount = ''
    if request.method == 'POST':
        input_data = request.form.get('data', '').strip()
        upi_name = request.form.get('upi_name', '').strip()
        amount = request.form.get('amount', '').strip()
        file = request.files.get('image_file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img_url = url_for('uploaded_file', filename=filename, _external=True)
            qr_img = generate_qr_img(img_url)
        elif is_upi_id(input_data):
            upi_url = f"upi://pay?pa={input_data}"
            if upi_name:
                upi_url += f"&pn={upi_name}"
            if amount:
                upi_url += f"&am={amount}"
            upi_url += "&cu=INR"
            qr_img = generate_qr_img(upi_url)
        else:
            qr_img = generate_qr_img(input_data)
    else:
        qr_img = generate_qr_img('')
    return render_template('index.html', qr_img=qr_img, input_data=input_data, upi_name=upi_name, amount=amount)

if __name__ == '__main__':
    app.run(debug=True) 