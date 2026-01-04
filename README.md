---
title: Diabetes Detector
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🩺 HealthCare — Sistem Prediksi Diabetes Mellitus

[![Hugging Face Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20App-yellow)](https://aadi045-diabetes-detector.hf.space)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-black)](https://flask.palletsprojects.com/)

**Sistem Pendukung Keputusan (DSS)** berbasis Machine Learning untuk membantu dokter dalam memprediksi risiko diabetes pasien. Proyek ini menggunakan algoritma **Decision Tree** yang telah dikalibrasi untuk menghasilkan probabilitas yang akurat.

---

## 🚀 COBA APLIKASI (LIVE DEMO)

Aplikasi ini sudah di-deploy dan dapat diakses secara online tanpa perlu instalasi.

### 👉 [KLIK DI SINI UNTUK MEMBUKA APLIKASI](https://aadi045-diabetes-detector.hf.space) 👈

*(Note: Jika aplikasi loadingnya agak lama (1-2 menit), harap bersabar karena menggunakan server gratis yang sedang "bangun tidur".)*

---

## 🌟 Fitur Utama

1.  **Diagnosa Cepat:** Input parameter klinis (Glukosa, BMI, Tensi, dll) dan dapatkan hasil instan.
2.  **Akurasi Tinggi:** Menggunakan model Decision Tree dengan akurasi uji ~99% (pada dataset DiaBD).
3.  **Laporan PDF:** Generate hasil diagnosa otomatis menjadi file PDF yang siap cetak.
4.  **Audit Trail:** Setiap prediksi tersimpan otomatis dalam log sistem (CSV).

## 🛠️ Cara Menjalankan di Lokal (Laptop)

Jika Anda ingin mencoba kodingannya di laptop sendiri:

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/adiprasetyo045/HEALTHCARE---Sistem-Prediksi-Diabetes-Mellitus-Untuk-Dokter.git](https://github.com/adiprasetyo045/HEALTHCARE---Sistem-Prediksi-Diabetes-Mellitus-Untuk-Dokter.git)
    ```
2.  **Install Library**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Jalankan Server**
    ```bash
    python run_app.py
    ```

---
> Dibuat oleh **Adi Prasetyo** | Mahasiswa IT Semester 5