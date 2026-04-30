import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
from components.styles import inject_styles
from components.data import get_all_books, get_book_emotions, get_all_genres, get_market_trends

inject_styles()

try:
    books_df = get_all_books()
    emotions_df = get_book_emotions()
    genres_df = get_all_genres()
    market_trends_df = get_market_trends()
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# Data preparation
books_df['book_id'] = books_df['book_id'].astype(str)
emotions_df['book_id'] = emotions_df['book_id'].astype(str)

if 'clean_price' not in books_df.columns and 'price' in books_df.columns:
    books_df['clean_price'] = books_df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
if 'clean_price' in books_df.columns:
    books_df['clean_price'] = pd.to_numeric(books_df['clean_price'], errors='coerce')

for col in ['days_since_published', 'true_satisfaction', 'rating_count', 'viral_potential_score']:
    if col in books_df.columns:
        books_df[col] = pd.to_numeric(books_df[col], errors='coerce')

master_df = pd.merge(books_df, emotions_df, on='book_id', how='left')

# --- Metrics ---
# Market Mood
market_mood = "Data Missing"
if 'days_since_published' in master_df.columns and 'secondary_emotion' in master_df.columns:
    recent_books = master_df[master_df['days_since_published'] <= 1260]
    if not recent_books.empty and not recent_books['secondary_emotion'].isnull().all():
        market_mood = str(recent_books['secondary_emotion'].mode()[0]).capitalize()

# Market Risk Index HTML
high_risk_html = "<p class='text-sm text-slate-500'>Data unavailable</p>"
low_risk_html = ""
if 'market_risk_index' in genres_df.columns and 'genres' in genres_df.columns:
    valid_genres = genres_df.dropna(subset=['market_risk_index'])
    if not valid_genres.empty:
        high_risk_html = ""
        for _, row in valid_genres.nlargest(3, 'market_risk_index').iterrows():
            genre, risk = row['genres'], row['market_risk_index']
            high_risk_html += f"""
            <div class='flex justify-between items-center p-3 bg-rose-50/50 rounded-lg border border-rose-100 mb-2'>
                <span class='font-medium text-slate-700 text-sm'>{genre}</span>
                <span class='font-mono font-bold text-rose-600 text-sm'>{risk:.2f} <span class='text-[10px] font-normal text-rose-400 ml-1'>IDX</span></span>
            </div>"""
        low_risk_html = ""
        for _, row in valid_genres.nsmallest(3, 'market_risk_index').iterrows():
            genre, risk = row['genres'], row['market_risk_index']
            low_risk_html += f"""
            <div class='flex justify-between items-center p-3 bg-emerald-50/50 rounded-lg border border-emerald-100 mb-2'>
                <span class='font-medium text-slate-700 text-sm'>{genre}</span>
                <span class='font-mono font-bold text-emerald-600 text-sm'>{risk:.2f} <span class='text-[10px] font-normal text-emerald-400 ml-1'>IDX</span></span>
            </div>"""

# Hidden Gems & Viral Breakouts
hidden_gems_count = int(books_df['hidden_gem_flag'].sum()) if 'hidden_gem_flag' in books_df.columns else 0
viral_breakouts_count = int(books_df['viral_breakout_flag'].sum()) if 'viral_breakout_flag' in books_df.columns else 0

# Pricing Sweet Spot (dynamic from market_trends)
best_bracket_name = "No data"
best_bracket_score = 0.0
if not market_trends_df.empty and 'trend_type' in market_trends_df.columns:
    pricing_data = market_trends_df[market_trends_df['trend_type'] == 'pricing_bracket'].copy()
    if not pricing_data.empty:
        if 'avg_satisfaction' in pricing_data.columns:
            pricing_data['avg_satisfaction'] = pd.to_numeric(pricing_data['avg_satisfaction'], errors='coerce')
            best_idx = pricing_data['avg_satisfaction'].idxmax()
            best_bracket_name = pricing_data.loc[best_idx, 'bracket_name']
            best_bracket_score = pricing_data.loc[best_idx, 'avg_satisfaction']
        elif 'avg_engagement_depth' in pricing_data.columns:
            pricing_data['avg_engagement_depth'] = pd.to_numeric(pricing_data['avg_engagement_depth'], errors='coerce')
            best_idx = pricing_data['avg_engagement_depth'].idxmax()
            best_bracket_name = pricing_data.loc[best_idx, 'bracket_name']
            best_bracket_score = pricing_data.loc[best_idx, 'avg_engagement_depth']

# =============================================================================
# 🔍 DEBUG EXPANDER – shows raw data used for all metrics
# =============================================================================
# with st.expander("🔍 Debug: Raw Data Sources (Visible only for verification)", expanded=False):
#     st.markdown("### Market Mood Calculation")
#     st.write(f"**Recent books (≤1260 days) secondary_emotion mode →** `{market_mood}`")
#     if 'days_since_published' in master_df.columns and 'secondary_emotion' in master_df.columns:
#         recent_sample = master_df[master_df['days_since_published'] <= 1260][['title', 'secondary_emotion', 'days_since_published']].head(10)
#         st.dataframe(recent_sample)

#     st.markdown("### Pricing Sweet Spot (from `market_trends` table)")
#     if not market_trends_df.empty:
#         pricing_data_raw = market_trends_df[market_trends_df['trend_type'] == 'pricing_bracket']
#         st.dataframe(pricing_data_raw[['bracket_name', 'avg_satisfaction', 'avg_engagement_depth', 'total_books_in_bracket']])
#         st.write(f"**Selected bracket:** `{best_bracket_name}` (score `{best_bracket_score:.2f}`)")
#     else:
#         st.write("No market_trends data available.")

#     st.markdown("### Hidden Gems (top 5 by value)")
#     if 'hidden_gem_flag' in books_df.columns:
#         gems = books_df[books_df['hidden_gem_flag'] == True].nlargest(5, 'normalized_bang_for_buck')
#         st.dataframe(gems[['title', 'author', 'normalized_bang_for_buck']])
#         st.write(f"**Total Hidden Gems count:** `{hidden_gems_count}`")

#     st.markdown("### Viral Breakouts (top 5 by viral score)")
#     if 'viral_breakout_flag' in books_df.columns:
#         breakouts = books_df[books_df['viral_breakout_flag'] == True].nlargest(5, 'viral_potential_score')
#         st.dataframe(breakouts[['title', 'author', 'viral_potential_score']])
#         st.write(f"**Total Viral Breakouts count:** `{viral_breakouts_count}`")

#     st.markdown("### Market Risk Index (top 10 highest risk genres)")
#     if 'market_risk_index' in genres_df.columns:
#         risk_df = genres_df[['genres', 'market_risk_index']].dropna().sort_values('market_risk_index', ascending=False)
#         st.dataframe(risk_df.head(10))
#         st.write("**High Risk (top 3):**")
#         st.write(risk_df.head(3))
#         st.write("**Low Risk (bottom 3):**")
#         st.write(risk_df.tail(3))

# =============================================================================

# --- Load HTML template (corrected path) ---
template_path = Path(__file__).parent.parent / "files as html" / "market_analysis.html"
try:
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()
except FileNotFoundError:
    st.error(f"Template file not found at {template_path}")
    st.stop()

# Fill placeholders
html_ui = html_template.format(
    market_mood=market_mood,
    best_bracket_name=best_bracket_name,
    best_bracket_score=best_bracket_score,
    hidden_gems_count=hidden_gems_count,
    viral_breakouts_count=viral_breakouts_count,
    high_risk_html=high_risk_html,
    low_risk_html=low_risk_html
)

components.html(html_ui, height=900, scrolling=True)