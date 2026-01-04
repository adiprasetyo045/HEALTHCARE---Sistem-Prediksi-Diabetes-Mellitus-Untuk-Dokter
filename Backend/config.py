"""
Backend/config.py
Pusat konfigurasi aplikasi.
Mengatur path folder, nama file, dan definisi fitur agar konsisten di seluruh aplikasi.
"""

import os
import json

class Config:
    # =========================================
    # 1. BASE DIRECTORIES
    # =========================================
    # Mendapatkan path absolut file ini (.../Diabetes-Detector/Backend/config.py)
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Mendapatkan path Root Project (.../Diabetes-Detector)
    ROOT_DIR = os.path.dirname(BACKEND_DIR)
    
    # =========================================
    # 2. FOLDER LOCATIONS
    # =========================================
    # Folder Logika & Data (Tetap di dalam Backend)
    DATA_DIR = os.path.join(BACKEND_DIR, "data")
    MODELS_DIR = os.path.join(BACKEND_DIR, "models")
    LOGS_DIR = os.path.join(BACKEND_DIR, "logs")
    TEMPLATES_DIR = os.path.join(BACKEND_DIR, "templates")

    # [PERBAIKAN UTAMA]
    # Mengarahkan folder static ke DALAM folder Backend.
    # Sesuai screenshot Anda: Backend/static/assets/leaf.svg
    STATIC_DIR = os.path.join(BACKEND_DIR, "static")
    
    # Folder Laporan PDF (di dalam static agar bisa diakses browser)
    REPORTS_DIR = os.path.join(STATIC_DIR, "reports")

    # =========================================
    # 3. FILE PATHS
    # =========================================
    # Dataset
    RAW_DATA = os.path.join(DATA_DIR, "diabetes.csv")
    BALANCED_DATA = os.path.join(DATA_DIR, "diabetes_balanced.csv")
    
    # Logs
    PREDICTION_LOG = os.path.join(LOGS_DIR, "prediction_logs.csv")
    
    # Model & Metadata
    MODEL_PATH = os.path.join(MODELS_DIR, "decision_tree_bundle.pkl")
    META_PATH = os.path.join(MODELS_DIR, "decision_tree_meta.json")
    
    # Laporan Teknis (Opsional)
    DATA_REPORT = os.path.join(DATA_DIR, "dataset_report.txt")

    # =========================================
    # 4. DATA DEFINITIONS (Single Source of Truth)
    # =========================================
    # Urutan fitur WAJIB sama persis dengan urutan kolom saat training model
    FEATURES = [
        'age', 'gender', 'pulse_rate', 'systolic_bp', 'diastolic_bp',
        'glucose', 'height', 'weight', 'bmi', 'family_diabetes',
        'hypertensive', 'family_hypertension', 'cardiovascular_disease', 'stroke'
    ]

    # Deskripsi untuk UI (Label Form) / Laporan PDF
    FEATURE_DESCRIPTIONS = {
        'age': 'Usia (Tahun)',
        'gender': 'Jenis Kelamin',
        'pulse_rate': 'Nadi (bpm)',
        'systolic_bp': 'Tekanan Darah Sistolik',
        'diastolic_bp': 'Tekanan Darah Diastolik',
        'glucose': 'Gula Darah (mmol/L)',
        'height': 'Tinggi (m)',
        'weight': 'Berat (kg)',
        'bmi': 'Indeks Massa Tubuh',
        'family_diabetes': 'Riwayat Diabetes Keluarga',
        'hypertensive': 'Status Hipertensi',
        'family_hypertension': 'Riwayat Hipertensi Keluarga',
        'cardiovascular_disease': 'Penyakit Jantung',
        'stroke': 'Riwayat Stroke'
    }

    # =========================================
    # 5. SERVER CONFIG
    # =========================================
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    DEBUG = True
    SECRET_KEY = "kunci_rahasia_bisa_diganti_nanti"

    # =========================================
    # 6. AUTO-INIT UTILITY
    # =========================================
    @classmethod
    def init_app(cls):
        """Membuat struktur folder otomatis jika belum ada."""
        required_folders = [
            cls.DATA_DIR, 
            cls.MODELS_DIR, 
            cls.LOGS_DIR, 
            cls.STATIC_DIR,
            cls.REPORTS_DIR
        ]
        
        # Cek dan buat folder secara diam-diam (silent check)
        for folder in required_folders:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    pass # Ignore error during import time

# Jalankan init saat modul di-import agar struktur folder terjamin ada
Config.init_app()

# =========================================
# UTILITY CHECKER (Hanya jalan jika file ini dijalankan langsung)
# =========================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏥 DIABETES SYSTEM CONFIGURATION CHECK")
    print("="*60)
    print(f"📂 Root Project   : {Config.ROOT_DIR}")
    print(f"📂 Backend Logic  : {Config.BACKEND_DIR}")
    print(f"📂 Static/Assets  : {Config.STATIC_DIR}")
    print("-" * 60)
    
    # Cek ketersediaan file penting
    files_to_check = {
        "Dataset CSV": Config.RAW_DATA,
        "Dataset Balanced": Config.BALANCED_DATA,
        "Model PKL": Config.MODEL_PATH,
        "Metadata JSON": Config.META_PATH
    }
    
    print("📄 STATUS FILE PENTING:")
    all_ready = True
    for name, path in files_to_check.items():
        exists = os.path.exists(path)
        icon = "✅" if exists else "❌"
        status_text = "ADA" if exists else "TIDAK ADA"
        print(f"   {icon} {name:<20} : {status_text}")
        if not exists: 
            all_ready = False

    print("-" * 60)
    if all_ready:
        print("🚀 KONFIGURASI AMAN. Semua file pendukung ditemukan.")
        print("   Anda bisa menjalankan 'python run_app.py' sekarang.")
    else:
        print("⚠️  PERINGATAN: Beberapa file belum ada.")
        print("   1. Pastikan dataset sudah ditaruh di folder 'Backend/data'.")
        print("   2. Jalankan 'python -m Scripts.train_model' untuk membuat model.")
    print("="*60 + "\n")