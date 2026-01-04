"""
Backend/routes/api_routes.py
Menangani Logic Utama API:
1. Load Model Machine Learning
2. Endpoint Prediksi (/predict)
3. Endpoint Generate PDF (/download-report)
4. Endpoint Logs & Info
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify, current_app

from Backend.config import Config
from Backend.models.preprocess import DiabetesPreprocessor
# Menggunakan utility yang baru dibuat agar kode lebih rapi
from Backend.models.utils import create_pdf, log_prediction, validate_input_data

api_bp = Blueprint('api', __name__)

# --- 1. GLOBAL MODEL LOADING ---
# Variabel global untuk menyimpan model di memori
model = None
model_meta = {}

def load_model_resources():
    """
    Memuat model .pkl dan metadata .json saat aplikasi dijalankan.
    """
    global model, model_meta
    
    # Gunakan path absolut dari Config
    model_path = Config.MODEL_PATH
    meta_path = Config.META_PATH

    try:
        # A. Load Model Joblib
        if os.path.exists(model_path):
            loaded_data = joblib.load(model_path)
            
            # Cek apakah formatnya dictionary (bundle) atau model langsung
            if isinstance(loaded_data, dict) and 'model' in loaded_data:
                model = loaded_data['model']
            else:
                model = loaded_data
            
            print(f"✅ Model berhasil dimuat dari: {model_path}")
        else:
            print(f"❌ File model tidak ditemukan di: {model_path}")

        # B. Load Metadata JSON
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                model_meta = json.load(f)
            print("✅ Metadata berhasil dimuat.")
            
    except Exception as e:
        print(f"❌ Error fatal saat memuat resource: {e}")

# Jalankan saat file ini di-import
load_model_resources()


# --- 2. API ENDPOINTS ---

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint utama: Menerima data JSON -> Preprocessing -> Prediksi Model.
    """
    global model
    
    # Safety Check: Pastikan model ada
    if model is None:
        load_model_resources()
        if model is None:
            return jsonify({'success': False, 'error': 'Model ML belum siap/hilang.'}), 503

    try:
        # 1. Ambil Data JSON
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'Format JSON tidak valid'}), 400

        # 2. Validasi Input (Menggunakan utils.py)
        validation = validate_input_data(data)
        if not validation['is_valid']:
            return jsonify({'success': False, 'error': validation['errors']}), 400

        # 3. Preprocessing Data
        preprocessor = DiabetesPreprocessor()
        df = pd.DataFrame([data])
        
        # Bersihkan & Encode (Sama persis seperti saat training)
        df_clean = preprocessor.clean_and_encode(df, is_training=False)
        
        if df_clean.empty:
            return jsonify({'success': False, 'error': 'Data input tidak valid untuk diproses.'}), 400

        # Ambil fitur sesuai urutan training
        X = preprocessor.get_features(df_clean)

        # 4. Prediksi (Inference)
        # Hasil: 0 (Sehat) atau 1 (Diabetes)
        prediction_class = int(model.predict(X)[0])
        
        # Probabilitas: Tingkat keyakinan model (0.0 - 1.0)
        if hasattr(model, 'predict_proba'):
            probability = float(model.predict_proba(X)[0][1])
        else:
            probability = 1.0 if prediction_class == 1 else 0.0

        result_label = "Diabetic" if prediction_class == 1 else "Non-Diabetic"
        prob_percent = round(probability * 100, 2)

        # 5. Extract Feature Importance (Penjelasan Logis)
        # Karena kita pakai CalibratedClassifierCV, kita harus ambil estimator dasarnya
        top_features = []
        try:
            base_model = model
            # Jika model terkalibrasi, ambil base estimator di dalamnya
            if hasattr(model, 'calibrated_classifiers_'):
                base_model = model.calibrated_classifiers_[0].estimator
            
            # Ambil feature importance dari Decision Tree
            if hasattr(base_model, 'named_steps'):
                # Jika pakai Pipeline
                tree_model = base_model.named_steps['dt']
                importances = tree_model.feature_importances_
            else:
                importances = base_model.feature_importances_

            # Mapping nama fitur ke nilai importance
            feature_names = Config.FEATURES
            feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
            
            # Ambil 5 fitur paling berpengaruh untuk kasus ini
            top_features = [
                {'name': name, 'value': round(val * 100, 2)} 
                for name, val in feat_imp[:5] if val > 0
            ]
        except Exception as e:
            current_app.logger.warning(f"Gagal ekstrak feature importance: {e}")

        # 6. Simpan Log ke CSV (Menggunakan utils.py)
        log_prediction(data, result_label, prob_percent)

        # 7. Return Response JSON
        response = {
            'success': True,
            'label': result_label,
            'probability_percent': prob_percent,
            'risk_level': 'Tinggi' if probability >= 0.7 else ('Sedang' if probability >= 0.4 else 'Rendah'),
            'feature_importance': top_features,
            'input_data': data
        }
        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f"Prediction Error: {e}")
        return jsonify({'success': False, 'error': f"Internal Server Error: {str(e)}"}), 500


@api_bp.route('/download-report', methods=['POST'])
def download_report():
    """
    Endpoint generate PDF.
    Frontend mengirim data hasil prediksi -> Backend membuat PDF -> Return URL download.
    """
    try:
        req_data = request.get_json()
        
        input_data = req_data.get('input_data')
        result_label = req_data.get('label')
        
        # Normalisasi format probability
        prob_raw = req_data.get('probability', 0)
        if isinstance(prob_raw, str):
            prob_raw = prob_raw.replace('%', '')
        probability = float(prob_raw)

        if not input_data:
            return jsonify({'success': False, 'error': 'Data input hilang.'}), 400

        # Panggil fungsi dari utils.py
        filename = create_pdf(input_data, result_label, probability)
        
        if filename:
            # Return URL statis (misal: /static/reports/Laporan_123.pdf)
            return jsonify({
                'success': True,
                'download_url': f"/static/reports/{filename}"
            })
        else:
            return jsonify({'success': False, 'error': 'Gagal generate PDF (Cek modul fpdf).'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/logs', methods=['GET'])
def get_logs():
    """Mengambil 100 data riwayat prediksi terakhir."""
    try:
        log_path = Config.PREDICTION_LOG
        if os.path.exists(log_path):
            df = pd.read_csv(log_path)
            # Ambil 100 terakhir & balik urutan (terbaru di atas)
            logs = df.tail(100).iloc[::-1].fillna('-').to_dict(orient='records')
            return jsonify({"success": True, "logs": logs})
        return jsonify({"success": True, "logs": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Mengambil metadata performa model (Akurasi, dll)."""
    return jsonify(model_meta)