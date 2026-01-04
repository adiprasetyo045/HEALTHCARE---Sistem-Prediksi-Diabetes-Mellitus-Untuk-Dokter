"""
Backend/models/__init__.py
Mengatur expose class dan fungsi agar mudah di-import oleh module lain.
File ini menyederhanakan proses import di routes.py.
"""

# Import komponen utama dari file-file di dalam folder models
from .decision_tree_model import DiabetesModel
from .preprocess import DiabetesPreprocessor
from .utils import validate_input_data, log_prediction

# Mendefinisikan apa yang akan di-import jika menggunakan 'from Backend.models import *'
# Ini juga menjaga agar namespace tetap bersih.
__all__ = [
    'DiabetesModel',
    'DiabetesPreprocessor',
    'validate_input_data',
    'log_prediction'
]