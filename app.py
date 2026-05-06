import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="DSS Pemilihan Hotel | SAW", page_icon="🏨", layout="wide")

st.title("🏨 Sistem Pendukung Keputusan Pemilihan Hotel di Jakarta")
st.markdown("Aplikasi ini menggunakan metode **Simple Additive Weighting (SAW)** dengan **5 Kriteria**.")

# ==========================================
# 2. FUNGSI PEMROSESAN DATA
# ==========================================
@st.cache_data
def load_and_preprocess_data():
    df = pd.read_csv('dataset/Hotel List Jakarta - TRAVELOKA - 1-30.csv')
    df = df.dropna(subset=['Harga']).reset_index(drop=True)
    
    # Cleansing Harga
    df['Harga_Clean'] = df['Harga'].str.replace('.', '', regex=False).astype(float)
    
    # Menghitung C5 (Fasilitas)
    def count_facilities(text):
        if pd.isna(text): return 0
        lines = [line.strip() for line in text.split('\n') if line.strip() and not line.strip().endswith(':')]
        return len(lines)
    
    df['Facility_Count'] = df['Facil + Akomod'].apply(count_facilities)
    
    # Matriks X (5 Kriteria)
    kriteria_df = df[['Hotel', 'Harga_Clean', 'Rating', 'Star', 'Reviews', 'Facility_Count']].copy()
    kriteria_df.columns = ['Alternatif (Hotel)', 'C1 (Harga)', 'C2 (Rating)', 'C3 (Star)', 'C4 (Reviews)', 'C5 (Fasilitas)']
    
    return df, kriteria_df

df_raw, df_matrix = load_and_preprocess_data()

# ==========================================
# 3. SIDEBAR PENGATURAN BOBOT DENGAN ERROR HANDLING
# ==========================================
st.sidebar.header("⚙️ Pengaturan Bobot")
st.sidebar.markdown("Ketik bobot kriteria. **Total harus tepat 100**. Jika tidak, perhitungan tidak dapat dilakukan.")
st.sidebar.markdown("---")

w_c1 = st.sidebar.number_input("Bobot C1 (Harga) - Cost", min_value=0, max_value=100, value=30, step=10)
w_c2 = st.sidebar.number_input("Bobot C2 (Rating) - Benefit", min_value=0, max_value=100, value=25, step=10)
w_c3 = st.sidebar.number_input("Bobot C3 (Star) - Benefit", min_value=0, max_value=100, value=20, step=10)
w_c4 = st.sidebar.number_input("Bobot C4 (Reviews) - Benefit", min_value=0, max_value=100, value=10, step=10)
w_c5 = st.sidebar.number_input("Bobot C5 (Fasilitas) - Benefit", min_value=0, max_value=100, value=15, step=10)

total_bobot = w_c1 + w_c2 + w_c3 + w_c4 + w_c5

st.sidebar.markdown("---")
# ERROR HANDLING
if total_bobot != 100:
    st.sidebar.error(f"⚠️ Total bobot saat ini {total_bobot}. Harus tepat 100.")
else:
    st.sidebar.success("✅ Total bobot valid (100).")

# Konversi ke skala 0-1 untuk perhitungan
W = [w_c1/100, w_c2/100, w_c3/100, w_c4/100, w_c5/100]

# ==========================================
# 4. TAMPILAN TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Matriks Keputusan (X)", "🔄 Normalisasi (R)", "🏆 Hasil Akhir (V) & Matriks", "📈 Visualisasi"])

with tab1:
    st.subheader("1. Matriks Keputusan Awal (X)")
    st.markdown("Menampilkan nilai aktual dari 5 kriteria hotel.")
    st.dataframe(df_matrix, use_container_width=True)

