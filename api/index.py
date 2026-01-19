import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__, template_folder="../templates", static_folder="../static")

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ======================================
# MODEL DATABASE
# ======================================
class Skrining(db.Model):
    __tablename__ = "skrining"

    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(100))
    umur = db.Column(db.Integer)
    jenis_kelamin = db.Column(db.String(20))
    sistolik = db.Column(db.Integer)
    diastolik = db.Column(db.Integer)
    kategori = db.Column(db.String(50))
    risiko = db.Column(db.String(50))
    skor_pengetahuan = db.Column(db.Integer)
    skor_sikap = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# ======================================
# HALAMAN UTAMA
# ======================================
@app.route('/')
def index():
    return render_template('index.html')

# ======================================
# HALAMAN INFORMASI
# ======================================
@app.route('/informasi')
def informasi():
    return render_template('informasi.html')

# ======================================
# PROSES SKRINING & HASIL
# ======================================
@app.route('/hasil', methods=['POST'])
def hasil():
    try:
        nama = request.form.get('nama', '').strip()
        umur = int(request.form.get('umur', 0))
        jk = request.form.get('jk', '-')

        sistolik = int(request.form.get('sistolik', 0))
        diastolik = int(request.form.get('diastolik', 0))

        if not nama or sistolik == 0 or diastolik == 0:
            return redirect('/')

    except:
        return redirect('/')

    # =========================
    # KLASIFIKASI
    # =========================
    if sistolik >= 140 or diastolik >= 90:
        kategori = "Hipertensi"
        risiko = "Tinggi"
        saran_singkat = (
            "Tekanan darah Anda tergolong tinggi. "
            "Disarankan untuk segera berkonsultasi dengan tenaga kesehatan."
        )
    elif sistolik >= 120 or diastolik >= 80:
        kategori = "Pra-Hipertensi"
        risiko = "Sedang"
        saran_singkat = (
            "Tekanan darah Anda berada di atas normal. "
            "Perubahan gaya hidup sehat sangat dianjurkan."
        )
    else:
        kategori = "Normal"
        risiko = "Rendah"
        saran_singkat = (
            "Tekanan darah Anda berada dalam batas normal. "
            "Pertahankan pola hidup sehat."
        )

    # =========================
    # SKOR PENGETAHUAN
    # =========================
    skor_pengetahuan = 0
    if request.form.get('pengetahuan_1') == "Ya":
        skor_pengetahuan += 1
    if request.form.get('pengetahuan_2') == "Ya":
        skor_pengetahuan += 1
    if request.form.get('pengetahuan_3') == "Tidak":
        skor_pengetahuan += 1

    kategori_pengetahuan = (
        "Baik" if skor_pengetahuan == 3 else
        "Sedang" if skor_pengetahuan == 2 else
        "Rendah"
    )

    # =========================
    # SKOR SIKAP
    # =========================
    skor_sikap = (
        int(request.form.get('sikap_1', 0)) +
        int(request.form.get('sikap_2', 0)) +
        int(request.form.get('sikap_3', 0))
    )

    kategori_sikap = (
        "Baik" if skor_sikap >= 10 else
        "Cukup" if skor_sikap >= 7 else
        "Kurang"
    )

    # =========================
    # SIMPAN KE DATABASE
    # =========================
    data = Skrining(
        nama=nama,
        umur=umur,
        jenis_kelamin=jk,
        sistolik=sistolik,
        diastolik=diastolik,
        kategori=kategori,
        risiko=risiko,
        skor_pengetahuan=skor_pengetahuan,
        skor_sikap=skor_sikap
    )

    db.session.add(data)
    db.session.commit()

    # =========================
    # RENDER HASIL
    # =========================
    return render_template(
        'result.html',
        nama=nama,
        umur=umur,
        jk=jk,
        sistolik=sistolik,
        diastolik=diastolik,
        kategori=kategori,
        risiko=risiko,
        saran_singkat=saran_singkat,
        skor_pengetahuan=skor_pengetahuan,
        kategori_pengetahuan=kategori_pengetahuan,
        skor_sikap=skor_sikap,
        kategori_sikap=kategori_sikap
    )

# ======================================
# HALAMAN EDUKASI
# ======================================
@app.route('/edukasi/<kategori>')
def edukasi(kategori):

    kategori = kategori.lower()

    status_map = {
        "hipertensi": (
            "Berdasarkan hasil skrining, tekanan darah Anda berada pada "
            "kategori hipertensi dan memerlukan perhatian lebih lanjut."
        ),
        "pra-hipertensi": (
            "Berdasarkan hasil skrining, tekanan darah Anda berada pada "
            "kategori pra-hipertensi dan perlu diwaspadai agar tidak meningkat."
        ),
        "normal": (
            "Berdasarkan hasil skrining, tekanan darah Anda berada pada "
            "kategori normal dan dalam rentang yang sehat."
        )
    }

    if kategori == "hipertensi":
        kategori_tampil = "Hipertensi"
        daftar_saran = [
            "Batasi konsumsi garam dan makanan tinggi lemak",
            "Lakukan aktivitas fisik minimal 30 menit setiap hari",
            "Kelola stres dengan baik",
            "Hentikan kebiasaan merokok",
            "Lakukan pemeriksaan tekanan darah secara rutin",
            "Konsultasikan dengan tenaga kesehatan"
        ]

    elif kategori == "pra-hipertensi":
        kategori_tampil = "Pra-Hipertensi"
        daftar_saran = [
            "Kurangi konsumsi makanan asin dan olahan",
            "Perbanyak konsumsi buah dan sayur",
            "Jaga berat badan ideal",
            "Lakukan olahraga ringan secara rutin",
            "Pantau tekanan darah secara berkala"
        ]

    else:
        kategori_tampil = "Normal"
        daftar_saran = [
            "Pertahankan pola makan seimbang",
            "Tetap aktif bergerak setiap hari",
            "Hindari rokok dan alkohol",
            "Kelola stres dengan baik",
            "Lakukan pemeriksaan kesehatan rutin"
        ]

    return render_template(
        'edukasi.html',
        kategori=kategori_tampil,
        status_ringkas=status_map.get(kategori, ""),
        daftar_saran=daftar_saran
    )

# ⬇️ WAJIB UNTUK VERCEL
app = app