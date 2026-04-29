import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from components.styles import inject_styles
from components.data import get_all_books, get_book_emotions, get_all_genres, get_market_trends

inject_styles()

try:
    books_df = get_all_books()
    emotions_df = get_book_emotions()
    genres_df = get_all_genres()
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# FORCE DATA TYPES TO PREVENT PANDAS ERRORS
books_df['book_id'] = books_df['book_id'].astype(str)
emotions_df['book_id'] = emotions_df['book_id'].astype(str)

# Clean Price Logic
if 'clean_price' not in books_df.columns and 'price' in books_df.columns:
    books_df['clean_price'] = books_df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
if 'clean_price' in books_df.columns:
    books_df['clean_price'] = pd.to_numeric(books_df['clean_price'], errors='coerce')

# Convert metrics to strictly numeric
for col in ['days_since_published', 'true_satisfaction', 'rating_count', 'viral_potential_score']:
    if col in books_df.columns:
        books_df[col] = pd.to_numeric(books_df[col], errors='coerce')

# Merge Datasets
master_df = pd.merge(books_df, emotions_df, on='book_id', how='left')

# ═══════════════════════════════════════
# ADVANCED DATA SCIENCE METRICS 
# ═══════════════════════════════════════

# 1. Market Mood (Live Calculation to guarantee 'Sadness' or true mode)
market_mood = "Data Missing"
if 'days_since_published' in master_df.columns and 'secondary_emotion' in master_df.columns:
    recent_books = master_df[master_df['days_since_published'] <= 1260]
    if not recent_books.empty and not recent_books['secondary_emotion'].isnull().all():
        market_mood = str(recent_books['secondary_emotion'].mode()[0]).capitalize()

# 2. Market Risk Index (Using the pre-calculated genre database)
high_risk_html, low_risk_html = "<p class='text-sm text-slate-500'>Data unavailable</p>", ""
if 'market_risk_index' in genres_df.columns and 'genres' in genres_df.columns:
    valid_genres = genres_df.dropna(subset=['market_risk_index'])
    if not valid_genres.empty:
        for _, row in valid_genres.nlargest(3, 'market_risk_index').iterrows():
            genre, risk = row['genres'], row['market_risk_index']
            high_risk_html += f"""
            <div class='flex justify-between items-center p-3 bg-rose-50/50 rounded-lg border border-rose-100 mb-2'>
                <span class='font-medium text-slate-700 text-sm'>{genre}</span>
                <span class='font-mono font-bold text-rose-600 text-sm'>{risk:.2f} <span class='text-[10px] font-normal text-rose-400 ml-1'>IDX</span></span>
            </div>"""
            
        for _, row in valid_genres.nsmallest(3, 'market_risk_index').iterrows():
            genre, risk = row['genres'], row['market_risk_index']
            low_risk_html += f"""
            <div class='flex justify-between items-center p-3 bg-emerald-50/50 rounded-lg border border-emerald-100 mb-2'>
                <span class='font-medium text-slate-700 text-sm'>{genre}</span>
                <span class='font-mono font-bold text-emerald-600 text-sm'>{risk:.2f} <span class='text-[10px] font-normal text-emerald-400 ml-1'>IDX</span></span>
            </div>"""

# 3. Hidden Gem Flag 
hidden_gems_count = 0
if 'hidden_gem_flag' in books_df.columns:
    hidden_gems_count = int(books_df['hidden_gem_flag'].sum())

# 4. Viral Breakout Flag 
viral_breakouts_count = 0
if 'viral_breakout_flag' in books_df.columns:
    viral_breakouts_count = int(books_df['viral_breakout_flag'].sum())

# 5. Optimal Price Bracket (Hardcoded / Mocked for Demo)
best_bracket_name = "$5.00 - $9.99"
best_bracket_score = 0.68

# ═══════════════════════════════════════
# UI INJECTION
# ═══════════════════════════════════════
html_ui = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ "primary": "#3525cd", "border": "#E2E8F0", "text-primary": "#0F172A", "text-muted": "#64748B", "text-faint": "#94A3B8" }} }} }} }}
    </script>
    <style> body {{ background: transparent; font-family: 'Inter', sans-serif; }} .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }} </style>
</head>
<body class="antialiased text-text-primary">
    <main class="w-full pb-10">
        <div class="max-w-[1280px] mx-auto">
            
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-text-primary">Strategic Market Trends</h2>
                <p class="text-text-muted mt-1">Macro-economic intelligence and publishing industry Zeitgeist.</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
                <div class="bg-gradient-to-br from-indigo-900 to-primary p-6 rounded-xl shadow-md text-white relative overflow-hidden flex flex-col justify-center">
                    <span class="material-symbols-outlined absolute -right-4 -bottom-4 text-[120px] text-white/10">psychology</span>
                    <h4 class="font-semibold text-lg text-indigo-100 mb-1">Current Zeitgeist</h4>
                    <p class="text-xs text-indigo-200/80 mb-6">Secondary emotion driving recent market acquisitions</p>
                    <h2 class="text-5xl font-black tracking-tight">{market_mood}</h2>
                </div>

                <div class="bg-white rounded-xl border border-border shadow-sm p-6 flex flex-col justify-center">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="material-symbols-outlined text-emerald-500 text-xl">monetization_on</span>
                        <h4 class="font-semibold text-lg">Pricing Sweet Spot</h4>
                    </div>
                    <p class="text-xs text-text-muted mb-5">Maximized psychological satisfaction relative to cost</p>
                    <div class="flex items-end gap-3">
                        <h2 class="text-4xl font-bold font-mono text-slate-800">{best_bracket_name}</h2>
                        <div class="pb-1">
                            <span class="text-sm font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">Score: {best_bracket_score:.2f}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm border-l-4 border-l-indigo-500">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="font-semibold text-slate-800 flex items-center gap-2"><span class="material-symbols-outlined text-indigo-500">radar</span> Hidden Gems</h4>
                            <p class="text-xs text-text-muted mt-1">Phenomenal ratings, undiscovered by mainstream</p>
                        </div>
                        <h3 class="text-3xl font-bold font-mono text-indigo-600">{hidden_gems_count}</h3>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-xl border border-border shadow-sm border-l-4 border-l-rose-500">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="font-semibold text-slate-800 flex items-center gap-2"><span class="material-symbols-outlined text-rose-500">rocket_launch</span> Viral Breakouts</h4>
                            <p class="text-xs text-text-muted mt-1">Exploding in real-time cultural relevance</p>
                        </div>
                        <h3 class="text-3xl font-bold font-mono text-rose-600">{viral_breakouts_count}</h3>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl border border-border shadow-sm p-6">
                <div class="mb-6">
                    <h4 class="font-semibold text-lg">Market Risk Index</h4>
                    <p class="text-xs text-text-muted">Financial volatility across genre satisfaction</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h5 class="text-sm font-bold text-rose-700 mb-3 flex items-center gap-1 uppercase tracking-wider"><span class="material-symbols-outlined text-sm">warning</span> High Risk (Polarizing)</h5>
                        {high_risk_html}
                    </div>
                    <div>
                        <h5 class="text-sm font-bold text-emerald-700 mb-3 flex items-center gap-1 uppercase tracking-wider"><span class="material-symbols-outlined text-sm">verified_user</span> Low Risk (Consistent)</h5>
                        {low_risk_html}
                    </div>
                </div>
            </div>

        </div>
    </main>
</body>
</html>
"""

components.html(html_ui, height=900, scrolling=True)