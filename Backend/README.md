# 🩺 HealthCare — Diabetes Prediction System

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20App-yellow)](https://aadi045-diabetes-detector.hf.space)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

**Sistem Pendukung Keputusan (DSS)** berbasis Machine Learning untuk memprediksi risiko diabetes. Dibangun menggunakan **Flask**, **Scikit-Learn**, dan **Decision Tree Algorithm** dengan optimasi kalibrasi probabilitas.

---

## 🔗 Coba Aplikasi (Live Demo)
Aplikasi ini sudah di-deploy dan dapat diakses secara langsung tanpa perlu instalasi:
👉 **[Klik Disini untuk Membuka Aplikasi](https://aadi045-diabetes-detector.hf.space)**

---

## 🚀 Fitur Utama

- **🧠 Decision Tree Classifier**: Menggunakan Entropy & `CalibratedClassifierCV` untuk probabilitas yang akurat.
- **⚖️ Data Balancing**: Implementasi **SMOTE** untuk menangani ketidakseimbangan kelas data.
- **🔄 Robust Preprocessing**: Konversi otomatis data kategori (teks) ke numerik.
- **🔌 RESTful API**: Endpoint JSON untuk integrasi Frontend/Mobile.
- **📄 PDF Report**: Generate laporan hasil diagnosa otomatis dalam format PDF.
- **📝 Prediction Logging**: Menyimpan riwayat prediksi ke CSV untuk audit trail.

## 📂 Struktur Proyek

```text
Diabetes-Detector
├── Backend/                 # Source Code Utama
│   ├── config.py            # Konfigurasi Global
│   ├── app.py               # Flask App Factory
│   ├── data/                # Dataset & Logs
│   ├── models/              # Model Logic & Pickle
│   ├── routes/              # API & Web Routes
│   ├── static/              # CSS/JS Assets & Reports
│   └── templates/           # HTML Views
├── Scripts/                 # Utilitas & Training
│   ├── check_dataset.py     # Cek Integritas Data
│   ├── balance_dataset.py   # SMOTE Balancing
│   ├── train_model.py       # Training Model
│   ├── debug_algo.py        # Debugging Manual
│   └── fix_prediction.py    # Self-Healing Tool
├── run_app.py               # Entry Point Server
├── requirements.txt         # Dependencies
└── README.md                # Dokumentasi