import pandas as pd
import numpy as np


def count_facilities(text):
    """Fungsi bantuan untuk menghitung jumlah baris fasilitas"""
    if pd.isna(text):
        return 0
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip() and not line.strip().endswith(":")
    ]
    return len(lines)


def load_and_preprocess_data(filepath):
    """Memuat data, melakukan data cleansing, dan membentuk Matriks X"""
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["Harga"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["Hotel"], keep="first").reset_index(drop=True)

    # Cleansing Harga
    df["Harga_Clean"] = df["Harga"].str.replace(".", "", regex=False).astype(float)

    # Menghitung C5 (Fasilitas)
    df["Facility_Count"] = df["Facil + Akomod"].apply(count_facilities)

    # Matriks X (5 Kriteria)
    kriteria_df = df[
        ["Hotel", "Harga_Clean", "Rating", "Star", "Reviews", "Facility_Count"]
    ].copy()
    kriteria_df.columns = [
        "Alternatif (Hotel)",
        "C1 (Harga)",
        "C2 (Rating)",
        "C3 (Star)",
        "C4 (Reviews)",
        "C5 (Fasilitas)",
    ]

    return df, kriteria_df


def calculate_normalization(df_matrix, atribut):
    """
    Melakukan Normalisasi menggunakan pendekatan NumPy
    atribut = array berisi 0 (Cost) atau 1 (Benefit)
    """
    # Ambil data angka saja
    data = df_matrix.iloc[:, 1:].values.astype(float)
    m, n = data.shape
    normalized_matrix = np.zeros((m, n))

    for j in range(n):
        if atribut[j] == 1:  # Kriteria Benefit
            normalized_matrix[:, j] = data[:, j] / np.max(data[:, j])
        else:  # Kriteria Cost
            normalized_matrix[:, j] = np.min(data[:, j]) / data[:, j]

    cols = df_matrix.columns[1:]
    df_norm = pd.DataFrame(normalized_matrix, columns=cols)
    df_norm.insert(0, "Alternatif (Hotel)", df_matrix["Alternatif (Hotel)"])

    return df_norm


def calculate_final_score(df_matrix, df_norm, bobot):
    """
    Menghitung Nilai Preferensi (V) menggunakan Dot Product (np.dot)
    """
    # Ambil matriks ternormalisasi (hanya angkanya)
    norm_data = df_norm.iloc[:, 1:].values.astype(float)
    bobot_array = np.array(bobot)

    value_preferensi = np.dot(norm_data, bobot_array)

    # Membuat DataFrame hasil akhir
    df_v = pd.DataFrame(
        {
            "Alternatif (Hotel)": df_norm["Alternatif (Hotel)"],
            "Skor Akhir": value_preferensi,
        }
    )

    # Menggabungkan skor akhir dengan matriks awal
    df_final = pd.merge(df_v, df_matrix, on="Alternatif (Hotel)")

    # Perankingan
    df_final = df_final.sort_values(by="Skor Akhir", ascending=False).reset_index(
        drop=True
    )
    df_final.index = df_final.index + 1
    df_final.index.name = "Peringkat"

    return df_final
