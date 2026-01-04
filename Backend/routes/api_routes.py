"""
Backend/routes/api_routes.py
Menangani Logic Utama API:
1. Load Model Machine Learning
2. Endpoint Prediksi (/predict) -> Otomatis jadi /api/predict
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
# Menggunakan utility agar kode lebih rapi
from Backend.models.utils import create_pdf, log_prediction, validate_input_data

# --- 🔥 PERBAIKAN PENTING DI SINI 🔥 ---
# url_prefix='/api' wajib ada agar alamatnya menjadi:
# /api/predict, /api/logs, dll. (Sesuai dengan apiClient.js)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- 1. GLOBAL MODEL LOADING ---
model = None
model_meta = {}

def load_model_resources():
    """Memuat model .pkl dan metadata .json saat aplikasi dijalankan."""
    global model, model_meta
    
    model_path = Config.MODEL_PATH
    meta_path = Config.META_PATH

    try:
        # A. Load Model Joblib
        if os.path.exists(model_path):
            loaded_data = joblib.load(model_path)
            
            # Cek format dictionary atau model langsung
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

# Jalankan saat import
load_model_resources()


# --- 2. API ENDPOINTS ---

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint utama: /api/predict
    """
    global model
    
    if model is None:
        load_model_resources()
        if model is None:
            return jsonify({'success': False, 'error': 'Model ML belum siap.'}), 503

    try:
        # 1. Ambil Data JSON
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'Format JSON tidak valid'}), 400

        # 2. Validasi Input
        validation = validate_input_data(data)
        if not validation['is_valid']:
            return jsonify({'success': False, 'error': validation['errors']}), 400

        # 3. Preprocessing Data
        preprocessor = DiabetesPreprocessor()
        df = pd.DataFrame([data])
        
        # Bersihkan & Encode
        df_clean = preprocessor.clean_and_encode(df, is_training=False)
        
        if df_clean.empty:
            return jsonify({'success': False, 'error': 'Data input tidak valid.'}), 400

        X = preprocessor.get_features(df_clean)

        # 4. Prediksi
        prediction_class = int(model.predict(X)[0])
        
        if hasattr(model, 'predict_proba'):
            probability = float(model.predict_proba(X)[0][1])
        else:
            probability = 1.0 if prediction_class == 1 else 0.0

        result_label = "Diabetic" if prediction_class == 1 else "Non-Diabetic"
        prob_percent = round(probability * 100, 2)

        # 5. Extract Feature Importance
        top_features = []
        try:
            # Logika ambil feature importance
            base_model = model
            if hasattr(model, 'calibrated_classifiers_'):
                base_model = model.calibrated_classifiers_[0].estimator
            
            if hasattr(base_model, 'named_steps'):
                tree_model = base_model.named_steps['dt']
                importances = tree_model.feature_importances_
            elif hasattr(base_model, 'feature_importances_'):
                importances = base_model.feature_importances_
            else:
                importances = []

            if len(importances) > 0:
                feature_names = Config.FEATURES
                feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
                top_features = [
                    {'name': name, 'value': round(val * 100, 2)} 
                    for name, val in feat_imp[:5] if val > 0
                ]
        except Exception as e:
            current_app.logger.warning(f"Gagal ekstrak feature importance: {e}")

        # 6. Simpan Log
        log_prediction(data, result_label, prob_percent)

        # 7. Return Response
        return jsonify({
            'success': True,
            'label': result_label,
            'probability_percent': prob_percent,
            'risk_level': 'Tinggi' if probability >= 0.7 else ('Sedang' if probability >= 0.4 else 'Rendah'),
            'feature_importance': top_features,
            'input_data': data
        })

    except Exception as e:
        current_app.logger.error(f"Prediction Error: {e}")
        return jsonify({'success': False, 'error': f"Internal Server Error: {str(e)}"}), 500


@api_bp.route('/download-report', methods=['POST'])
def download_report():
    """Endpoint generate PDF: /api/download-report"""
    try:
        req_data = request.get_json()
        input_data = req_data.get('input_data')
        result_label = req_data.get('label')
        
        prob_raw = req_data.get('probability', 0)
        if isinstance(prob_raw, str):
            prob_raw = prob_raw.replace('%', '')
        probability = float(prob_raw)

        if not input_data:
            return jsonify({'success': False, 'error': 'Data input hilang.'}), 400

        filename = create_pdf(input_data, result_label, probability)
        
        if filename:
            # Return URL statis
            # Hugging Face otomatis melayani folder static/
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
    """Endpoint Logs: /api/logs"""
    try:
        log_path = Config.PREDICTION_LOG
        if os.path.exists(log_path):
            df = pd.read_csv(log_path)
            logs = df.tail(100).iloc[::-1].fillna('-').to_dict(orient='records')
            return jsonify({"success": True, "logs": logs})
        return jsonify({"success": True, "logs": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Endpoint Info: /api/model-info"""
    return jsonify(model_meta)