"""
Backend/routes/__init__.py
Mengatur registrasi semua Blueprint (API & Web).
File ini bertugas mengumpulkan semua rute agar rapi saat dipanggil di app utama.
"""

from flask import Flask
from .api_routes import api_bp
from .web_routes import web_bp

def register_routes(app: Flask):
    """
    Mendaftarkan semua blueprint ke aplikasi Flask utama.
    
    Args:
        app (Flask): Instance aplikasi Flask yang sedang berjalan.
    """
    
    # 1. Register Web Routes (Dashboard, History)
    # Akses: http://localhost:8000/
    # Menangani halaman HTML (Jinja2 Templates)
    app.register_blueprint(web_bp)
    
    # 2. Register API Routes (Predict, Logs, dll)
    # Akses: http://localhost:8000/api/...
    # Menangani request JSON dari JavaScript (formHandler.js)
    # PENTING: url_prefix='/api' memisahkan namespace agar rapi.
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Expose function dan blueprints agar bisa diimport manual jika perlu
__all__ = ['register_routes', 'api_bp', 'web_bp']