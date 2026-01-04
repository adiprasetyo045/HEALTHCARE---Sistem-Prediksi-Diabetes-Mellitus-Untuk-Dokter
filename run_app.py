import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# --- 1. SETUP APLIKASI UTAMA ---
# Kita arahkan folder templates & static dengan path yang jelas
app = Flask(__name__, 
            template_folder='Backend/templates', 
            static_folder='Backend/static')

# Izinkan akses dari luar (agar API tidak diblokir browser)
CORS(app)

# --- 2. REGISTRASI BLUEPRINT (MENGHUBUNGKAN MENU) ---
with app.app_context():
    try:
        # A. Hubungkan Rute Halaman Web (HTML)
        # Ini akan mengambil 'web_bp' dari file web_routes.py yang Anda kirim tadi
        from Backend.routes.web_routes import web_bp
        app.register_blueprint(web_bp)
        print("✅ Web Routes (HTML) berhasil terhubung!")

        # B. Hubungkan Rute API (JSON) - PENTING UNTUK PREDIKSI
        # Kita coba import api_bp, kalau error (misal nama beda) kita handle biar server gak mati
        try:
            from Backend.routes.api_routes import api_bp
            app.register_blueprint(api_bp)
            print("✅ API Routes berhasil terhubung!")
        except ImportError:
            print("⚠️ Warning: api_routes tidak ditemukan atau nama blueprint beda. Cek kembali nanti.")
        except Exception as e:
            print(f"⚠️ Warning: Gagal load API routes: {e}")
            
    except Exception as e:
        print(f"❌ ERROR FATAL saat load routes: {e}")

# --- 3. ROUTES DARURAT (Cek apakah server hidup) ---
@app.route('/health')
def health_check():
    return jsonify({"status": "online", "message": "Server Diabetes Detector Berjalan!"})

# --- 4. JALANKAN SERVER ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)