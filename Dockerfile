# Gunakan Python 3.9 agar kompatibel
FROM python:3.9

# Buat folder kerja
WORKDIR /code

# Copy requirements dan install library
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy seluruh kodingan ke server
COPY . .

# Beri izin akses ke folder (agar tidak error permission)
RUN chmod -R 777 /code

# Jalankan aplikasi di Port 7860 (Port wajib Hugging Face)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "run_app:app"]