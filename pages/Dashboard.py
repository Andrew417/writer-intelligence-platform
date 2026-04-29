import streamlit as st
import streamlit.components.v1 as components
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


def build_leaderboard_html(df, sort_col, badge_text, badge_color_class, icon):
    html = ""
    top_4 = df.nlargest(4, sort_col) if sort_col in df.columns else pd.DataFrame()
    for _, row in top_4.iterrows():
        title = row.get('title', 'Unknown Title')
        author = row.get('author', 'Unknown Author')
        score = row.get(sort_col, 0)
        display_score = f"{score:.2f}" 
        html += f"""
        <div class="p-4 hover:bg-slate-50 transition-colors">
            <p class="text-sm font-semibold text-slate-900 truncate" title="{title}">{title}</p>
            <p class="text-[11px] text-slate-500 mb-2 truncate">{author}</p>
            <div class="flex justify-between items-center">
                <span class="text-[10px] {badge_color_class} px-1.5 py-0.5 rounded font-mono font-bold uppercase">{badge_text}: {display_score}</span>
                <span class="material-symbols-outlined {badge_color_class.split(' ')[1].replace('bg-', 'text-')} text-sm">{icon}</span>
            </div>
        </div>
        """
    return html

trending_html = build_leaderboard_html(books_df, 'viral_potential_score', "Viral Score", "bg-rose-100 text-rose-700", "trending_up")
hidden_gems_html = build_leaderboard_html(books_df, 'normalized_bang_for_buck', "Value Score", "bg-indigo-100 text-indigo-700", "verified")

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
    <div class="relative inline-flex items-center gap-3 px-5 py-2.5 rounded-full overflow-hidden backdrop-blur-sm" style="background: linear-gradient(135deg, rgba(53,37,205,0.08) 0%, rgba(124,58,237,0.08) 100%); border: 1px solid rgba(53,37,205,0.2);">
    <div class="flex items-center justify-center w-7 h-7 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full shadow-lg shadow-indigo-500/30">
        <span class="material-symbols-outlined text-white text-[16px]">insights</span>
    </div>
    <div class="flex items-baseline gap-2">
        <span class="text-[10px] font-bold uppercase tracking-widest text-indigo-500/80">Market Mood</span>
        <span class="text-base font-extrabold bg-gradient-to-r from-indigo-700 to-purple-700 bg-clip-text text-transparent">{primary_mood}</span>
    </div>
</div>
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