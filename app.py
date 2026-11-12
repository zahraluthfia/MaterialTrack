import streamlit as st
import sqlite3
import hashlib
import secrets
import pandas as pd
from pathlib import Path
from datetime import date
from io import BytesIO

# ==================================================
# CONFIGURATION
# ==================================================

DB_PATH = "materialtrack.db"
st.set_page_config(
    page_title="MaterialTrack",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# DESIGN
# ==================================================


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --pink: #E9AFC5;
    --pink-light: #FFF1F6;
    --pink-dark: #B96D8C;
    --purple: #A995C9;
    --text: #574453;
    --muted: #8D7C89;
    --border: #F0DCE6;
    --yellow: #FFD84D;
    --red: #FF5252;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 8% 10%, #FCE4EF 0, transparent 25%),
        radial-gradient(circle at 95% 85%, #EAE3FA 0, transparent 27%),
        linear-gradient(135deg, #FFFAFC, #FFF6FA 55%, #F8F5FF);
    color: var(--text);
}

.block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FCE8F0, #F5EAF8);
    border-right: 1px solid #F0D5E2;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent;
}

/* HEADING */
h1, h2, h3, h4 {
    color: #604052;
    font-weight: 800;
    letter-spacing: -0.5px;
}

p, label {
    color: #665663;
}

/* HERO */
.hero {
    background: linear-gradient(120deg, #DDEBFA, #E9DDF8, #F9DCE8);
    padding: 32px;
    border-radius: 24px;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(153, 116, 151, 0.10);
    animation: fadeUp .65s ease both;
}

.hero h1 {
    color: #344C68;
    font-size: 34px;
    font-weight: 800;
}

.hero p {
    color: #53677D;
}

.pink-hero {
    background: linear-gradient(120deg, #F9DCE8, #E9DDF8);
    padding: 27px;
    border-radius: 23px;
    margin-bottom: 23px;
    box-shadow: 0 8px 22px rgba(153, 116, 151, 0.10);
    animation: fadeUp .6s ease both;
}

.pink-hero h2 {
    color: #75465B;
    margin-bottom: 5px;
}

/* PROJECT CARD */
.project-card {
    background: rgba(255,255,255,.92);
    border: 1px solid var(--border);
    border-radius: 19px;
    padding: 20px;
    margin-bottom: 12px;
    box-shadow: 0 5px 18px rgba(128, 86, 111, .06);
    transition: transform .25s ease, box-shadow .25s ease;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 28px rgba(128, 86, 111, .13);
}

/* BUTTON */
div.stButton > button,
div.stDownloadButton > button {
    border-radius: 13px;
    font-weight: 700;
    min-height: 43px;
    border: 1px solid #E9C8D7;
    background: linear-gradient(135deg, #FFF1F6, #F9E5EF);
    color: #75465B;
    transition: all .2s ease;
    box-shadow: 0 3px 9px rgba(185, 109, 140, .08);
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #E9AFC5, #D9BCEB);
    color: white;
    border-color: #D9A5BD;
    transform: translateY(-2px);
    box-shadow: 0 7px 16px rgba(185, 109, 140, .20);
}

div.stButton > button:active,
div.stDownloadButton > button:active {
    background: #B96D8C !important;
    color: white !important;
    transform: scale(.97);
}

div.stButton > button:focus:not(:active) {
    border-color: #C77F9D;
    color: #75465B;
    box-shadow: 0 0 0 3px rgba(233, 175, 197, .25);
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.92);
    border: 1px solid #F0DCE5;
    border-radius: 18px;
    padding: 19px;
    box-shadow: 0 5px 18px rgba(128, 86, 111, .06);
    transition: transform .25s ease, box-shadow .25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 22px rgba(128, 86, 111, .12);
}

div[data-testid="stMetricLabel"] {
    color: #8D7181;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #75465B;
    font-weight: 800;
}

/* INPUT */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #604052 !important;
    -webkit-text-fill-color: #604052 !important;
    border-radius: 11px !important;
}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: #B49AA7 !important;
    -webkit-text-fill-color: #B49AA7 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #FFFFFF !important;
    border-color: #E9C8D7 !important;
    border-radius: 11px !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 9px;
    border-bottom: 1px solid #F0DCE5;
}

.stTabs [data-baseweb="tab"] {
    background: #F9E8EF;
    border-radius: 12px 12px 0 0;
    padding: 11px 17px;
    color: #806477;
    font-weight: 600;
    transition: all .2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #F1D3E0;
    color: #75465B;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #E9AFC5;
    color: #FFFFFF;
    font-weight: 800;
}

/* FORM */
div[data-testid="stForm"] {
    background: rgba(255,255,255,.95);
    padding: 19px;
    border: 1px solid #F1DCE5;
    border-radius: 18px;
    box-shadow: 0 5px 18px rgba(128, 86, 111, .05);
}

/* ALERT */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* TABLE */
div[data-testid="stDataFrame"] {
    border: 1px solid #F0DCE5;
    border-radius: 15px;
    overflow: hidden;
}

/* DIVIDER */
hr {
    border-color: #F0DCE5;
}

/* ANIMATION */
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)



