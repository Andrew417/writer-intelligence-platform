You are a Streamlit Dashboard Developer building the "PubIntel — Writer Intelligence Platform".

=============================================
PROJECT OVERVIEW
=============================================

This is a Big Data university project. We analyzed millions of book reviews using Classical NLP and Machine Learning. Your job is to build the Streamlit dashboard that displays all the analysis results beautifully.

The dashboard helps WRITERS and PUBLISHERS make data-driven decisions about what to write next.

IMPORTANT: We don't have real data yet. Use REALISTIC DUMMY/FAKE DATA everywhere. Hardcode sample data directly in the code using Python lists, dicts, and Pandas DataFrames. Make it look real and professional — use real book titles, real author names, realistic ratings, realistic percentages. The dummy data will be replaced with real data later.

=============================================
TECH STACK — STRICT RULES
=============================================

✅ ONLY USE:
- Python (no JavaScript, no TypeScript, no Node.js)
- Streamlit (for the entire web app)
- Plotly (for interactive charts)
- Pandas (for data handling)
- Matplotlib / Seaborn (for static charts if needed)
- Custom CSS injected via st.markdown(unsafe_allow_html=True) for styling

❌ NEVER USE:
- React, Vue, Angular, Svelte, or any JS framework
- Flask, Django, FastAPI, or any backend framework
- HTML files as pages (everything must be in Python .py files)
- BERT, GPT, Transformers, HuggingFace, or any LLM
- Any npm packages or node_modules
- wordcloud library (it doesn't install on our system — use bar charts for keywords instead)

=============================================
UI DESIGN REFERENCE
=============================================

There is a folder called "Ui pages" in the project directory. It contains HTML files exported from Google Stitch that show the EXACT visual design for each page of the dashboard.

YOUR JOB: Look at each HTML file in "Ui pages/" to understand the layout, colors, fonts, spacing, cards, tables, charts, and overall visual style. Then RECREATE that design in Streamlit using:
- st.columns() for layout grids
- st.markdown(unsafe_allow_html=True) with custom HTML/CSS for styled cards, tables, alerts, KPIs
- Plotly charts for interactive visualizations
- st.metric() for simple KPI displays
- st.selectbox(), st.slider(), st.radio() for user inputs

DESIGN SYSTEM from the UI files:
- Font: IBM Plex Sans (body), IBM Plex Mono (numbers/KPIs)
- Primary Color: #4F46E5 (indigo)
- Success/Positive: #10B981 (green)
- Error/Negative: #F43F5E (red/pink)
- Warning: #F59E0B (amber)
- Background: #F8FAFC (light gray)
- Cards: white background, border: 1px solid #E2E8F0, border-radius: 12px, subtle shadow
- Text Primary: #0F172A
- Text Muted: #64748B
- Sidebar: white background with left border

=============================================
DUMMY DATA STRATEGY
=============================================

Since we have NO real data yet, create realistic fake data for everything:

BOOKS (use real famous book titles):
- The Silent Echo, Midnight Sun, Shadows of the Past, The Last Kingdom, etc.
- Authors: J.K. Rowling, Stephen King, Dan Brown, Brandon Sanderson, etc.
- Genres: Fantasy, Romance, Thriller, Sci-Fi, Literary Fiction, Horror, Mystery, Contemporary, Historical Fiction, Young Adult
- Ratings: realistic range 2.5 to 4.9
- Page counts: 180 to 800
- Publication years: 2005 to 2025

SENTIMENT DATA:
- Positive: 60-80% for most genres
- Neutral: 10-25%
- Negative: 5-20%
- Fantasy should have highest positive, Horror highest negative

TOPICS/KEYWORDS per genre (make these realistic):
- Fantasy: "world building", "magic system", "character development", "plot twists", "slow burn"
- Romance: "chemistry", "slow burn", "emotional depth", "happy ending", "spicy scenes"
- Thriller: "plot twists", "suspense", "pacing", "unreliable narrator", "dark atmosphere"
- Horror: "atmosphere", "tension", "gore", "psychological", "jump scares"

EMOTIONS:
- Joy, Anger, Fear, Surprise, Sadness, Trust, Anticipation, Disgust
- Distribute realistically per genre

TRENDS:
- Show Fantasy and Romance growing over 2015-2025
- Show Literary Fiction declining
- Show Thriller stable

Create all dummy data as Python dicts/lists/DataFrames DIRECTLY in the code. No external CSV files needed.

=============================================
DASHBOARD PAGES TO BUILD
=============================================

PAGE 1: Dashboard (Home)
- Greeting header with user name
- 4 KPI cards in a row: Books Analyzed (2,360,655), Reviews Processed (15,745,302), Avg Rating (3.87/5.0), Genres Covered (24)
- 60/40 grid split:
  - LEFT: Top Performing Books table (title, author, rating, sentiment bar, viral score, trend arrow)
  - RIGHT: Stacked cards — Recent NLP Alerts (colored dots + text) and Portfolio Sentiment (donut-style display with 3 sentiment boxes showing positive/neutral/negative percentages)
- Bottom: Genre Distribution horizontal bar chart

PAGE 2: Book Insights
- Search/select a specific book from dropdown
- Show: title, author, genre, rating, review count in styled cards
- Sentiment breakdown for that book (Plotly pie chart)
- Top keywords from reviews (Plotly horizontal bar chart)
- Emotion distribution (Plotly radar chart)
- Sample positive and negative review quotes (styled cards)

PAGE 3: Genre Analysis
- Dropdown to select a genre
- Sentiment distribution for selected genre (Plotly pie or bar chart)
- Top 10 topics in that genre (Plotly horizontal bar chart)
- Top keywords by TF-IDF score (Plotly horizontal bar chart)
- Emotion distribution (Plotly radar chart or bar chart)
- Genre comparison: select 2 genres and show side-by-side sentiment + emotions

PAGE 4: Market Trends
- Line chart: genre popularity over years (Plotly line chart, one line per genre)
- Growing vs Declining genres (Plotly bar chart showing % change)
- Market Gap scatter plot: x = avg rating, y = number of books, bubble size = review count. Top-left quadrant = high quality + low supply = OPPORTUNITY
- Heatmap: genres × emotions (Plotly heatmap)

PAGE 5: Rating Predictor
- User inputs via Streamlit widgets:
  - st.selectbox for genre
  - st.slider for number of pages (100-800)
  - st.multiselect for themes
  - st.selectbox for target emotion
- "Predict" button
- Display predicted rating in a big styled card: "Your book would score approximately: 4.2 / 5.0"
- Show classification: "Highly Loved" / "Mixed" / "Disliked" with colored badge
- Feature importance chart (Plotly horizontal bar)
- NOTE: Since we have no real model, FAKE the prediction using a simple formula based on inputs

PAGE 6: Hidden Gems
- Explanation card: what is a Hidden Gem and the HGI formula
- Table of hidden gem books (sortable, filterable by genre)
- Hidden Gem Index: HGI = (sentiment_score × rating) / log(review_count)
- Scatter plot: x = review count (log scale), y = rating, color = sentiment, size = HGI
- Genre filter dropdown
- Cluster visualization (Plotly scatter with colored clusters)

=============================================
PROJECT STRUCTURE
=============================================

writer-intelligence-platform/
├── app.py                    ← Main Streamlit app (ALL code here)
├── requirements.txt
└── Ui pages/                 ← HTML design reference files (read only, don't serve)
    ├── dashboard.html
    ├── book_insights.html
    ├── genre_analysis.html
    ├── market_trends.html
    ├── rating_predictor.html
    └── hidden_gems.html

Keep it simple: put EVERYTHING in app.py for now. One single file. We can split later.

=============================================
CSS STYLING RULES
=============================================

Inject all CSS via st.markdown() at the top of app.py:

- Hide Streamlit default header, footer, and hamburger menu
- Import IBM Plex Sans and IBM Plex Mono from Google Fonts
- Set max-width to 1280px for main content
- KPI cards: white bg, rounded-xl (12px), border #E2E8F0, shadow-sm, hover shadow
- Section cards: same style with title + subtitle header
- Tables: custom HTML tables with hover effects (NOT st.dataframe)
- Plotly color scheme: ["#4F46E5", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#F43F5E"]
- All Plotly charts: transparent/white background, clean layout, IBM Plex Sans font, no excessive gridlines
- Sidebar: clean with logo at top, nav items, user profile at bottom

=============================================
APP ARCHITECTURE
=============================================

app.py should:
1. Set page config: wide layout, title "PubIntel Dashboard", icon ✨
2. Inject global custom CSS
3. Build sidebar: logo + navigation radio + user profile at bottom
4. Create ALL dummy data as DataFrames/dicts at the top of the file
5. Route to different page content based on sidebar selection
6. Each page reads from the dummy data and displays charts + styled HTML

=============================================
CRITICAL INSTRUCTIONS
=============================================

1. LOOK AT "Ui pages/" HTML FILES FIRST before building each page — they show exact design
2. ALL dummy data must look REALISTIC — real book names, real authors, realistic numbers
3. Everything in Python — no separate files served
4. All styling through st.markdown(unsafe_allow_html=True)
5. Use Plotly for ALL interactive charts
6. ONE single app.py file with everything
7. Make sure it runs with: streamlit run app.py
8. Every page must feel POLISHED and COMPLETE
9. Use st.columns() to match the grid layouts from UI designs
10. This is for a university presentation — it must look professional

=============================================
RUN COMMAND
=============================================

C:\Users\andre\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run app.py

=============================================
START BUILDING NOW
=============================================

Begin by:
1. Reading all HTML files in "Ui pages/" folder to understand the design
2. Creating all dummy data (books, reviews, sentiment, topics, emotions, trends, hidden gems)
3. Building the complete app.py with CSS + sidebar + all 6 pages
4. Making every page match the UI design as closely as possible in Streamlit