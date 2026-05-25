# 🏨 Intelligent Decision Support System for Hotel Selection in Bali

This repository contains the final project for the **Intelligent Systems and Decision Support Practicum** (Plug H). This application is a web-based Decision Support System (DSS) built using **Streamlit**, implementing the **Simple Additive Weighting (SAW)** method to provide the best hotel recommendations in Bali using real scraped data from the Tiket.com platform.

---

## 👥 Team Identity (Plug-H)
This project was developed by:
* **Adhafa Joan Putranto** (123240069) — [adhafajp](https://github.com/adhafajp)
* **Muhammad Farelino Kelfin** (123240205) — [kelfinofarelino](https://github.com/kelfinofarelino)

---

## ✨ Main Features
This DSS application is equipped with an interactive web-based Graphical User Interface (GUI) featuring the following highlights:

* **Structured Layout Navigation (Tabs):** Neatly separates the data processing workflow into 5 pages (*Team Profile, Initial Matrix X, Normalization R, Ranking Results V, and Visualization*).
* **Interactive Dataset Display:** Presents raw hotel data and matrix calculation results in dynamic tables that can be sorted or expanded using `st.dataframe`.
* **Dynamic Weight Input:** Users can adjust weight proportions for 5 different criteria via interactive sidebar components (a combination of `st.slider` and `st.number_input`), complete with a validation system requiring the total weight to equal exactly 100.
* **Manual Execution (*On-Demand*):** The SAW mathematical calculation is bound to an execution button (`st.button`). The calculation only runs when the button is pressed, saving memory resources and preventing heavy automatic recalculations every time a weight is adjusted.
* **Ranking Visualization:** Displays an interactive Bar Chart comparing the final preference scores of the **Top 15 Best Hotels** in Bali.
* **Robust Data Cleaning Mechanism:** The code is equipped with automatic handling for hidden characters (*Byte Order Mark* via `utf-8-sig`), keyword-based column detection (*fuzzy matching*), and automatic conversion of local comma decimals (`,`) to dots (`.`) to ensure seamless mathematical processing by Python.

---

## 💾 Dataset Link
The dataset used in this system was obtained from Kaggle:
* **Source:** [Hotel Listings in Bali (Scraped Data from Tiket.com)](https://www.kaggle.com/datasets/anisyanugraheni/hotel-listings-in-bali-scraped-data)
* **File Name:** `Updated_ScrapingHotelTiketcom.csv` (Includes actual hotel names along with their price parameters).

---

## 📊 Assessment Criteria (SAW)
This system utilizes 5 main criteria to determine the utility value of the hotels:
1. **C1 - Price (*Price Starts From*):** *Cost* attribute (The cheaper the room rate, the better).
2. **C2 - Rating:** *Benefit* attribute (The higher the guest rating score, the better).
3. **C3 - Star:** *Benefit* attribute (The higher the hotel's star classification, the better).
4. **C4 - Number of Reviews (*Review Count*):** *Benefit* attribute (A higher number of reviews indicates better hotel credibility).
5. **C5 - Facilities:** *Benefit* attribute (The system dynamically calculates the total number of available facilities from the text data. The more comprehensive the facilities, the better).

---

## 🛠️ Technologies Used
* **Programming Language:** Python 3.12+
* **GUI Framework:** Streamlit
* **Data Analysis Libraries:** Pandas, NumPy

---