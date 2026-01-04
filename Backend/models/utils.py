"""
Backend/models/utils.py
Berisi fungsi bantuan untuk:
1. Validasi Input API
2. Logging ke CSV (Audit Trail)
3. Generate Laporan PDF (Resep/Hasil)
"""

import os
import csv
import datetime
from typing import Dict, Any, List

# Import Config untuk Path dan Definisi Fitur
from Backend.config import Config

# Coba import FPDF, jika belum install beri peringatan tapi jangan crash
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False
    print("⚠️ Warning: Modul 'fpdf' belum terinstall. Fitur PDF tidak akan berjalan.")
    print("   Install dengan: pip install fpdf")

# --- 1. FUNGSI VALIDASI ---
def validate_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Memastikan data input memiliki semua fitur yang dibutuhkan model.
    Menggunakan Config.FEATURES sebagai acuan.
    """
    missing = []
    empty = []
    
    for feature in Config.FEATURES:
        if feature not in data:
            missing.append(feature)
        else:
            val = data[feature]
            if val is None or (isinstance(val, str) and str(val).strip() == ""):
                empty.append(feature)

    errors = []
    if missing:
        errors.append(f"Data hilang: {', '.join(missing)}")
    if empty:
        errors.append(f"Data kosong: {', '.join(empty)}")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

# --- 2. FUNGSI LOGGING CSV ---
def log_prediction(input_data: Dict[str, Any], prediction: str, probability: float) -> None:
    """
    Menyimpan riwayat prediksi ke CSV untuk audit.
    """
    try:
        # Pastikan folder logs ada (menggunakan Config)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        log_path = Config.PREDICTION_LOG
        
        # Cek apakah file sudah ada (untuk menentukan perlu tulis header atau tidak)
        file_exists = os.path.exists(log_path)

        # Siapkan data baris
        row_data = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prediction': prediction,
            'probability': f"{probability:.2f}%"
        }
        # Gabungkan data input user ke row_data
        for feature in Config.FEATURES:
            row_data[feature] = input_data.get(feature, "")

        # Tentukan urutan kolom (Header)
        fieldnames = ['timestamp', 'prediction', 'probability'] + Config.FEATURES

        with open(log_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader() # Tulis header jika file baru
            
            writer.writerow(row_data)
            
    except Exception as e:
        print(f"⚠️ Gagal menulis log prediksi: {e}")

# --- 3. CLASS PDF REPORT ---
if HAS_FPDF:
    class PDFReport(FPDF):
        def header(self):
            # Judul
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Laporan Hasil Deteksi Diabetes', 0, 1, 'C')
            
            # Sub-judul
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, 'Sistem Pakar Berbasis Machine Learning (Decision Tree)', 0, 1, 'C')
            
            # Garis pembatas
            self.line(10, 30, 200, 30)
            self.ln(10)

        def footer(self):
            # Posisi 1.5 cm dari bawah
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

# --- 4. FUNGSI GENERATOR PDF ---
def create_pdf(data: Dict[str, Any], result_label: str, probability: float) -> str:
    """
    Membuat file PDF hasil diagnosa.
    Return: Nama file (filename) jika berhasil, None jika gagal.
    """
    if not HAS_FPDF:
        return None

    try:
        pdf = PDFReport()
        pdf.add_page()
        
        # A. INFORMASI WAKTU
        pdf.set_font("Arial", size=11)
        tanggal = datetime.datetime.now().strftime("%d-%m-%Y %H:%M WIB")
        pdf.cell(0, 10, f"Waktu Pemeriksaan: {tanggal}", ln=True)
        pdf.ln(5)

        # B. HASIL DIAGNOSA (Highlight)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "HASIL ANALISIS:", ln=True)
        
        # Logika Warna (Merah = Bahaya, Hijau = Aman)
        if result_label.lower() == "diabetic":
            pdf.set_text_color(220, 53, 69) # Merah Bootstrap
        else:
            pdf.set_text_color(40, 167, 69) # Hijau Bootstrap
            
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 15, f"{result_label.upper()}", ln=True)
        
        # Reset Warna ke Hitam
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Tingkat Keyakinan Model: {probability:.2f}%", ln=True)
        pdf.ln(10)

        # C. TABEL RINCIAN DATA
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Rincian Data Pasien:", ln=True)
        pdf.set_font("Arial", size=11)

        # Mapping Key (Teknis) -> Label (Bahasa Indonesia)
        # KUNCI (Keys) harus sama persis dengan Config.FEATURES
        label_map = {
            'age': 'Usia (Tahun)',
            'gender': 'Jenis Kelamin',
            'pulse_rate': 'Detak Jantung (bpm)',
            'systolic_bp': 'Tekanan Darah (Sistolik)',
            'diastolic_bp': 'Tekanan Darah (Diastolik)',
            'glucose': 'Gula Darah (mg/dL)',
            'height': 'Tinggi Badan (cm)',
            'weight': 'Berat Badan (kg)',
            'bmi': 'BMI (Indeks Massa Tubuh)',
            'family_diabetes': 'Riwayat Diabetes Keluarga',
            'hypertensive': 'Status Hipertensi',
            'family_hypertension': 'Riwayat Hipertensi Keluarga',
            'cardiovascular_disease': 'Penyakit Jantung',
            'stroke': 'Riwayat Stroke'
        }

        # Konfigurasi Tabel
        col_label_w = 80
        col_value_w = 60
        row_h = 8

        # Loop berdasarkan urutan Config.FEATURES agar rapi
        for key in Config.FEATURES:
            if key not in data: continue

            # Ambil label bahasa Indonesia, fallback ke key asli jika tidak ada di map
            label_indo = label_map.get(key, key)
            raw_val = data[key]
            
            # Formatting Nilai agar enak dibaca
            display_val = str(raw_val)
            
            # Khusus Gender
            if key == 'gender':
                if str(raw_val).lower() in ['male', '1', 'laki-laki']:
                    display_val = "Laki-laki"
                else:
                    display_val = "Perempuan"
            # Khusus Nilai Boolean (0/1)
            elif str(raw_val) in ['0', '1']:
                 display_val = "Ya" if str(raw_val) == '1' else "Tidak"
            
            pdf.cell(col_label_w, row_h, label_indo, border=1)
            pdf.cell(col_value_w, row_h, display_val, border=1, ln=True)

        # D. SIMPAN FILE
        # Gunakan Config.REPORTS_DIR yang sudah pasti benar path-nya
        filename = f"Hasil_Diagnosa_{int(datetime.datetime.now().timestamp())}.pdf"
        full_path = os.path.join(Config.REPORTS_DIR, filename)
        
        pdf.output(full_path)
        print(f"✅ PDF Created: {full_path}")
        
        return filename

    except Exception as e:
        print(f"❌ Error membuat PDF: {e}")
        import traceback
        traceback.print_exc()
        return None