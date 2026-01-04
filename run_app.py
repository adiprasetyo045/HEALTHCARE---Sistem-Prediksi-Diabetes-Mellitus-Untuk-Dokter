import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# 1. SETUP PATH
# Mengambil path root project agar folder 'Backend' dikenali sebagai package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Import Config dulu untuk mendapatkan Path yang benar
from Backend.config import Config
from Backend.routes.api_routes import api_bp
from Backend.routes.web_routes import web_bp

def create_app():
    """Factory function untuk inisialisasi aplikasi Flask."""
    
    # 2. DEFINISI APP & PATH ASET (PERBAIKAN UTAMA DISINI)
    # Gunakan Config.TEMPLATES_DIR dan Config.STATIC_DIR 
    # agar sinkron dengan pengaturan penyimpanan PDF.
    app = Flask(
        __name__,
        template_folder=Config.TEMPLATES_DIR, # Ambil dari Config
        static_folder=Config.STATIC_DIR       # Ambil dari Config
    )
    
    # Load Konfigurasi Flask
    app.config.from_object(Config)
    
    # Inisialisasi Folder (Buat folder otomatis jika belum ada)
    Config.init_app()
    
    # Mengaktifkan CORS
    CORS(app) 
    
    # 3. REGISTER BLUEPRINTS
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # 4. ERROR HANDLERS
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "error": "Endpoint API tidak ditemukan",
                "path": request.path
            }), 404
        # Return HTML sederhana atau render template 404 jika punya
        return """
        <div style="text-align:center; padding:50px;">
            <h1>404</h1>
            <p>Halaman tidak ditemukan.</p>
            <a href="/">Kembali ke Beranda</a>
        </div>
        """, 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            "success": False,
            "error": "Internal Server Error", 
            "message": str(e)
        }), 500

    return app

if __name__ == "__main__":
    app = create_app()
    
    # Konfigurasi Port
    PORT = Config.SERVER_PORT if hasattr(Config, 'SERVER_PORT') else 8000
    
    print("\n" + "="*60)
    print(f"🚀 DIABETES PREDICTION SYSTEM BERJALAN")
    print("="*60)
    print(f"📂 Root Path   : {BASE_DIR}")
    print(f"📄 Dashboard   : http://localhost:{PORT}/")
    print(f"🔌 API Info    : http://localhost:{PORT}/api/model-info")
    print("="*60 + "\n")
    
    # Jalankan Server
    app.run(host='0.0.0.0', port=PORT, debug=Config.DEBUG)