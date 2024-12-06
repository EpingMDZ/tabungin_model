# Menggunakan image Python sebagai base
FROM python:3.9-slim

# Menentukan direktori kerja di dalam container
WORKDIR /app

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Menginstal dependensi yang diperlukan dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua file aplikasi, termasuk model my_model.keras, ke dalam container
COPY . /app/

# Mengekspos port yang digunakan oleh aplikasi Flask
EXPOSE 8080

# Menjalankan aplikasi Flask
CMD ["python", "app.py"]
