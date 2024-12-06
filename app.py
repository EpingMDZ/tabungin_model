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
# Fungsi untuk menyimpan data ke Firestore
def save_to_firestore(income, total_expenses, dependents, prediction, savings_recommendation):
    doc_ref = db.collection('predictions').add({
        'income': float(income),  # Convert to float
        'total_expenses': float(total_expenses),  # Convert to float
        'dependents': int(dependents),  # Convert to int
        'prediction': float(prediction),  # Convert to float
        'savings_recommendation': float(savings_recommendation),  # Convert to float
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    print("Data berhasil disimpan ke Firestore:", doc_ref)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Mengambil data dari request JSON
        data = request.get_json()

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

        # Hitung sisa pendapatan dan rekomendasi tabungan
        total_expenses = sum(features[3:])
        remaining_income = features[0] - total_expenses
        savings_recommendation = remaining_income * 0.2

        # Simpan ke Firestore
        save_to_firestore(
            income=features[0],
            total_expenses=total_expenses,
            dependents=features[2],
            prediction=prediction,
            savings_recommendation=savings_recommendation
        )

        # Kembalikan hasil ke pengguna
        return jsonify({
            'Hasil_Prediksi_Model': float(prediction),
            'Pendapatan_Bulanan': features[0],
            'Total_Pengeluaran_Bulanan': total_expenses,
            'Sisa_Pendapatan_After_Expenses': remaining_income,
            'Saran_Tabungan_Bulanan': savings_recommendation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
