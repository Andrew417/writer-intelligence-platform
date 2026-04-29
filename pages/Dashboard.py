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

primary_mood = market_mood_doc.get("market_mood", "unknown").lower()
books_analyzed_mood = market_mood_doc.get("books_analyzed", 0)
lookback_days = market_mood_doc.get("lookback_days", 0)

# Compute emotion shares from genre averages (consistent math for all bars)
emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise']
mean_emotions = {}
for emo in emotions:
    col_name = f'avg_{emo}'
    if col_name in genres_df.columns:
        mean_emotions[emo] = genres_df[col_name].mean()

total_emo_score = sum(mean_emotions.values()) if mean_emotions else 0

emotion_pcts = {}
if total_emo_score > 0:
    for emo, val in mean_emotions.items():
        emotion_pcts[emo] = (val / total_emo_score) * 100

# Build all 5 emotion bars with primary highlighted
emotion_meta = {
    'joy':      ('bg-amber-400',  'text-amber-700',  '😊'),
    'sadness':  ('bg-blue-500',   'text-blue-700',   '😢'),
    'anger':    ('bg-red-500',    'text-red-700',    '😠'),
    'fear':     ('bg-purple-500', 'text-purple-700', '😨'),
    'surprise': ('bg-pink-500',   'text-pink-700',   '😲'),
}

sorted_all_emotions = sorted(emotion_pcts.items(), key=lambda x: x[1], reverse=True)

emotion_bars_html = ""
for emo_name, emo_pct in sorted_all_emotions:
    is_primary = (emo_name == primary_mood)
    bar_color, text_color, emoji = emotion_meta.get(emo_name, ('bg-slate-400', 'text-slate-700', '•'))
    
    if is_primary:
        label_class = "font-semibold text-slate-900 text-sm"
        pct_class = f"text-sm font-mono font-bold {text_color}"
        bar_height = "h-3"
        bar_bg = bar_color
        primary_badge = '<span class="ml-2 text-[9px] font-bold uppercase tracking-wider text-white bg-primary px-1.5 py-0.5 rounded">⬆ TRENDING</span>'
    else:
        label_class = "text-sm text-slate-600"
        pct_class = "text-sm font-mono text-slate-500"
        bar_height = "h-2"
        bar_bg = "bg-slate-300"
        primary_badge = ""
    
    emotion_bars_html += f"""
        <div>
            <div class="flex justify-between items-center mb-1.5">
                <span class="{label_class} flex items-center gap-2">
                    <span>{emoji}</span> {emo_name.capitalize()} {primary_badge}
                </span>
                <span class="{pct_class}">{emo_pct:.1f}%</span>
            </div>
            <div class="{bar_height} bg-slate-100 rounded-full overflow-hidden">
                <div class="h-full {bar_bg} rounded-full transition-all duration-500" style="width: {emo_pct}%"></div>
            </div>
        </div>
    """

primary_mood_display = primary_mood.capitalize()

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
            
            <div class="mb-8">
                <h2 class="text-3xl font-bold text-text-primary">Global Dashboard</h2>
                <p class="text-text-muted mt-1">Real-time literary performance and reader sentiment indices.</p>
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

            <div class="grid grid-cols-1 gap-5 mb-8">
                <div class="bg-white rounded-xl border border-border shadow-sm p-6 relative overflow-hidden">
                    <div class="flex justify-between items-start mb-6">
                        <div>
                        <div class="flex items-center gap-3 mb-1">
    <h4 class="font-semibold text-lg">Sentiment Landscape</h4>
    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 bg-primary/10 text-primary rounded-full text-xs font-bold uppercase tracking-wide">
        <span class="material-symbols-outlined text-[14px]">trending_up</span>
        Trending: {primary_mood_display}
    </span>
</div>
<p class="text-xs text-text-muted">
    📊 Bars show overall emotion distribution across all 98 genres &nbsp;•&nbsp; 
    🎯 <strong>{primary_mood_display}</strong> is the rising market mood from {books_analyzed_mood} recent books ({lookback_days} days)
</p>
                        </div>
                        <span class="material-symbols-outlined text-text-faint">insights</span>
                    </div>
                    <div class="space-y-4">
                        {emotion_bars_html}
                    </div>
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