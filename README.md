# QR Code Generator

A modern, mobile-responsive QR code generator web app built with Flask and Bootstrap.

## Features
- Generate QR codes from text or URLs
- Embed a logo (upload or via URL)
- Choose QR code foreground and background colors
- Select QR code style: square, rounded, or circle
- Mobile-friendly, clean UI
- Download or screenshot your generated QR code

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```bash
   python app.py
   ```
4. **Open in your browser**
   Go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Deployment
- You can deploy this app to [Render](https://render.com/), [Heroku](https://heroku.com), or [PythonAnywhere](https://www.pythonanywhere.com/).
- For Render/Heroku, add a `Procfile` with:
  ```
  web: gunicorn app:app
  ```
- Make sure your `requirements.txt` is up to date.

## Project Structure
```
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── (QR code images, uploads)
```

## License
MIT 