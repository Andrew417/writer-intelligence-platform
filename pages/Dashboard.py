import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
from components.styles import inject_styles
from components.data import get_all_genres, get_all_books, get_total_reviews_count, get_global_market_mood

inject_styles()

try:
    genres_df = get_all_genres()
    books_df = get_all_books()
    exact_review_count = get_total_reviews_count()
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

total_books = len(books_df) if not books_df.empty else 0
genres_tracked = len(genres_df) if not genres_df.empty else 0


def format_large_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(int(num))


formatted_reviews = format_large_number(exact_review_count)

# --- GLOBAL MARKET MOOD (from pre-computed market_trends collection) ---
market_mood_doc = get_global_market_mood()
primary_mood = market_mood_doc.get("market_mood", "unknown").capitalize()


# ═══════════════════════════════════════════════════════════
# Build Trending Now leaderboard (clickable links)
# ═══════════════════════════════════════════════════════════
def build_leaderboard_html(df, sort_col, badge_text, badge_color_class, icon):
    html = ""
    top_4 = df.nlargest(4, sort_col) if sort_col in df.columns else pd.DataFrame()
    for _, row in top_4.iterrows():
        title = row.get('title', 'Unknown Title')
        author = row.get('author', 'Unknown Author')
        book_id = row.get('book_id', '')
        score = row.get(sort_col, 0)
        display_score = f"{score:.2f}"

        # Build URL with book_id parameter
        # Build URL with book_id parameter
        book_link = f"./Book_Insights?book_id={book_id}" if book_id else ""

        html += f"""
        <div onclick="window.parent.location.href='{book_link}'" 
            class="p-4 hover:bg-slate-50 transition-colors cursor-pointer" 
            style="cursor:pointer;">
            <p class="text-sm font-semibold text-slate-900 truncate hover:text-rose-600 transition-colors" title="{title}">{title}</p>
            <p class="text-[11px] text-slate-500 mb-2 truncate">{author}</p>
            <div class="flex justify-between items-center">
                <span class="text-[10px] {badge_color_class} px-1.5 py-0.5 rounded font-mono font-bold uppercase">{badge_text}: {display_score}</span>
                <span class="material-symbols-outlined {badge_color_class.split(' ')[1].replace('bg-', 'text-')} text-sm">{icon}</span>
            </div>
        </div>
"""
    return html


# ═══════════════════════════════════════════════════════════
# Build Hidden Gems leaderboard (clickable, ranked)
# ═══════════════════════════════════════════════════════════
def build_hidden_gems_html(df):
    html = ""

    # Filter to only books flagged as hidden gems
    if 'hidden_gem_flag' in df.columns:
        gems_df = df[df['hidden_gem_flag'] == True].copy()
    else:
        gems_df = pd.DataFrame()

    if gems_df.empty:
        return '<div class="p-4 text-center text-slate-500 text-sm">No hidden gems found.</div>'

    # Sort by high satisfaction + low rating count
    def compute_score(row):
        sat = row.get('true_satisfaction', 0) or 0
        rc = row.get('rating_count', 0) or 0
        if rc <= 0:
            return 0
        popularity_penalty = 1 / np.log10(rc + 10)
        return sat * popularity_penalty

    gems_df['gem_rank_score'] = gems_df.apply(compute_score, axis=1)
    top_4 = gems_df.nlargest(4, 'gem_rank_score')

    for idx, (_, row) in enumerate(top_4.iterrows(), 1):
        title = row.get('title', 'Unknown Title')
        author = row.get('author', 'Unknown Author')
        book_id = row.get('book_id', '')
        satisfaction = row.get('true_satisfaction', 0) or 0
        rating_count = row.get('rating_count', 0) or 0

        # Format rating count
        if rating_count >= 1_000_000:
            rc_display = f"{rating_count/1_000_000:.1f}M"
        elif rating_count >= 1_000:
            rc_display = f"{rating_count/1_000:.1f}K"
        else:
            rc_display = f"{int(rating_count)}"

        book_link = f"./Book_Insights?book_id={book_id}" if book_id else ""

        html += f"""
        <div onclick="window.parent.location.href='{book_link}'" 
            class="p-4 hover:bg-slate-50 transition-colors cursor-pointer" 
            style="cursor:pointer;">
            <div class="flex items-start gap-3 mb-2">
                <span class="flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-full bg-indigo-600 text-white text-xs font-bold">
                    {idx}
                </span>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-slate-900 truncate hover:text-indigo-600 transition-colors" title="{title}">{title}</p>
                    <p class="text-[11px] text-slate-500 truncate">{author}</p>
                </div>
            </div>
            <div class="flex justify-between items-center pl-10">
                <div class="flex items-center gap-2 text-[11px]">
                    <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-bold flex items-center gap-1">
                        💯 {satisfaction*100:.0f}% satisfied
                    </span>
                    <span class="bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                        {rc_display} ratings
                    </span>
                </div>
                <span class="material-symbols-outlined text-indigo-600 text-sm">verified</span>
            </div>
        </div>
        """
    return html