with tab2:
    st.subheader("2. Matriks Normalisasi (R)")
    
    df_norm = df_matrix.copy()
    
    # C1 (Cost) = Min / X
    min_c1 = df_matrix['C1 (Harga)'].min()
    df_norm['C1 (Harga)'] = min_c1 / df_matrix['C1 (Harga)']
    
    # C2-C5 (Benefit) = X / Max
    for col in ['C2 (Rating)', 'C3 (Star)', 'C4 (Reviews)', 'C5 (Fasilitas)']:
        max_val = df_matrix[col].max()
        df_norm[col] = df_matrix[col] / max_val
        
    st.dataframe(df_norm.style.format({
        'C1 (Harga)': "{:.4f}", 'C2 (Rating)': "{:.4f}", 
        'C3 (Star)': "{:.4f}", 'C4 (Reviews)': "{:.4f}", 'C5 (Fasilitas)': "{:.4f}"
    }), use_container_width=True)

with tab3:
    st.subheader("3. Perhitungan Nilai Preferensi (V) & Perankingan")
    
    # LOGIKA ERROR HANDLING: Hanya tampilkan hasil jika bobot valid
    if total_bobot == 100:
        st.markdown("Tabel ini menampilkan **Skor Akhir** bersanding dengan **Matriks Awal** secara lengkap.")
        
        # Hitung V
        df_v = pd.DataFrame({'Alternatif (Hotel)': df_norm['Alternatif (Hotel)']})
        df_v['Skor Akhir'] = (
            (df_norm['C1 (Harga)'] * W[0]) +
            (df_norm['C2 (Rating)'] * W[1]) +
            (df_norm['C3 (Star)'] * W[2]) +
            (df_norm['C4 (Reviews)'] * W[3]) +
            (df_norm['C5 (Fasilitas)'] * W[4])
        )
        
        # Gabungkan Skor Akhir dengan isi matriks asli
        df_final = pd.merge(df_v, df_matrix, on='Alternatif (Hotel)')
        
        # Sorting dari skor tertinggi
        df_final = df_final.sort_values(by='Skor Akhir', ascending=False).reset_index(drop=True)
        df_final.index = df_final.index + 1 
        df_final.index.name = 'Peringkat'
        
        # Penyesuaian agar tabel tetap rapi
        st.dataframe(
            df_final.style.format({
                'Skor Akhir': "{:.4f}",
                'C1 (Harga)': "Rp {:,.0f}",
                'C2 (Rating)': "{:.1f}",
                'C3 (Star)': "{:.0f}",
                'C4 (Reviews)': "{:.0f}",
                'C5 (Fasilitas)': "{:.0f}"
            }).background_gradient(cmap='Greens', subset=['Skor Akhir']), 
            use_container_width=True
        )
        
        top_hotel = df_final.iloc[0]['Alternatif (Hotel)']
        top_score = df_final.iloc[0]['Skor Akhir']
        st.success(f"🎉 **Rekomendasi Terbaik:** Alternatif terbaik adalah **{top_hotel}** dengan skor akhir **{top_score:.4f}**.")
    else:
        # Peringatan jika bobot salah
        st.error(f"❌ **Perhitungan Dihentikan.** Total bobot saat ini adalah {total_bobot}. Silakan perbaiki input bobot di menu samping kiri agar jumlahnya tepat 100.")

with tab4:
    st.subheader("📈 Visualisasi Ranking Hotel")
    
    # LOGIKA ERROR HANDLING: Hanya tampilkan grafik jika bobot valid
    if total_bobot == 100:
        st.markdown("Menampilkan Top 15 Hotel berdasarkan Skor Preferensi Akhir (V)")
        
        # Ambil 15 besar dan pilih kolom yang dibutuhkan saja
        chart_data = df_final.head(15)[['Alternatif (Hotel)', 'Skor Akhir']]
        
        # Jadikan nama hotel sebagai Index agar terbaca sebagai label sumbu X/Y
        chart_data = chart_data.set_index('Alternatif (Hotel)')
        
        # Gunakan bar_chart bawaan Streamlit (Lebih stabil & anti-blank)
        st.bar_chart(chart_data, color="#2ECC71")
        
    else:
        # Peringatan jika bobot salah
        st.error("❌ Grafik tidak dapat ditampilkan karena proporsi bobot belum mencapai 100.")

# Footer
st.markdown("---")
st.markdown("💡 *Dibuat untuk keperluan Praktikum Sistem Pendukung Keputusan*")