import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from components.styles import inject_styles
from components.data import get_all_genres, get_all_books
# ═══════════════════════════════════════
# 1. INITIALIZATION & SETUP
# ═══════════════════════════════════════
inject_styles()

# ═══════════════════════════════════════
# 2. FETCH DATA FROM MONGODB
# ═══════════════════════════════════════
# Fetching from the database exactly as your teammate set it up
try:
    genres_df = get_all_genres()
    books_df = get_all_books()
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

# ═══════════════════════════════════════
# 3. CALCULATE DASHBOARD METRICS
# ═══════════════════════════════════════
# Top KPIs
total_books = len(books_df) if not books_df.empty else 0
total_reviews = books_df['reviews'].sum() if 'reviews' in books_df.columns else 0
genres_tracked = len(genres_df) if not genres_df.empty else 0

# Format large numbers for the UI (e.g., 2,400,000 -> 2.4M)
def format_large_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(int(num))

formatted_reviews = format_large_number(total_reviews)

# Global Satisfaction (Assume a 5-star scale normalized to 0-1.0)
avg_rating = books_df['rating'].mean() if 'rating' in books_df.columns else 3.4
global_satisfaction = avg_rating / 5.0
circle_offset = 364.4 - (364.4 * global_satisfaction) # Math for the SVG circle animation

# ═══════════════════════════════════════
# 4. GENERATE LEADERBOARD ROWS
# ═══════════════════════════════════════
# Helper function to generate HTML rows for the leaderboards
def build_leaderboard_html(df, sort_col, badge_text, badge_color_class, icon):
    html = ""
    top_4 = df.nlargest(4, sort_col) if sort_col in df.columns else pd.DataFrame()
    for _, row in top_4.iterrows():
        title = row.get('title', 'Unknown')
        author = row.get('author', 'Unknown')
        score = row.get(sort_col, 0)
        
        # Adjust formatting based on the column
        display_score = f"{score:.2f}" if score < 10 else f"{score:.0f}"

        html += f"""
        <div class="p-4 hover:bg-slate-50 transition-colors">
            <p class="text-sm font-semibold text-slate-900">{title}</p>
            <p class="text-[11px] text-slate-500 mb-2">{author}</p>
            <div class="flex justify-between items-center">
                <span class="text-[10px] {badge_color_class} px-1.5 py-0.5 rounded font-mono font-bold uppercase">{badge_text}: {display_score}</span>
                <span class="material-symbols-outlined {badge_color_class.split(' ')[1].replace('bg-', 'text-')} text-sm">{icon}</span>
            </div>
        </div>
        """
    return html

# Ensure we have the fallback columns to prevent crashes if DB schema varies slightly
viral_col = 'viral' if 'viral' in books_df.columns else 'rating'
hgi_col = 'HGI' if 'HGI' in books_df.columns else 'rating'

trending_html = build_leaderboard_html(books_df, viral_col, "Viral Score", "bg-rose-100 text-rose-700", "trending_up")
hall_of_fame_html = build_leaderboard_html(books_df, 'rating', "Rating", "bg-amber-100 text-amber-700", "star")
hidden_gems_html = build_leaderboard_html(books_df, hgi_col, "HGI Score", "bg-indigo-100 text-indigo-700", "verified")

