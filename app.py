import streamlit as st
import saw_preprocessing as saw

# ==========================================
# 1. MAIN CONFIGURATION & GUI
# ==========================================
st.set_page_config(
    page_title="DSS Hotel Bali | SAW", 
    page_icon="🏨", 
    layout="wide"
)

st.title("🏨 Smart Decision Support System for Hotel Selection in Bali")
st.markdown(
    """
    This application uses the **Simple Additive Weighting (SAW)** method to provide 
    the best hotel recommendations in Bali using real data.
    """
)

# ==========================================
# 2. DATASET LOADING
# ==========================================
# Wrap data loading function
@st.cache_data
def get_data():
    return saw.load_and_preprocess_data("dataset/Updated_ScrapingHotelTiketcom.csv")

try:
    df_raw, df_matrix = get_data()
except FileNotFoundError:
    st.error("❌ Dataset not found. Please ensure the Bali CSV file is inside the 'dataset/' folder.")
    st.stop()

# ==========================================
# 3. SIDEBAR
# ==========================================
st.sidebar.header("⚙️ Criteria Weights Settings")
st.sidebar.markdown("The total of all criteria weights must be exactly 100.")
st.sidebar.markdown("---")

w_c1 = st.sidebar.slider("C1 Weight (Price) [Cost]", 0, 100, 30, step=5)
w_c2 = st.sidebar.slider("C2 Weight (Rating) [Benefit]", 0, 100, 20, step=5)
w_c3 = st.sidebar.slider("C3 Weight (Star) [Benefit]", 0, 100, 15, step=5)
w_c4 = st.sidebar.number_input("C4 Weight (Reviews) [Benefit]", min_value=0, max_value=100, value=15, step=5)
w_c5 = st.sidebar.number_input("C5 Weight (Facilities) [Benefit]", min_value=0, max_value=100, value=20, step=5)

total_weight = w_c1 + w_c2 + w_c3 + w_c4 + w_c5
st.sidebar.markdown("---")

is_weight_valid = (total_weight == 100)

if not is_weight_valid:
    st.sidebar.error(f"⚠️ Current total weight: **{total_weight}**. It must be exactly 100.")
else:
    st.sidebar.success("✅ Total weight is valid (100).")

W = [w_c1 / 100, w_c2 / 100, w_c3 / 100, w_c4 / 100, w_c5 / 100]
attributes = [0, 1, 1, 1, 1] 

# Preprocessing file call normalization
df_norm = saw.calculate_normalization(df_matrix, attributes)

# ==========================================
# 4. TABS & CALCULATION
# ==========================================
tab_profile, tab_data, tab_norm, tab_calc, tab_chart = st.tabs([
    "👥 Group Profile", "📊 Matrix (X)", "🔄 Normalization (R)", "🏆 Result (V)", "📈 Visualization"
])

with tab_profile:
    st.subheader("👥 Developer Group Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.info("### Member 1\n* **Name:** Adhafa Joan Putranto\n* **NIM:** 123240069\n* **Role:** Data Preprocessing & Model Analyst")
    with col2:
        st.success("### Member 2\n* **Name:** Muhammad Farelino Kelfin\n* **NIM:** 123240205\n* **Role:** Streamlit GUI Developer & System Algorithm")

with tab_data:
    st.subheader("1. Initial Decision Matrix (X)")
    st.dataframe(df_matrix, use_container_width=True)

with tab_norm:
    st.subheader("2. Normalized Matrix (R)")
    st.dataframe(
        df_norm.style.format("{:.4f}"),
        use_container_width=True
    )

with tab_calc:
    st.subheader("3. Preference Value Calculation (V)")
    
    if is_weight_valid:
        with st.form(key="saw_calculation_form"):
            st.markdown("Click the button below to explore the hotel recommendation rankings.")
            calc_button = st.form_submit_button("🚀 Calculate DSS Ranking", type="primary")
            
            if calc_button:
                # Call final score calculation from preprocessing file
                st.session_state['df_final_result'] = saw.calculate_final_score(df_matrix, df_norm, W)
                st.session_state['show_results'] = True
                
        # Display result outside the form container
        if st.session_state.get('show_results', False) and 'df_final_result' in st.session_state:
            st.success("🎉 Successfully executed!")
            df_display = st.session_state['df_final_result']
            st.dataframe(
                df_display.style.format({
                    "Final Score": "{:.4f}",
                    "C1 (Price)": "Rp {:,.0f}",
                    "C2 (Rating)": "{:.1f}",
                    "C3 (Star)": "{:.0f}",
                    "C4 (Reviews)": "{:.0f}",
                    "C5 (Facilities)": "{:.0f}"
                }).background_gradient(cmap="Greens", subset=["Final Score"]),
                use_container_width=True
            )
            top_alt = df_display.iloc[0]['Alternative (Hotel)']
            top_score = df_display.iloc[0]['Final Score']
            st.success(f"🏅 **Best Recommendation:** Hotel **{top_alt}** with a score of **{top_score:.4f}**.")
    else:
        st.error("❌ Adjust the weights until the total is 100 to calculate.")
        st.session_state['show_results'] = False

with tab_chart:
    st.subheader("📈 Data Visualizations")
    
    if is_weight_valid and st.session_state.get('show_results', False) and 'df_final_result' in st.session_state:
        df_full = st.session_state['df_final_result']
        
        # Mengambil data 15 hotel terbaik berdasarkan Final Score
        df_top15 = df_full.head(15)
        
        # ---------------------------------------------------------
        # Visualisasi 1: BAR CHART (Peringkat Skor Akhir)
        # ---------------------------------------------------------
        st.markdown("#### 1. Top 15 Best Hotels (Bar Chart)")
        st.markdown("*Menampilkan peringkat 15 hotel terbaik berdasarkan skor rekomendasi akhir.*")
        chart_data_bar = df_top15[['Alternative (Hotel)', 'Final Score']].set_index('Alternative (Hotel)')
        st.bar_chart(chart_data_bar, color="#2ECC71") # Warna Hijau
        
        st.divider()
        
        # ---------------------------------------------------------
        # Visualisasi 2: SCATTER CHART (Korelasi Harga vs Skor)
        # ---------------------------------------------------------
        st.markdown("#### 2. Persebaran Harga vs Final Score (Scatter Chart)")
        st.markdown("*Melihat hubungan apakah hotel dengan harga yang lebih mahal selalu memiliki skor akhir yang lebih tinggi.*")
        st.scatter_chart(
            data=df_full, 
            x='C1 (Price)', 
            y='Final Score', 
            color="#3498DB" # Warna Biru
        )
        
        st.divider()
        
        # ---------------------------------------------------------
        # Visualisasi 3: AREA CHART (Tren Jumlah Ulasan)
        # ---------------------------------------------------------
        st.markdown("#### 3. Jumlah Ulasan pada Top 15 Hotel Terbaik (Area Chart)")
        st.markdown("*Melihat popularitas (jumlah review/ulasan) dari ke-15 hotel terbaik tersebut.*")
        chart_data_area = df_top15[['Alternative (Hotel)', 'C4 (Reviews)']].set_index('Alternative (Hotel)')
        st.area_chart(chart_data_area, color="#E74C3C") # Warna Merah
        
    else:
        st.info("💡 Hitung data terlebih dahulu di tab '🏆 Result (V)' untuk melihat visualisasi.")