# ==================================================
# DATABASE
# ==================================================

def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            planned_qty REAL DEFAULT 0,
            unit_price REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            qty REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            note TEXT
        );
        """)
        db.commit()


init_db()


# ==================================================
# PASSWORD
# ==================================================

def make_password(password):
    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        200000
    ).hex()

    return salt + ":" + hashed


def check_password(password, stored):
    try:
        salt, old_hash = stored.split(":")

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            200000
        ).hex()

        return secrets.compare_digest(new_hash, old_hash)

    except Exception:
        return False


# ==================================================
# SESSION
# ==================================================

defaults = {
    "user_id": None,
    "username": None,
    "auth_page": "welcome",
    "project_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# DATA HELPERS
# ==================================================

def get_projects(user_id):
    with connect_db() as db:
        return db.execute("""
            SELECT * FROM projects
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()


def get_project(project_id, user_id):
    with connect_db() as db:
        return db.execute("""
            SELECT * FROM projects
            WHERE id = ? AND user_id = ?
        """, (project_id, user_id)).fetchone()


def get_materials(project_id):
    with connect_db() as db:
        return db.execute("""
            SELECT * FROM materials
            WHERE project_id = ?
            ORDER BY name
        """, (project_id,)).fetchall()


def get_stock(project_id):
    with connect_db() as db:
        return db.execute("""
            SELECT
                m.id,
                m.name,
                m.unit,
                m.planned_qty,
                m.unit_price,
                COALESCE(SUM(
                    CASE WHEN t.kind = 'Masuk'
                    THEN t.qty ELSE 0 END
                ), 0) AS total_in,
                COALESCE(SUM(
                    CASE WHEN t.kind = 'Keluar'
                    THEN t.qty ELSE 0 END
                ), 0) AS total_out
            FROM materials m
            LEFT JOIN transactions t
                ON m.id = t.material_id
                AND t.project_id = m.project_id
            WHERE m.project_id = ?
            GROUP BY m.id
            ORDER BY m.name
        """, (project_id,)).fetchall()


def get_transactions(project_id, kind=None):
    with connect_db() as db:
        if kind:
            return db.execute("""
                SELECT
                    t.id,
                    m.name AS material,
                    m.unit,
                    t.kind,
                    t.qty,
                    t.transaction_date,
                    t.note
                FROM transactions t
                JOIN materials m ON m.id = t.material_id
                WHERE t.project_id = ? AND t.kind = ?
                ORDER BY t.transaction_date DESC, t.id DESC
            """, (project_id, kind)).fetchall()

        return db.execute("""
            SELECT
                t.id,
                m.name AS material,
                m.unit,
                t.kind,
                t.qty,
                t.transaction_date,
                t.note
            FROM transactions t
            JOIN materials m ON m.id = t.material_id
            WHERE t.project_id = ?
            ORDER BY t.transaction_date DESC, t.id DESC
        """, (project_id,)).fetchall()


def dataframe(rows):
    return pd.DataFrame([dict(row) for row in rows])


def rupiah(value):
    return "Rp " + f"{value:,.0f}".replace(",", ".")


# ==================================================
# AUTHENTICATION
# ==================================================

