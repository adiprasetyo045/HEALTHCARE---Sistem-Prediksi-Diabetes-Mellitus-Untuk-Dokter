/**
 * formHandler.js - VERSI FINAL HUGGING FACE 🚀
 * Menggunakan window.apiClient agar koneksi stabil & otomatis.
 */

// Variabel Global
let currentInputData = {};
let currentResultLabel = "";
let currentProbability = 0;

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. INISIALISASI ELEMEN ---
    const hInput = document.getElementById('height');
    const wInput = document.getElementById('weight');
    const bInput = document.getElementById('bmi');
    
    const btnPredict = document.getElementById('btnPredict');
    const btnPdf = document.getElementById('btnPdf'); 
    const btnReset = document.getElementById('resetBtn');
    
    const form = document.getElementById('predictionForm');
    const resContainer = document.getElementById('resultContainer');

    // --- 2. LOGIKA AUTO BMI ---
    const updateBMI = () => {
        const h = parseFloat(hInput.value); 
        const w = parseFloat(wInput.value); 
        if (h > 0 && w > 0) {
            // Rumus BMI: Berat / (Tinggi x Tinggi)
            const bmi = (w / (h * h)).toFixed(2);
            bInput.value = bmi;
        } else {
            bInput.value = '';
        }
    };

    if (hInput && wInput) {
        hInput.addEventListener('input', updateBMI);
        wInput.addEventListener('input', updateBMI);
    }

    // --- 3. LOGIKA PREDIKSI (PAKAI API CLIENT) ---
    if (btnPredict && form) {
        btnPredict.addEventListener('click', async (e) => {
            e.preventDefault(); 
            
            // Validasi Form HTML5
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            // UI Loading
            const originalText = btnPredict.innerHTML;
            btnPredict.innerHTML = '⏳ Memproses...';
            btnPredict.disabled = true;
            resContainer.style.display = 'none';

            try {
                // Ambil data form
                const formData = new FormData(form);
                const rawData = Object.fromEntries(formData.entries());
                const payload = {};
                
                // Konversi tipe data (String -> Number) agar Python tidak error
                const intFields = ['age', 'pulse_rate', 'systolic_bp', 'diastolic_bp'];
                
                for (const key in rawData) {
                    if (key === 'bmi') continue; // BMI kita ambil manual
                    
                    if (intFields.includes(key)) {
                        payload[key] = parseInt(rawData[key]) || 0;
                    } else if (['glucose', 'height', 'weight'].includes(key)) {
                        payload[key] = parseFloat(rawData[key]) || 0;
                    } else {
                        payload[key] = rawData[key]; // Biarkan string (Male/Female, Yes/No)
                    }
                }
                
                // Masukkan BMI
                payload['bmi'] = parseFloat(bInput.value) || 0;
                
                // Simpan ke global (untuk PDF nanti)
                currentInputData = payload;

                // 🔥 BAGIAN PENTING: Panggil Server via apiClient 🔥
                console.log("Mengirim data...", payload);
                
                // Kita gunakan window.apiClient yang sudah pintar
                const res = await window.apiClient.predict(payload);

                if (res.success) {
                    currentResultLabel = res.label;
                    currentProbability = res.probability_percent;
                    renderResult(res);
                } else {
                    alert("Gagal Diagnosa: " + (res.error || "Server error."));
                }

            } catch (err) {
                console.error("Prediction Error:", err);
                alert("Terjadi Kesalahan: " + err.message);
            } finally {
                btnPredict.innerHTML = originalText;
                btnPredict.disabled = false;
            }
        });
    }

    // --- 4. LOGIKA CETAK PDF (PAKAI API CLIENT) ---
    if (btnPdf) {
        btnPdf.addEventListener('click', async () => {
            const originalText = btnPdf.innerHTML;
            btnPdf.innerHTML = '⏳ Mengunduh...';
            btnPdf.disabled = true;

            try {
                // Request download link
                const data = await window.apiClient.request('/api/download-report', {
                    method: 'POST',
                    body: {
                        input_data: currentInputData,
                        label: currentResultLabel,
                        probability: currentProbability
                    }
                });

                if (data.success) {
                    // Buka link download di tab baru
                    // apiClient.baseUrl sudah berisi alamat https://huggingface... yang benar
                    const downloadUrl = window.apiClient.baseUrl + data.download_url;
                    window.open(downloadUrl, '_blank');
                } else {
                    alert("Gagal membuat PDF: " + data.error);
                }

            } catch (error) {
                console.error('PDF Error:', error);
                alert("Gagal download PDF: " + error.message);
            } finally {
                btnPdf.innerHTML = originalText;
                btnPdf.disabled = false;
            }
        });
    }

    // --- 5. RENDER HASIL (TAMPILAN) ---
    function renderResult(res) {
        resContainer.style.display = 'block';
        const isDiabetic = res.label === 'Diabetic';
        const color = isDiabetic ? '#ef4444' : '#10b981'; // Merah / Hijau
        
        // Label & Skor
        const resLabel = document.getElementById('resLabel');
        resLabel.innerText = isDiabetic ? 'TERINDIKASI DIABETES' : 'TIDAK TERINDIKASI';
        resLabel.style.color = color;
        
        document.getElementById('resRisk').innerText = res.risk_level;
        document.getElementById('resRisk').style.color = color;
        
        const probEl = document.getElementById('resProb');
        probEl.innerText = res.probability_percent + '%';
        probEl.style.color = color;

        // Info Model
        if(res.model_info) {
            document.getElementById('modName').innerText = res.model_info.name;
            document.getElementById('modAcc').innerText = res.model_info.accuracy;
        }

        // Tampilkan Ulang Input User
        const inputList = document.getElementById('inputList');
        if(inputList) {
            inputList.innerHTML = '';
            const keysShow = ['age', 'gender', 'bmi', 'glucose', 'hypertensive'];
            keysShow.forEach(k => {
                if(currentInputData[k] !== undefined) {
                    inputList.innerHTML += `
                        <li>
                            <span>${k.toUpperCase()}</span>
                            <strong>${currentInputData[k]}</strong>
                        </li>`;
                }
            });
        }

        // Grafik Faktor Penyebab (Feature Importance)
        const featList = document.getElementById('featList');
        featList.innerHTML = '';
        
        if (res.feature_importance && res.feature_importance.length > 0) {
            res.feature_importance.forEach(f => {
                featList.innerHTML += `
                    <li>
                        <span>${f.name}</span>
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:100px; height:6px; background:#334155; border-radius:3px; overflow:hidden;">
                                <div style="width:${f.value}%; height:100%; background:${color};"></div>
                            </div>
                            <strong>${f.value}%</strong>
                        </div>
                    </li>`;
            });
        } else {
            featList.innerHTML = '<li style="justify-content:center;">Data faktor tidak tersedia</li>';
        }

        // Scroll ke bawah otomatis
        resContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // --- 6. RESET FORM ---
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            form.reset();
            resContainer.style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});