# ═══════════════════════════════════════
# 5. INJECT GOOGLE STITCH UI
# ═══════════════════════════════════════
html_ui = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        "primary": "#3525cd",
                        "border": "#E2E8F0",
                        "success-text": "#065F46",
                        "success-subtle": "#D1FAE5",
                        "text-primary": "#0F172A",
                        "text-muted": "#64748B",
                        "text-faint": "#94A3B8"
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ background: transparent; font-family: 'Inter', sans-serif; }}
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }}
    </style>
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
                        <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                            <span class="material-symbols-outlined">library_books</span>
                        </div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Total Books Analyzed</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{total_books:,}</h3>
                </div>
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                            <span class="material-symbols-outlined">forum</span>
                        </div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Total Reader Reviews</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{formatted_reviews}</h3>
                </div>
                <div class="bg-white p-6 rounded-xl border border-border shadow-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-amber-50 text-amber-600 rounded-lg">
                            <span class="material-symbols-outlined">category</span>
                        </div>
                    </div>
                    <p class="text-text-muted text-xs uppercase tracking-wider font-semibold">Genres Tracked</p>
                    <h3 class="text-3xl font-bold font-mono mt-1">{genres_tracked}</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
                <div class="bg-white rounded-xl border border-border shadow-sm p-6 relative overflow-hidden group">
                    <div class="flex justify-between items-center mb-6">
                        <div>
                            <h4 class="font-semibold text-lg">Current Market Mood</h4>
                            <p class="text-xs text-text-muted">Primary sentiment drivers across all platforms</p>
                        </div>
                        <span class="material-symbols-outlined text-text-faint group-hover:text-primary transition-colors">trending_up</span>
                    </div>
                    <div class="space-y-6">
                        <div class="flex items-center gap-4">
                            <div class="flex-1">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="font-medium text-slate-700">Joy & Surprise</span>
                                    <span class="text-sm font-mono font-bold text-primary">82%</span>
                                </div>
                                <div class="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-primary rounded-full w-[82%]"></div>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-4">
                            <div class="flex-1">
                                <div class="flex justify-between items-center mb-2 text-text-muted">
                                    <span class="text-sm">Anticipation</span>
                                    <span class="text-sm font-mono">64%</span>
                                </div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-slate-300 rounded-full w-[64%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-xl border border-border shadow-sm p-6 flex items-center gap-8 group">
                    <div class="flex-1">
                        <h4 class="font-semibold text-lg mb-1">Global Market Satisfaction</h4>
                        <p class="text-xs text-text-muted mb-6">Aggregate satisfaction score normalized (0-1.0)</p>
                        <div class="flex items-baseline gap-2">
                            <span class="text-4xl font-bold font-display text-indigo-600">{global_satisfaction:.2f}</span>
                            <span class="text-xl text-text-faint font-medium">/ 1.0</span>
                        </div>
                    </div>
                    <div class="relative flex items-center justify-center w-32 h-32">
                        <svg class="w-full h-full transform -rotate-90">
                            <circle class="text-slate-100" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" stroke-width="8"></circle>
                            <circle class="text-indigo-500 transition-all duration-1000" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" stroke-dasharray="364.4" stroke-dashoffset="{circle_offset}" stroke-linecap="round" stroke-width="10"></circle>
                        </svg>
                        <div class="absolute inset-0 flex flex-col items-center justify-center">
                            <span class="material-symbols-outlined text-indigo-600 text-3xl">star</span>
                        </div>
                    </div>
                </div>
            </div>

            <h2 class="text-xl font-semibold mb-5 flex items-center gap-3">
                Industry Leaderboards
                <span class="h-[1px] flex-1 bg-slate-200"></span>
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                
                <div class="bg-white rounded-xl border border-border shadow-sm overflow-hidden border-t-4 border-t-rose-500">
                    <div class="p-4 border-b border-slate-100 bg-rose-50/30 flex justify-between items-center">
                        <h5 class="font-semibold text-rose-700 flex items-center gap-2">
                            <span class="material-symbols-outlined text-[20px]">bolt</span> Trending Now
                        </h5>
                        <span class="text-[10px] uppercase font-bold text-rose-400">Viral Spike</span>
                    </div>
                    <div class="divide-y divide-slate-50">
                        {trending_html}
                    </div>
                </div>

                <div class="bg-white rounded-xl border border-border shadow-sm overflow-hidden border-t-4 border-t-amber-500">
                    <div class="p-4 border-b border-slate-100 bg-amber-50/30 flex justify-between items-center">
                        <h5 class="font-semibold text-amber-700 flex items-center gap-2">
                            <span class="material-symbols-outlined text-[20px]">workspace_premium</span> Hall of Fame
                        </h5>
                        <span class="text-[10px] uppercase font-bold text-amber-500">Evergreen</span>
                    </div>
                    <div class="divide-y divide-slate-50">
                        {hall_of_fame_html}
                    </div>
                </div>

                <div class="bg-white rounded-xl border border-border shadow-sm overflow-hidden border-t-4 border-t-indigo-500">
                    <div class="p-4 border-b border-slate-100 bg-indigo-50/30 flex justify-between items-center">
                        <h5 class="font-semibold text-indigo-700 flex items-center gap-2">
                            <span class="material-symbols-outlined text-[20px]">diamond</span> Hidden Gems
                        </h5>
                        <span class="text-[10px] uppercase font-bold text-indigo-400">Under Valued</span>
                    </div>
                    <div class="divide-y divide-slate-50">
                        {hidden_gems_html}
                    </div>
                </div>

            </div>
        </div>
    </main>
</body>
</html>
"""

# Render the HTML block inside Streamlit
components.html(html_ui, height=1000, scrolling=True)