def welcome_page():
    st.markdown("""
    <div class="hero">
        <h1>🏗️ MaterialTrack</h1>
        <h3>Manage Projects, Track Materials.</h3>
        <p>
        Kelola material proyek konstruksi dengan lebih praktis,
        teratur, dan mudah dipantau.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.25, 1])

    with center:
        st.markdown(
            "<h2 style='text-align:center'>Selamat Datang!</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center'>"
            "Silakan pilih untuk melanjutkan ke MaterialTrack."
            "</p>",
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "REGISTRASI AKUN BARU",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.auth_page = "register"
            st.rerun()

        if st.button(
            "LOGIN — SUDAH PUNYA AKUN",
            use_container_width=True
        ):
            st.session_state.auth_page = "login"
            st.rerun()

        st.caption(
            "Dengan MaterialTrack, pengelolaan proyek jadi lebih mudah."
        )


def register_page():
    st.markdown("""
    <div class="hero">
        <h1> Buat Akun Baru</h1>
        <p>Daftar terlebih dahulu untuk mulai menggunakan MaterialTrack.</p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.2, 1])

    with center:
        with st.form("register_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm = st.text_input(
                "Konfirmasi Password",
                type="password"
            )

            submit = st.form_submit_button(
                "Daftar Sekarang",
                use_container_width=True
            )

        if submit:
            username = username.strip()

            if len(username) < 3:
                st.error("Username minimal 3 karakter.")
            elif len(password) < 8:
                st.error("Password minimal 8 karakter.")
            elif password != confirm:
                st.error("Konfirmasi password tidak sama.")
            else:
                try:
                    with connect_db() as db:
                        db.execute("""
                            INSERT INTO users (username, password)
                            VALUES (?, ?)
                        """, (username, make_password(password)))
                        db.commit()

                    st.success(
                        "Registrasi berhasil! Sekarang silakan login."
                    )
                    st.session_state.auth_page = "login"
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error("Username sudah digunakan.")

        if st.button("← Kembali"):
            st.session_state.auth_page = "welcome"
            st.rerun()


