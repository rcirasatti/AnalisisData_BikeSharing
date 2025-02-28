import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from os import path, getcwd

sns.set(style='dark')

# Fungsi untuk membuat DataFrame analisis
def create_weekday_df(df):
    weekday_df = df.groupby(['weekday_day'])['cnt'].mean().reset_index()
    weekday_df.rename(columns={'cnt': 'avg_usage'}, inplace=True)
    return weekday_df

def create_hourly_df(df):
    hourly_df = df.groupby(['hr', 'workingday_day'])['cnt'].mean().reset_index()
    hourly_df.rename(columns={'cnt': 'avg_usage'}, inplace=True)
    return hourly_df

def create_season_df(df):
    season_df = df.groupby('season_day')['cnt'].sum().reset_index()
    season_df.rename(columns={'cnt': 'total_usage'}, inplace=True)
    return season_df

try:
    # Load data dari main_data.csv
    main_df = pd.read_csv("dashboard/main_data.csv")
    main_df['dteday'] = pd.to_datetime(main_df['dteday'])  # Konversi dteday ke datetime
    main_df.sort_values(by='dteday', inplace=True)
    main_df.reset_index(drop=True, inplace=True)

    # Filter waktu di sidebar
    img_path = path.join(getcwd(), "dashboard", "img.png")
    st.sidebar.image("dashboard/img.png", use_container_width=True)

    min_date = main_df['dteday'].min()
    max_date = main_df['dteday'].max()

    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter data berdasarkan rentang waktu
    filtered_df = main_df[(main_df['dteday'] >= pd.to_datetime(start_date)) &
                          (main_df['dteday'] <= pd.to_datetime(end_date))]

    # Buat DataFrame analisis
    weekday_df = create_weekday_df(filtered_df)
    hourly_df = create_hourly_df(filtered_df[filtered_df['season_day'] == 3])  # Fall
    season_df = create_season_df(filtered_df)

    # Header Dashboard
    st.header('Bike Sharing Dashboard :bike:')
    st.subheader(f'Key Metrics (Rentang Waktu: {start_date} hingga {end_date})')

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_usage = int(filtered_df['cnt'].sum())
        st.metric("Total Usage", value=total_usage)
    with col2:
        avg_daily_usage = int(filtered_df['cnt'].mean())
        st.metric("Average Usage", value=avg_daily_usage)
    with col3:
        peak_hour = hourly_df.loc[hourly_df['avg_usage'].idxmax(), 'hr']
        st.metric("Peak Hour (Fall)", value=f"{peak_hour}:00")

    # Visualisasi Tren Penggunaan Harian
    st.subheader(f"Tren Penggunaan Sepeda Harian ({start_date.year} - {end_date.year})")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weekday_day', y='avg_usage', data=weekday_df, palette='muted', ax=ax1)
    days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
    ax1.set_xticklabels(days, fontsize=12)
    for p in ax1.patches:
        ax1.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=12)
    ax1.set_title('Tren Penggunaan Sepeda Harian', fontsize=14)
    ax1.set_xlabel(None)
    ax1.set_ylabel('Rata-rata Penggunaan', fontsize=12)
    st.pyplot(fig1)

    # Visualisasi Pola per Jam di Fall
    st.subheader(f"Pola Penggunaan per Jam (Fall {start_date.year} - {end_date.year})")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.lineplot(x='hr', y='avg_usage', hue='workingday_day', data=hourly_df, palette='coolwarm', ax=ax2)
    ax2.set_xticks(range(24))
    ax2.set_xticklabels([f'{i:02d}' for i in range(24)], fontsize=10)
    ax2.set_title('Pola Penggunaan Sepeda per Jam (Fall)', fontsize=14)
    ax2.set_xlabel(None)
    ax2.set_ylabel('Rata-rata Penggunaan', fontsize=12)
    ax2.legend(title='Hari Kerja', loc='upper right')
    st.pyplot(fig2)

    # Visualisasi Total Penggunaan per Musim
    st.subheader(f"Total Penggunaan Sepeda per Musim ({start_date.year} - {end_date.year})")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]  # Biru, Oranye, Hijau, Merah
    sns.barplot(y='total_usage', x='season_day', data=season_df.sort_values(by='total_usage', ascending=False),
                palette=colors, ax=ax3)
    seasons = ['Springer', 'Summer', 'Fall', 'Winter']
    ax3.set_xticks(range(4))
    ax3.set_xticklabels(seasons, fontsize=12)
    ax3.set_title('Total Penggunaan Sepeda per Musim', fontsize=15)
    ax3.set_xlabel(None)
    ax3.set_ylabel('Total Penggunaan', fontsize=12)
    for index, row in season_df.iterrows():
        ax3.text(x=index, y=row["total_usage"] + 5000, s=f"{int(row['total_usage'])}", ha="center", va="bottom", fontsize=12)
    st.pyplot(fig3)

    # Copyright
    st.caption(f'Copyright (c) 2025 Rucirasatti N.')

except FileNotFoundError:
    st.error("File 'main_data.csv' tidak ditemukan. Pastikan file ada di direktori yang benar.")
except Exception as e:
    st.error(f"Terjadi kesalahan: {str(e)}")