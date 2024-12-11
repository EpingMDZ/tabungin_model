# Menggunakan base image Python 3.9-slim
FROM python:3.9-slim

# Mengatur working directory di dalam container
WORKDIR /app

# Menyalin requirements.txt dan menginstall dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua file dari direktori lokal ke dalam container
COPY . .

# Mengekspose port 8080 untuk berkomunikasi dengan aplikasi
EXPOSE 8080

# Menjalankan aplikasi Flask
CMD ["python", "app.py"]