def login_page():
    st.markdown("""
    <div class="hero">
        <h1> Login MaterialTrack</h1>
        <p>Masuk menggunakan akun yang sudah kamu daftarkan.</p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.2, 1])

    with center:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submit = st.form_submit_button(
                "Masuk",
                use_container_width=True,
                type="primary"
            )

        if submit:
            with connect_db() as db:
                user = db.execute("""
                    SELECT * FROM users
                    WHERE username = ?
                """, (username.strip(),)).fetchone()

            if user and check_password(password, user["password"]):
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                st.session_state.project_id = None
                st.rerun()
            else:
                st.error("Username atau password salah.")

        if st.button("← Kembali"):
            st.session_state.auth_page = "welcome"
            st.rerun()


# ==================================================
# SIDEBAR
# ==================================================

def sidebar():
    with st.sidebar:
        st.markdown("## MaterialTrack")
        st.caption("Construction Management")

        st.divider()

        st.write("Halo,")
        st.markdown(f"### {st.session_state.username}")

        st.divider()

        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.project_id = None
            st.rerun()

        if st.session_state.project_id is not None:
            if st.button("📁 Proyek Aktif", use_container_width=True):
                st.rerun()

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.project_id = None
            st.session_state.auth_page = "welcome"
            st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

def dashboard():
    user_id = st.session_state.user_id

    st.markdown(f"""
    <div class="pink-hero">
        <h2>Halo, {st.session_state.username}! </h2>
        <p>Selamat datang di dashboard proyek MaterialTrack.</p>
    </div>
    """, unsafe_allow_html=True)

    projects = get_projects(user_id)

    col1, col2 = st.columns([4, 1])

    with col1:
        st.subheader("Proyek Saya")
        st.caption("Semua proyek yang kamu kelola.")

    with col2:
        st.metric("Jumlah Proyek", len(projects))

    with st.expander("＋ Tambah Proyek Baru", expanded=False):
        with st.form("new_project"):
            name = st.text_input("Nama proyek")
            location = st.text_input("Lokasi proyek")

            c1, c2 = st.columns(2)

            with c1:
                start = st.date_input(
                    "Tanggal mulai",
                    value=date.today()
                )

            with c2:
                end = st.date_input(
                    "Target selesai",
                    value=date.today()
                )

            description = st.text_area("Deskripsi proyek")

            save = st.form_submit_button(
                "Simpan Proyek",
                use_container_width=True
            )

        if save:
            if not name.strip():
                st.error("Nama proyek harus diisi.")
            elif end < start:
                st.error("Tanggal selesai tidak boleh sebelum tanggal mulai.")
            else:
                with connect_db() as db:
                    db.execute("""
                        INSERT INTO projects
                        (user_id, name, location, start_date, end_date, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        name.strip(),
                        location,
                        str(start),
                        str(end),
                        description
                    ))
                    db.commit()

                st.success("Proyek berhasil ditambahkan.")
                st.rerun()

    if not projects:
        st.info(
            "Belum ada proyek. Tambahkan proyek pertamamu "
            "melalui tombol Tambah Proyek Baru."
        )
        return

    cols = st.columns(2)

    pastel_colors = ["#FCE5EE", "#E9E1F8", "#DFF2E9", "#FFF0D5"]

    for index, project in enumerate(projects):
        with cols[index % 2]:
            color = pastel_colors[index % len(pastel_colors)]

            st.markdown(f"""
            <div class="project-card" style="background:{color}">
                <h3>🏗️ {project['name']}</h3>
                <p>📍 {project['location'] or 'Lokasi belum diisi'}</p>
                <p>📅 {project['start_date']} — {project['end_date']}</p>
                <small>{project['description'] or 'Tidak ada deskripsi.'}</small>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                "Buka Proyek →",
                key=f"project_{project['id']}",
                use_container_width=True
            ):
                st.session_state.project_id = project["id"]
                st.rerun()


# ==================================================
# PROJECT DETAIL
# ==================================================

def project_detail():
    user_id = st.session_state.user_id
    project_id = st.session_state.project_id

    project = get_project(project_id, user_id)

    if not project:
        st.session_state.project_id = None
        st.rerun()

    if st.button("← Kembali ke Dashboard"):
        st.session_state.project_id = None
        st.rerun()

    st.markdown(f"""
    <div class="pink-hero">
        <h2>🏗️ {project['name']}</h2>
        <p>📍 {project['location'] or 'Lokasi belum diisi'}</p>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------
    # RINGKASAN MONITORING STOK
    # --------------------------

    st.subheader("Ringkasan Monitoring Stok")

    stock_summary = get_stock(project_id)

    normal_count = 0
    warning_count = 0
    critical_count = 0
    no_rab_count = 0

    for m in stock_summary:
        remaining = float(m["total_in"] or 0) - float(m["total_out"] or 0)
        planned = float(m["planned_qty"] or 0)

        if planned <= 0:
            no_rab_count += 1
            continue

        percentage = (remaining / planned) * 100

        if remaining < 0 or percentage <= 3:
            critical_count += 1
        elif percentage <= 10:
            warning_count += 1
        else:
            normal_count += 1

    total_material = len(stock_summary)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Material", total_material)
    c2.metric("Normal", normal_count)
    c3.metric("Stok Menipis", warning_count)
    c4.metric("Stok Kritis", critical_count)

    if critical_count > 0:
        st.error(
            f"🔴 PERINGATAN! Ada {critical_count} material "
            "dalam kondisi kritis atau defisit. Segera lakukan pengadaan."
        )

    if warning_count > 0:
        st.warning(
            f"🟡 PERHATIAN! Ada {warning_count} material "
            "yang stoknya mulai menipis."
        )

    if critical_count == 0 and warning_count == 0:
        st.success("🩷 Semua stok material dalam kondisi normal.")

    if no_rab_count > 0:
        st.info(
            f"Ada {no_rab_count} material yang belum memiliki "
            "jumlah kebutuhan RAB."
        )

    st.divider()

    overview, rab, incoming, outgoing, stock_report = st.tabs([
        "Overview",
        "Data Material / RAB",
        "Material Masuk",
        "Material Keluar",
        "Stok & Laporan"
    ])

    # --------------------------
    # OVERVIEW
    # --------------------------

    with overview:
        materials = get_stock(project_id)

        total_types = len(materials)
        total_in = sum(m["total_in"] for m in materials)
        total_out = sum(m["total_out"] for m in materials)
        total_stock = total_in - total_out

        st.subheader("Ringkasan Proyek")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Jenis Material", total_types)
        c2.metric("Material Masuk", f"{total_in:,g}")
        c3.metric("Material Keluar", f"{total_out:,g}")
        c4.metric("Sisa Stok", f"{total_stock:,g}")

        st.divider()

        st.subheader("Informasi Proyek")
        st.write(f"**Nama:** {project['name']}")
        st.write(f"**Lokasi:** {project['location'] or '-'}")
        st.write(f"**Tanggal mulai:** {project['start_date'] or '-'}")
        st.write(f"**Target selesai:** {project['end_date'] or '-'}")
        st.write(f"**Deskripsi:** {project['description'] or '-'}")

        st.subheader("Transaksi Terbaru")

        recent = get_transactions(project_id)

        if recent:
            st.dataframe(
                dataframe(recent).head(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Belum ada transaksi material.")

    # --------------------------
    # RAB / MATERIAL
    # --------------------------

    with rab:
        st.subheader("Data Material dari RAB")
        st.caption("Masukkan material yang direncanakan dalam proyek.")

        with st.form("add_material"):
            name = st.text_input("Nama material")

            unit = st.selectbox(
                "Satuan",
                [
                    "m³", "m²", "m", "kg", "ton",
                    "batang", "sak", "unit", "liter", "lainnya"
                ]
            )

            qty = st.number_input(
                "Volume kebutuhan RAB",
                min_value=0.0,
                step=1.0
            )

            price = st.number_input(
                "Harga satuan (Rp)",
                min_value=0.0,
                step=1000.0
            )

            save_material = st.form_submit_button(
                "＋ Tambahkan Material",
                use_container_width=True
            )

        if save_material:
            if not name.strip():
                st.error("Nama material harus diisi.")
            else:
                with connect_db() as db:
                    db.execute("""
                        INSERT INTO materials
                        (project_id, name, unit, planned_qty, unit_price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        project_id,
                        name.strip(),
                        unit,
                        qty,
                        price
                    ))
                    db.commit()

                st.success("Material berhasil ditambahkan.")
                st.rerun()

        materials = get_stock(project_id)

        if materials:
            rab_rows = []

            for m in materials:
                rab_rows.append({
                    "Material": m["name"],
                    "Satuan": m["unit"],
                    "Volume RAB": m["planned_qty"],
                    "Harga Satuan": m["unit_price"],
                    "Total Anggaran": m["planned_qty"] * m["unit_price"]
                })

            st.dataframe(
                pd.DataFrame(rab_rows),
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.write("**Hapus material**")

            material_options = {
                f"{m['name']} ({m['unit']})": m["id"]
                for m in materials
            }

            selected_delete = st.selectbox(
                "Pilih material yang akan dihapus",
                list(material_options.keys()),
                key="delete_material_select"
            )

            if st.button("Hapus Material Terpilih"):
                material_id = material_options[selected_delete]

                with connect_db() as db:
                    db.execute("""
                        DELETE FROM transactions
                        WHERE project_id = ? AND material_id = ?
                    """, (project_id, material_id))

                    db.execute("""
                        DELETE FROM materials
                        WHERE id = ? AND project_id = ?
                    """, (material_id, project_id))

                    db.commit()

                st.success("Material berhasil dihapus.")
                st.rerun()

        else:
            st.info("Belum ada data material.")

    # --------------------------
    # TRANSACTIONS
    # --------------------------

    def transaction_page(kind):
        st.subheader(f"Catat Material {kind}")

        materials = get_materials(project_id)

        if not materials:
            st.warning(
                "Tambahkan material terlebih dahulu di menu Data Material / RAB."
            )
            return

        options = {
            f"{m['name']} ({m['unit']})": m["id"]
            for m in materials
        }

        with st.form(f"transaction_{kind}"):
            selected = st.selectbox(
                "Pilih material",
                list(options.keys())
            )

            qty = st.number_input(
                "Jumlah",
                min_value=0.01,
                step=1.0
            )

            trans_date = st.date_input(
                "Tanggal transaksi",
                value=date.today()
            )

            note = st.text_input("Keterangan (opsional)")

            submit = st.form_submit_button(
                f"Simpan Material {kind}",
                use_container_width=True
            )

        if submit:
            material_id = options[selected]

            with connect_db() as db:
                if kind == "Keluar":
                    current = db.execute("""
                        SELECT
                            COALESCE(SUM(
                                CASE WHEN kind = 'Masuk'
                                THEN qty ELSE 0 END
                            ), 0) -
                            COALESCE(SUM(
                                CASE WHEN kind = 'Keluar'
                                THEN qty ELSE 0 END
                            ), 0) AS stock
                        FROM transactions
                        WHERE project_id = ? AND material_id = ?
                    """, (project_id, material_id)).fetchone()

                    if qty > current["stock"]:
                        st.error(
                            f"Stok tidak cukup. "
                            f"Stok tersedia: {current['stock']}."
                        )
                        return

                db.execute("""
                    INSERT INTO transactions
                    (project_id, material_id, kind, qty, transaction_date, note)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    material_id,
                    kind,
                    qty,
                    str(trans_date),
                    note
                ))
                db.commit()

            st.success(f"Material {kind.lower()} berhasil dicatat.")
            st.rerun()

        st.divider()
        st.write(f"**Riwayat Material {kind}**")

        history = get_transactions(project_id, kind)

        if history:
            st.dataframe(
                dataframe(history),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Belum ada transaksi.")

    with incoming:
        transaction_page("Masuk")

    with outgoing:
        transaction_page("Keluar")

    # --------------------------
    # STOCK AND REPORT
    # --------------------------

    with stock_report:
        st.subheader("Stok Material")

        stock = get_stock(project_id)

        if not stock:
            st.info("Belum ada material.")
        else:
            
            rows = []

            for m in stock:
                remaining = m["total_in"] - m["total_out"]
                planned = float(m["planned_qty"] or 0)

                if planned <= 0:
                    remaining_pct = None
                    status = "Belum ada RAB"
                else:
                    remaining_pct = (remaining / planned) * 100

                    if remaining < 0:
                        status = "Defisit"
                    elif remaining_pct <= 3:
                        status = "Kritis"
                    elif remaining_pct <= 10:
                        status = "Menipis"
                    else:
                        status = "Normal"

                rows.append({
                    "Material": m["name"],
                    "Satuan": m["unit"],
                    "Kebutuhan RAB": m["planned_qty"],
                    "Material Masuk": m["total_in"],
                    "Material Keluar": m["total_out"],
                    "Sisa Stok": remaining,
                    "Persentase Sisa": remaining_pct,
                    "Status Stok": status,
                    "Harga Satuan": m["unit_price"],
                    "Nilai Stok": remaining * m["unit_price"]
                })

            stock_df = pd.DataFrame(rows)

            def warna_status(row):
                status = row["Status Stok"]

                if status in ["Kritis", "Defisit"]:
                    color = (
                        "background-color: #FF2424;"
                        "color: white;"
                        "font-weight: bold;"
                    )
                elif status == "Menipis":
                    color = (
                        "background-color: #FFD500;"
                        "color: #392B00;"
                        "font-weight: bold;"
                    )
                else:
                    color = (
                        "background-color: #FCE8F0;"
                        "color: #604052;"
                    )

                return [color] * len(row)

            styled_stock = (
                stock_df.style
                .apply(warna_status, axis=1)
                .format({
                    "Persentase Sisa": lambda x:
                        "—" if pd.isna(x) else f"{x:.1f}%"
                })
            )

            st.dataframe(
                styled_stock,
                use_container_width=True,
                hide_index=True
            )

            st.metric(
                "Total Nilai Stok",
                rupiah(stock_df["Nilai Stok"].sum())
            )

            st.divider()
            st.subheader("Unduh Laporan Excel")

            transaction_rows = get_transactions(project_id)
            transaction_df = dataframe(transaction_rows)

            output = BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:
                stock_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Stok Material"
                )

                transaction_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Riwayat Transaksi"
                )

            st.download_button(
                "⬇️ Download Laporan Excel",
                data=output.getvalue(),
                file_name=f"Laporan_{project['name']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


# ==================================================
# MAIN APP
# ==================================================

if st.session_state.user_id is None:

    if st.session_state.auth_page == "register":
        register_page()

    elif st.session_state.auth_page == "login":
        login_page()

    else:
        welcome_page()

else:
    sidebar()

    if st.session_state.project_id is None:
        dashboard()
    else:
        project_detail()
