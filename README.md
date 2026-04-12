Here’s a **complete, professional README** you can use for your project — it walks from building the Flask API all the way to deploying on AWS and connecting a domain.

---

# 🚀 Flask API Deployment Guide (GitHub → AWS EC2 → Domain)

This project demonstrates how to build, containerize (optional), and deploy a Flask API to a cloud server using Amazon Web Services EC2, with optional domain configuration.

---

## 📌 Project Overview

A simple Flask API that exposes an endpoint:

```
GET /api/classify?name=chris
```

Example response:

```json
{
  "message": "Hello Chris, your request was processed!"
}
```

---

## 🧱 1. Project Structure

```
project/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🐍 2. Flask Application (`app.py`)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/api/classify')
def classify():
    name = request.args.get('name', 'Guest')
    return jsonify({
        "message": f"Hello {name}, your request was processed!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 📦 3. Requirements (`requirements.txt`)

```
flask
gunicorn
```

---

## 💻 4. Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python app.py
```

Test:

```
http://127.0.0.1:5000/api/classify?name=chris
```

---

## 🗂️ 5. Push Code to GitHub

1. Create repo on GitHub
2. Initialize and push:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## ☁️ 6. Deploy to AWS EC2

### 🔹 Launch Instance

- Use Ubuntu Server
- Open ports: 22, 80, 443, 5000

---

### 🔹 Connect via SSH

```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

---

### 🔹 Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx -y
```

---

### 🔹 Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

### 🔹 Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ 7. Run with Gunicorn

```bash
gunicorn -b 0.0.0.0:5000 app:app
```

---

## 🔁 8. Setup Systemd Service

```bash
sudo nano /etc/systemd/system/flaskapp.service
```

```ini
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/YOUR_REPO
ExecStart=/home/ubuntu/YOUR_REPO/venv/bin/gunicorn -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp
```

---

## 🌐 9. Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/flaskapp
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🌍 10. Domain Configuration

Buy a domain from:

- Namecheap
- GoDaddy

### 🔹 Add DNS Record

- Type: A
- Host: @
- Value: YOUR_EC2_PUBLIC_IP

Wait for DNS propagation.

---

## 🔒 11. Enable HTTPS (SSL)

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

Run:

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## ✅ 12. Test API

```
http://yourdomain.com/api/classify?name=chris
```

---

## 🚨 Troubleshooting

### ❌ Site not loading

- Check security group (port 80/5000)
- Check Nginx:

```bash
sudo systemctl status nginx
```

---

### ❌ App not running

```bash
sudo systemctl status flaskapp
```

---

### ❌ Port issues

```bash
sudo lsof -i :5000
```

---

## 🧠 Best Practices

- Use Gunicorn (not Flask dev server)
- Use Nginx as reverse proxy
- Enable HTTPS
- Use environment variables for secrets

---

## 📌 Future Improvements

- Dockerize the app
- CI/CD pipeline (GitHub Actions)
- Logging & monitoring
- Load balancing

---

## 👨‍💻 Author

Built with Flask, deployed on Amazon Web Services

---

## ⭐ If this helped you, give it a star on GitHub!

---

If you want, I can customize this README specifically for **your exact repo (with your real endpoints and structure)** or even add **Docker + CI/CD pipeline**.
