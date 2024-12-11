import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from google.cloud import firestore

# Inisialisasi Flask dan Firestore
app = Flask(__name__)
db = firestore.Client()

# Muat model yang sudah dilatih
model = tf.keras.models.load_model('my_model.keras')

# Fungsi untuk menyimpan data ke Firestore
def save_to_firestore(income, total_expenses, dependents, prediction, savings_recommendation, status):
    try:
        doc_ref = db.collection('predictions').add({
            'income': float(income),
            'total_expenses': float(total_expenses),
            'dependents': int(dependents),
            'prediction': float(prediction),
            'savings_recommendation': float(savings_recommendation),
            'status': status,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print("Data berhasil disimpan ke Firestore:", doc_ref)
    except Exception as e:
        print(f"Error saat menyimpan data ke Firestore: {str(e)}")

# Fungsi untuk memvalidasi input dari pengguna
def validate_input(data):
    required_fields = [
        'Pendapatan_Bulanan', 'Umur', 'Jumlah_Tanggungan', 'Sewa_Bulanan', 'Pembayaran_Pinjaman_Bulanan', 
        'Biaya_Asuransi_Bulanan', 'Biaya_Bahan_Makanan_Bulanan', 'Biaya_Transportasi_Bulanan', 
        'Biaya_Makan_Di_Luar_Bulanan', 'Biaya_Hiburan_Bulanan', 'Biaya_Utilitas_Bulanan', 
        'Biaya_Perawatan_Kesehatan_Bulanan', 'Biaya_Pendidikan_Bulanan', 'Biaya_Lain_Lain_Bulanan'
    ]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Field {field} tidak ditemukan dalam input")

    return True

@app.route('/')
def home():
    return "Cloud Run is working!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()

        # Validasi input
        validate_input(data)

        # Mendapatkan data input dengan pemeriksaan None dan memberikan nilai default 0 jika None
        features = [
            data.get('Pendapatan_Bulanan', 0),
            data.get('Umur', 0),
            data.get('Jumlah_Tanggungan', 0),
            data.get('Sewa_Bulanan', 0),
            data.get('Pembayaran_Pinjaman_Bulanan', 0),
            data.get('Biaya_Asuransi_Bulanan', 0),
            data.get('Biaya_Bahan_Makanan_Bulanan', 0),
            data.get('Biaya_Transportasi_Bulanan', 0),
            data.get('Biaya_Makan_Di_Luar_Bulanan', 0),
            data.get('Biaya_Hiburan_Bulanan', 0),
            data.get('Biaya_Utilitas_Bulanan', 0),
            data.get('Biaya_Perawatan_Kesehatan_Bulanan', 0),
            data.get('Biaya_Pendidikan_Bulanan', 0),
            data.get('Biaya_Lain_Lain_Bulanan', 0)
        ]

        # Konversi ke array NumPy
        input_data = np.array([features], dtype=np.float32)

        # Prediksi menggunakan model
        prediction = model.predict(input_data)[0][0]

        # Hitung total pengeluaran dan sisa pendapatan
        total_expenses = sum(features[3:])
        remaining_income = features[0] - total_expenses

        # Saran tabungan (20% dari sisa pendapatan jika memungkinkan)
        savings_recommendation = max(remaining_income * 0.2, 0) if remaining_income > 0 else 0

        # Tentukan status keuangan berdasarkan prediksi
        status = "On Track" if prediction >= 0.5 else "Needs Attention"

        # Alert untuk pengguna berdasarkan status keuangan
        alert_message = ""
        if status == "On Track":
            alert_message = "✅ Anda berada di jalur yang tepat dengan tujuan tabungan Anda. Pertahankan!"
        else:
            alert_message = (
                "⚠️ Anda perlu menabung lebih banyak untuk mencapai target tabungan Anda. "
                "Pertimbangkan untuk mengurangi pengeluaran dalam kategori seperti hiburan, makan di luar, atau lain-lain untuk meningkatkan tabungan Anda."
            )

        # Simpan ke Firestore
        save_to_firestore(
            income=features[0],
            total_expenses=total_expenses,
            dependents=features[2],
            prediction=prediction,
            savings_recommendation=savings_recommendation,
            status=status
        )

        # Kembalikan hasil ke pengguna dengan format yang diinginkan
        return jsonify({
            'Detail_Keuangan_Anda': {
                'Total_Pendapatan_Bulanan': f"IDR {features[0]:,.2f}",
                'Total_Pengeluaran_Bulanan': f"IDR {total_expenses:,.2f}",
                'Sisa_Pendapatan_Setelah_Pengeluaran': f"IDR {remaining_income:,.2f}"
            },
            'Alert': alert_message,
            'Rekomendasi_Tabungan_Bulanan_Anda': f"IDR {savings_recommendation:,.2f}",
            'Status_Keuangan': status
        })

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
