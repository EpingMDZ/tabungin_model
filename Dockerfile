# Gunakan image Python terbaru
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy file requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file proyek
COPY . .

# Menjalankan aplikasi dengan Flask
CMD ["python", "app.py"]
