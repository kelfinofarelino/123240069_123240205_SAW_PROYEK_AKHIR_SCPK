import streamlit as st
import saw_processing as saw

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(
    page_title="DSS Pemilihan Hotel | SAW", page_icon="🏨", layout="wide"
)

st.title("🏨 Sistem Pendukung Keputusan Pemilihan Hotel di Jakarta")
st.markdown(
    "Aplikasi ini menggunakan metode **Simple Additive Weighting (SAW)** dengan **5 Kriteria**."
)


# ==========================================
# 2. PEMUATAN DATA
# ==========================================
# Membungkus fungsi dari saw ke dalam st.cache_data untuk optimasi memori
@st.cache_data
def get_data():
    return saw.load_and_preprocess_data(
        "dataset/Hotel List Jakarta - TRAVELOKA - 1-30.csv"
    )


try:
    df_raw, df_matrix = get_data()
except FileNotFoundError:
    st.error(
        "❌ Dataset tidak ditemukan. Pastikan file 'Hotel List Jakarta - TRAVELOKA - 1-30.csv' berada di dalam folder 'dataset/'."
    )
    st.stop()

# ==========================================
# 3. SIDEBAR PENGATURAN BOBOT
# ==========================================
st.sidebar.header("⚙️ Pengaturan Bobot")
st.sidebar.markdown(
    "Ketik bobot kriteria. **Total harus tepat 100**. Jika tidak, perhitungan tidak dapat dilakukan."
)
st.sidebar.markdown("---")

w_c1 = st.sidebar.number_input(
    "Bobot C1 (Harga) - Cost", min_value=0, max_value=100, value=30, step=10
)
w_c2 = st.sidebar.number_input(
    "Bobot C2 (Rating) - Benefit", min_value=0, max_value=100, value=25, step=10
)
w_c3 = st.sidebar.number_input(
    "Bobot C3 (Star) - Benefit", min_value=0, max_value=100, value=20, step=10
)
w_c4 = st.sidebar.number_input(
    "Bobot C4 (Reviews) - Benefit", min_value=0, max_value=100, value=10, step=10
)
w_c5 = st.sidebar.number_input(
    "Bobot C5 (Fasilitas) - Benefit", min_value=0, max_value=100, value=15, step=10
)

total_bobot = w_c1 + w_c2 + w_c3 + w_c4 + w_c5

st.sidebar.markdown("---")

# ERROR HANDLING DAN KONVERSI BOBOT
is_weight_valid = total_bobot == 100

if not is_weight_valid:
    st.sidebar.error(f"⚠️ Total bobot saat ini {total_bobot}. Harus tepat 100.")
else:
    st.sidebar.success("✅ Total bobot valid (100).")

# Konversi skala (1-100) menjadi desimal (0-1) untuk matriks array
W = [w_c1 / 100, w_c2 / 100, w_c3 / 100, w_c4 / 100, w_c5 / 100]

# 0 = Cost (Harga), 1 = Benefit (Rating, Star, Reviews, Fasilitas)
atribut = [0, 1, 1, 1, 1]

# ==========================================
# 4. TAMPILAN TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Matriks Keputusan (X)",
        "🔄 Normalisasi (R)",
        "🏆 Hasil Akhir (V) & Matriks",
        "📈 Visualisasi",
    ]
)

# Menjalankan Normalisasi langsung melalui Backend API
df_norm = saw.calculate_normalization(df_matrix, atribut)

with tab1:
    st.subheader("1. Matriks Keputusan Awal (X)")
    st.markdown("Menampilkan nilai aktual dari 5 kriteria hotel.")
    st.dataframe(df_matrix, use_container_width=True)

with tab2:
    st.subheader("2. Matriks Normalisasi (R)")
    st.dataframe(
        df_norm.style.format(
            {
                "C1 (Harga)": "{:.4f}",
                "C2 (Rating)": "{:.4f}",
                "C3 (Star)": "{:.4f}",
                "C4 (Reviews)": "{:.4f}",
                "C5 (Fasilitas)": "{:.4f}",
            }
        ),
        use_container_width=True,
    )

with tab3:
    st.subheader("3. Perhitungan Nilai Preferensi (V) & Perankingan")

    if is_weight_valid:
        st.markdown(
            "Tabel ini menampilkan **Skor Akhir** bersanding dengan **Matriks Awal** secara lengkap."
        )

        # Eksekusi skor akhir menggunakan module logic
        df_final = saw.calculate_final_score(df_matrix, df_norm, W)

        st.dataframe(
            df_final.style.format(
                {
                    "Skor Akhir": "{:.4f}",
                    "C1 (Harga)": "Rp {:,.0f}",
                    "C2 (Rating)": "{:.1f}",
                    "C3 (Star)": "{:.0f}",
                    "C4 (Reviews)": "{:.0f}",
                    "C5 (Fasilitas)": "{:.0f}",
                }
            ).background_gradient(cmap="Greens", subset=["Skor Akhir"]),
            use_container_width=True,
        )

        top_hotel = df_final.iloc[0]["Alternatif (Hotel)"]
        top_score = df_final.iloc[0]["Skor Akhir"]
        st.success(
            f"🎉 **Rekomendasi Terbaik:** Alternatif terbaik adalah **{top_hotel}** dengan skor akhir **{top_score:.4f}**."
        )
    else:
        st.error(
            f"❌ **Perhitungan Dihentikan.** Total bobot saat ini adalah {total_bobot}. Silakan perbaiki input bobot di menu samping kiri agar jumlahnya tepat 100."
        )

with tab4:
    st.subheader("📈 Visualisasi Ranking Hotel")

    if is_weight_valid:
        st.markdown("Menampilkan Top 15 Hotel berdasarkan Skor Preferensi Akhir (V)")
        chart_data = df_final.head(15)[["Alternatif (Hotel)", "Skor Akhir"]]
        chart_data = chart_data.set_index("Alternatif (Hotel)")
        st.bar_chart(chart_data, color="#2ECC71")
    else:
        st.error(
            "❌ Grafik tidak dapat ditampilkan karena proporsi bobot belum mencapai 100."
        )

st.markdown("---")
st.markdown("💡 *Dibuat untuk keperluan Praktikum Sistem Pendukung Keputusan*")
