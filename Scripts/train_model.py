import sys
import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
from pathlib import Path

# =========================================
# 1. SETUP PATH SYSTEM (CRITICAL)
# =========================================
# Kita perlu menambahkan folder Root Project ke sys.path
# Agar Python mengenali folder 'Backend' sebagai module.
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Naik 2 level: Scripts -> Root
sys.path.insert(0, str(project_root))

# =========================================
# 2. IMPORT MODULE BACKEND
# =========================================
try:
    # Menggunakan Config yang baru saja diperbaiki
    from Backend.config import Config
    # Mengimport Preprocessor dari package models
    from Backend.models import DiabetesPreprocessor
except ModuleNotFoundError as e:
    print("\n❌ CRITICAL ERROR: Gagal mengimport modul 'Backend'.")
    print(f"   Detail: {e}")
    print(f"   Path saat ini: {sys.path[0]}")
    print("   Pastikan Anda menjalankan script ini dari folder Root Project.")
    sys.exit(1)

# Import Library Machine Learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, roc_auc_score, confusion_matrix,
    precision_score, recall_score, f1_score
)

def train_model():
    print("=" * 60)
    print("🧠 TRAINING MODEL DIABETES (DECISION TREE)")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # 3. Load Dataset
        # ---------------------------------------------------------
        if not os.path.exists(Config.BALANCED_DATA):
            print(f"❌ Dataset tidak ditemukan di: {Config.BALANCED_DATA}")
            print("   Mohon pastikan file 'diabetes_balanced.csv' ada di folder 'Backend/data'.")
            return False

        print(f"📂 Membaca dataset: {Config.BALANCED_DATA}")
        df = pd.read_csv(Config.BALANCED_DATA)

        # ---------------------------------------------------------
        # 4. Preprocessing
        # ---------------------------------------------------------
        preprocessor = DiabetesPreprocessor()
        
        # Cek apakah data sudah bersih/numerik
        # (Asumsi: jika kolom gender sudah angka, berarti sudah diproses sebelumnya)
        if np.issubdtype(df['gender'].dtype, np.number):
            print("ℹ️  Info: Dataset terdeteksi sudah numerik. Skip encoding.")
            df_clean = df.copy().dropna()
        else:
            print("ℹ️  Info: Dataset mentah (String). Menjalankan encoding otomatis...")
            df_clean = preprocessor.clean_and_encode(df, is_training=True)
        
        if len(df_clean) == 0:
            print("❌ ERROR: Dataset kosong setelah preprocessing!")
            return False

        # Pisahkan Fitur (X) dan Target (y)
        # Menggunakan urutan fitur dari Config agar konsisten selamanya
        X = df_clean[Config.FEATURES]
        y = df_clean['diabetic'] # Pastikan nama kolom target sesuai CSV Anda
        
        print(f"📊 Dataset Shape: {X.shape}")
        print(f"📊 Distribusi Kelas: {Counter(y)}")

        # ---------------------------------------------------------
        # 5. Membangun Pipeline Model
        # ---------------------------------------------------------
        # Base Model: Decision Tree
        dt_classifier = DecisionTreeClassifier(
            criterion="entropy",
            max_depth=6,
            min_samples_leaf=10,
            min_samples_split=20,
            class_weight="balanced",
            random_state=42
        )

        # Pipeline: Scaling -> Modeling
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('dt', dt_classifier)
        ])

        # ---------------------------------------------------------
        # 6. Kalibrasi Probabilitas (Agar output % lebih akurat)
        # ---------------------------------------------------------
        calibrated_model = CalibratedClassifierCV(
            estimator=pipeline,
            method='sigmoid',
            cv=5
        )

        # ---------------------------------------------------------
        # 7. Evaluasi Cross Validation
        # ---------------------------------------------------------
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        print("\n🔄 Menjalankan 5-Fold Cross Validation...")
        scores = cross_val_score(calibrated_model, X, y, cv=cv, scoring='accuracy')
        mean_acc = scores.mean()
        
        print(f"📈 Rata-rata Akurasi Validasi: {mean_acc:.4f} (±{scores.std():.4f})")

        # ---------------------------------------------------------
        # 8. Final Training (Full Data)
        # ---------------------------------------------------------
        print("💪 Melatih model final dengan seluruh data...")
        calibrated_model.fit(X, y)

        # Prediksi untuk metrik evaluasi
        y_pred = calibrated_model.predict(X)
        y_proba = calibrated_model.predict_proba(X)[:, 1]

        # Hitung Metrik Lengkap
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'roc_auc': roc_auc_score(y, y_proba),
            'precision': precision_score(y, y_pred, average='weighted'),
            'recall': recall_score(y, y_pred, average='weighted'),
            'f1_score': f1_score(y, y_pred, average='weighted')
        }

        cm = confusion_matrix(y, y_pred)
        tn, fp, fn, tp = cm.ravel()

        # Ekstrak Feature Importance (Dari fold pertama sebagai representasi)
        base_pipeline = calibrated_model.calibrated_classifiers_[0].estimator
        importance_vals = base_pipeline.named_steps['dt'].feature_importances_
        feature_importance = sorted(zip(Config.FEATURES, importance_vals), key=lambda x: x[1], reverse=True)

        # ---------------------------------------------------------
        # 9. Simpan Model & Metadata
        # ---------------------------------------------------------
        # Pastikan folder models ada (dibuat via Config, tapi kita cek lagi)
        os.makedirs(Config.MODELS_DIR, exist_ok=True)
        
        # Bundle objek untuk disimpan (.pkl)
        bundle = {
            'model': calibrated_model,
            'features': Config.FEATURES,
            'target_names': ['Non-Diabetic', 'Diabetic'],
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(bundle, Config.MODEL_PATH)
        print(f"\n💾 Model tersimpan: {Config.MODEL_PATH}")

        # Metadata JSON untuk keperluan Log/UI
        metadata = {
            'algorithm': 'Calibrated Decision Tree (Entropy)',
            'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'accuracy_cv': round(mean_acc, 4),
            'accuracy_train': round(metrics['accuracy'], 4),
            'metrics': {k: round(v, 4) for k, v in metrics.items()},
            'confusion_matrix': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
            'top_features': {k: round(v, 4) for k, v in feature_importance[:5]}
        }

        with open(Config.META_PATH, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"📄 Metadata tersimpan: {Config.META_PATH}")
        return True

    except Exception as e:
        print(f"\n❌ TRAINING ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Eksekusi fungsi utama
    if train_model():
        print("\n✅ PROSES SELESAI. Model siap digunakan di Web App.")
    else:
        print("\n❌ PROSES GAGAL.")
        sys.exit(1)