# ═══════════════════════════════════════════════════════════
# Build leaderboards (now AFTER both functions are defined)
# ═══════════════════════════════════════════════════════════
trending_html = build_leaderboard_html(
    books_df, 'viral_potential_score',
    "Viral Score", "bg-rose-100 text-rose-700", "trending_up"
)
hidden_gems_html = build_hidden_gems_html(books_df)


# ═══════════════════════════════════════════════════════════
# Render the dashboard
# ═══════════════════════════════════════════════════════════
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

            <div class="mb-8 flex justify-between items-start flex-wrap gap-3">
                <div>
                    <h2 class="text-3xl font-bold text-text-primary">Global Dashboard</h2>
                    <p class="text-text-muted mt-1">Real-time literary performance and reader sentiment indices.</p>
                </div>
                <span class="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-bold uppercase tracking-wide border border-primary/20">
                    <span class="material-symbols-outlined text-[18px]">psychology</span>
                    Current Market Mood: {primary_mood}
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg"><span class="material-symbols-outlined">library_books</span></div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Total Books Analyzed</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{total_books:,}</h3>
                </div>
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><span class="material-symbols-outlined">forum</span></div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Reviews Analyzed</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{formatted_reviews}</h3>
                </div>
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-amber-50 text-amber-600 rounded-lg"><span class="material-symbols-outlined">category</span></div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Genres Tracked</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{genres_tracked}</h3>
                </div>
            </div>

            <h2 class="text-xl font-semibold mb-5 flex items-center gap-3">Industry Leaderboards <span class="h-[1px] flex-1 bg-slate-200"></span></h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div class="bg-white rounded-xl border border-border shadow-sm overflow-hidden border-t-4 border-t-rose-500">
                    <div class="p-4 border-b border-slate-100 bg-rose-50/30 flex justify-between items-center">
                        <h5 class="font-semibold text-rose-700 flex items-center gap-2"><span class="material-symbols-outlined text-[20px]">bolt</span> Trending Now</h5>
                        <span class="text-[10px] uppercase font-bold text-rose-400">Viral Spike</span>
                    </div>
                    <div class="divide-y divide-slate-50">{trending_html}</div>
                </div>
                <div class="bg-white rounded-xl border border-border shadow-sm overflow-hidden border-t-4 border-t-indigo-500">
                    <div class="p-4 border-b border-slate-100 bg-indigo-50/30 flex justify-between items-center">
                        <h5 class="font-semibold text-indigo-700 flex items-center gap-2"><span class="material-symbols-outlined text-[20px]">diamond</span> Hidden Gems</h5>
                        <span class="text-[10px] uppercase font-bold text-indigo-400">Under Valued</span>
                    </div>
                    <div class="divide-y divide-slate-50">{hidden_gems_html}</div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"""

components.html(html_ui, height=1000, scrolling=True)