/**
 * formHandler.js - Final Synchronized Version
 * Cocok dengan ID di form.html (btnPdf, predictionForm, dll)
 */

// Variabel Global Data
let currentInputData = {};
let currentResultLabel = "";
let currentProbability = 0;

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. INISIALISASI ELEMEN (SESUAI ID DI HTML) ---
    const hInput = document.getElementById('height');
    const wInput = document.getElementById('weight');
    const bInput = document.getElementById('bmi');
    
    // ID tombol sesuai HTML Anda
    const btnPredict = document.getElementById('btnPredict');
    const btnPdf = document.getElementById('btnPdf'); // SUDAH DIPERBAIKI (sebelumnya btnCetak)
    const btnReset = document.getElementById('resetBtn');
    
    const form = document.getElementById('predictionForm');
    const resContainer = document.getElementById('resultContainer');

    // --- 2. LOGIKA AUTO BMI ---
    const updateBMI = () => {
        const h = parseFloat(hInput.value); // cm? atau m?
        const w = parseFloat(wInput.value); // kg
        
        // Cek placeholder di HTML: Height (m). Jadi inputnya Meter.
        // Tapi logic JS sebelumnya convert cm ke m. 
        // Kita ikuti standar HTML Anda (input dalam Meter)
        if (h > 0 && w > 0) {
            // Jika input user 1.70 (meter)
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

    // --- 3. LOGIKA PREDIKSI ---
    if (btnPredict && form) {
        btnPredict.addEventListener('click', async (e) => {
            e.preventDefault(); 

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
                const formData = new FormData(form);
                const rawData = Object.fromEntries(formData.entries());
                const payload = {};

                // Konversi Data
                const intFields = ['age', 'pulse_rate', 'systolic_bp', 'diastolic_bp'];
                // Dropdown value di HTML Anda adalah "Male"/"Female", "Yes"/"No".
                // Backend Python butuh konversi atau bisa baca string?
                // Asumsi: Backend Python sudah punya Preprocessor yang handle string "Male"/"Yes".
                
                for (const key in rawData) {
                    if (key === 'bmi') continue;
                    
                    if (intFields.includes(key)) {
                        payload[key] = parseInt(rawData[key]) || 0;
                    } else if (['glucose', 'height', 'weight'].includes(key)) {
                        payload[key] = parseFloat(rawData[key]) || 0;
                    } else {
                        // Kirim string apa adanya (Male/Female, Yes/No)
                        payload[key] = rawData[key];
                    }
                }
                
                payload['bmi'] = parseFloat(bInput.value) || 0;
                currentInputData = payload;

                // Kirim ke Backend
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const res = await response.json();

                if (res.success) {
                    currentResultLabel = res.label;
                    currentProbability = res.probability_percent;
                    renderResult(res);
                } else {
                    alert("Gagal: " + (res.error || "Kesalahan server."));
                }

            } catch (err) {
                console.error("Fetch Error:", err);
                alert("Gagal menghubungi server backend.");
            } finally {
                btnPredict.innerHTML = originalText;
                btnPredict.disabled = false;
            }
        });
    }

    // --- 4. LOGIKA CETAK PDF ---
    if (btnPdf) {
        btnPdf.addEventListener('click', async () => {
            const originalText = btnPdf.innerHTML;
            btnPdf.innerHTML = '⏳ Mengunduh...';
            btnPdf.disabled = true;

            try {
                const response = await fetch('/api/download-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input_data: currentInputData,
                        label: currentResultLabel,
                        probability: currentProbability
                    })
                });

                const data = await response.json();

                if (data.success) {
                    window.open(data.download_url, '_blank');
                } else {
                    alert("Gagal PDF: " + data.error);
                }
            } catch (error) {
                console.error('PDF Error:', error);
                alert("Error koneksi saat download PDF.");
            } finally {
                btnPdf.innerHTML = originalText;
                btnPdf.disabled = false;
            }
        });
    }

    // --- 5. RENDER HASIL ---
    function renderResult(res) {
        resContainer.style.display = 'block';

        const isDiabetic = res.label === 'Diabetic';
        const color = isDiabetic ? '#ef4444' : '#10b981'; // Merah/Hijau Tailwind like
        
        // 1. Label Utama
        const resLabel = document.getElementById('resLabel');
        resLabel.innerText = isDiabetic ? 'TERINDIKASI DIABETES' : 'TIDAK TERINDIKASI';
        resLabel.style.color = color;
        
        // 2. Risk & Probabilitas
        document.getElementById('resRisk').innerText = res.risk_level;
        document.getElementById('resRisk').style.color = color;
        
        const probEl = document.getElementById('resProb');
        probEl.innerText = res.probability_percent + '%';
        probEl.style.color = color;

        // 3. Info Model
        if(res.model_info) {
            document.getElementById('modName').innerText = res.model_info.name;
            document.getElementById('modAcc').innerText = res.model_info.accuracy;
        }

        // 4. List Data Input (Agar user bisa review)
        const inputList = document.getElementById('inputList');
        if(inputList) {
            inputList.innerHTML = '';
            // Tampilkan beberapa data penting saja
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

        // 5. Feature Importance (Faktor Dominan)
        const featList = document.getElementById('featList');
        featList.innerHTML = '';
        
        if (res.feature_importance && res.feature_importance.length > 0) {
            res.feature_importance.forEach(f => {
                // Render sebagai List Item sesuai CSS HTML Anda
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

        // Scroll
        resContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // --- 6. LOGIKA RESET ---
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            // Confirm tidak perlu, langsung reset saja biar UX cepat
            form.reset();
            resContainer.style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});