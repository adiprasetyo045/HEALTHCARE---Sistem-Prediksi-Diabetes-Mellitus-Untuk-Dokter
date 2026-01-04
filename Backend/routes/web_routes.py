"""
Backend/routes/web_routes.py
Menangani Routing Halaman Web (HTML Render).
File ini bertugas mengembalikan file HTML dari folder templates kepada pengguna.
"""

from flask import Blueprint, render_template
from jinja2 import TemplateNotFound

# Definisi Blueprint 'web'
web_bp = Blueprint('web', __name__)

# --- RUTE 1: LANDING PAGE (HOME) ---
@web_bp.route('/')
def index():
    """
    Halaman Utama (Dashboard).
    URL: http://localhost:8000/
    """
    try:
        # active_page='home' digunakan untuk menandai menu navigasi yang aktif
        return render_template('pages/index.html', active_page='home')
    except TemplateNotFound:
        return "❌ Error: File 'Backend/templates/pages/index.html' tidak ditemukan.", 404

# --- RUTE 2: TENTANG (ABOUT) ---
@web_bp.route('/about')
def about():
    """
    Halaman Dokumentasi Metodologi & Dataset.
    URL: http://localhost:8000/about
    """
    try:
        return render_template('pages/about.html', active_page='about')
    except TemplateNotFound:
        return "❌ Error: File 'Backend/templates/pages/about.html' tidak ditemukan.", 404

# --- RUTE 3: FORM DIAGNOSIS (PREDIKSI) ---
@web_bp.route('/predict')
def predict():
    """
    Halaman Formulir Input Klinis.
    URL: http://localhost:8000/predict
    """
    try:
        return render_template('pages/form.html', active_page='predict')
    except TemplateNotFound:
        return "❌ Error: File 'Backend/templates/pages/form.html' tidak ditemukan.", 404

# --- RUTE 4: RIWAYAT LENGKAP ---
@web_bp.route('/history')
def history():
    """
    Halaman Log Riwayat Lengkap.
    URL: http://localhost:8000/history
    """
    try:
        # Pastikan Anda sudah membuat file logs.html di folder pages
        return render_template('pages/logs.html', active_page='history')
    except TemplateNotFound:
        return "❌ Error: File 'Backend/templates/pages/logs.html' tidak ditemukan.", 404