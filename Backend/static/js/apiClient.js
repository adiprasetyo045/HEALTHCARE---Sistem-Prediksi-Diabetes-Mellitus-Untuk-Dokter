class DiabetesApiClient {
    constructor(baseUrl = '') {
        // --- HUGGING FACE FIX ---
        // Otomatis deteksi URL. Ini akan mengikuti domain Hugging Face (https://...)
        // Tidak lagi memaksa localhost:8000
        this.baseUrl = baseUrl || window.location.origin;
        this.isConnected = false;
        
        console.log('🌐 Diabetes API Client initialized');
        console.log('   Target URL:', this.baseUrl);
    }

    /**
     * Core Request Handler (Wrapper untuk fetch)
     */
    async request(endpoint, options = {}) {
        // Pastikan endpoint diawali dengan '/'
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
        const url = this.baseUrl + cleanEndpoint;
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        if (finalOptions.body && typeof finalOptions.body === 'object') {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            console.log(`📡 Sending [${finalOptions.method}] to ${url}`);
            const response = await fetch(url, finalOptions);
            const contentType = response.headers.get("content-type");
            
            // Handle jika server error dan tidak mengembalikan JSON (misal 500 HTML error)
            if (!contentType || !contentType.includes("application/json")) {
                // Jika statusnya OK tapi bukan JSON, mungkin halaman HTML biasa
                if (response.ok) {
                    console.warn("⚠️ Received non-JSON response but status is OK");
                    return { status: "ok", message: "Non-JSON response received" };
                }
                throw new Error(`Server Error: Received non-JSON response (${response.status})`);
            }

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = data.error || data.message || `HTTP Error ${response.status}`;
                throw new Error(errorMessage);
            }

            this.isConnected = true;
            return data;

        } catch (error) {
            console.error(`❌ API Error [${finalOptions.method}] ${endpoint}:`, error.message);
            this.isConnected = false;
            throw error;
        }
    }

    /**
     * CEK KONEKSI (Health Check)
     * UPDATE: Menggunakan endpoint /health yang sudah dibuat di run_app.py
     * Ini jauh lebih stabil daripada /api/model-info
     */
    async checkConnection() {
        return this.request('/health');
    }

    /**
     * PREDIKSI (Endpoint Utama)
     */
    async predict(payload) {
        if (!payload || typeof payload !== 'object') {
            throw new Error("Data input tidak valid.");
        }
        
        return this.request('/api/predict', {
            method: 'POST',
            body: payload
        });
    }

    /**
     * GET LOGS/HISTORY
     */
    async getLogs() {
        return this.request('/api/logs');
    }

    /**
     * GET MODEL INFO
     */
    async getModelInfo() {
        return this.request('/api/model-info');
    }
}

// Global Export
const api = new DiabetesApiClient();
window.apiClient = api;

// Auto-check connection saat file dimuat
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log("🔄 Checking API connection...");
        const status = await api.checkConnection();
        console.log('✅ API Connected:', status);
        document.dispatchEvent(new CustomEvent('api-connected'));
    } catch (e) {
        console.warn('⚠️ Gagal cek koneksi awal (tapi mungkin prediksi tetap bisa jalan).', e);
        // Jangan alert error dulu agar user tidak panik saat pertama buka
    }
});