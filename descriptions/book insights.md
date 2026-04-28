# 📖 Book Insights — Metric Definitions

> [!abstract] Overview
> Every book in the database carries a suite of computed metrics that measure quality, engagement, psychology, value, and virality. These metrics are derived from raw Goodreads data, NLP-processed review text, and cross-collection aggregation pipelines. Together they form a **360° analytical profile** of each book.
>
> All scores range from **0.0 to 1.0** unless otherwise noted.

---

# 🎯 Sentiment & Opinion Metrics

## 1. Sentiment Strength
`sentiment_strength`

> [!info] Definition
> The raw magnitude of the reviewers' opinions, stripping away whether those opinions are positive or negative.

### How to Calculate
1. Take the raw sentiment score from the NLP model (ranges from -1.0 to 1.0)
2. Convert to its *Absolute Value* (e.g., a -0.8 hate review and a +0.8 love review both become 0.8)
3. Average this across all reviews for the book

### Interpretation
- *High* → The book evokes strong opinions
- *Low* → Reviews are indifferent or purely descriptive ("The book had 300 pages and a blue cover")

### Why It Matters
> [!tip] The "Apathy Detector"
> In entertainment, *apathy is worse than hatred*. A book with high sentiment strength proves it leaves a lasting psychological imprint on the reader, regardless of whether they loved the hero or hated the villain.

---

## 2. Normalized Sentiment Strength
`normalized_sentiment_strength`

> [!info] Definition
> The sentiment_strength scaled perfectly between 0.0 and 1.0 relative to your specific database.

### How to Calculate
1. Find the *highest* and *lowest* sentiment_strength in your entire database
2. Apply *Relative Min-Max Normalization*:


$$
\frac{\text{score} - \min}{\max - \min}
$$


### Interpretation
- *1.0* → The most fiercely debated or passionately loved book in your system
- *0.0* → The most boring, universally "meh" book

### Why It Matters
> [!tip] Standardized Passion
> This standardizes passion so it can be fed into larger algorithms. It allows you to definitively rank books by *"vibe intensity,"* making it a crucial building block for calculating overall [[#6. Engagement Depth Score|Engagement Depth]].

---

## 3. Average Review Emotion
`avg_review_emotion` (stored as `avg_emotion_intensity` in `book_emotion_summary`)

> [!info] Definition
> The baseline emotional arousal triggered by the text. This is the **average emotion_intensity** across all NLP-processed reviews for a book, aggregated from the `review_nlp_analysis` collection.

### How to Calculate
1. For each review, the NLP model generates an `emotion_intensity` score
2. Group all reviews by `book_id`
3. Calculate the **mean** of `emotion_intensity` for each book
4. Store as `avg_emotion_intensity` in the `book_emotion_summary` collection

### Interpretation
- *High* → Readers were pushed into heightened states (intense joy, deep sadness, spiking fear)
- *Low* → The emotional landscape was flat

### Why It Matters
> [!tip] Opinion vs. Visceral Reaction
> While *sentiment* measures opinion (good/bad), *emotion* measures visceral reaction.
> - A *textbook* might have high positive sentiment ("This was very useful") but zero emotion.
> - A *thriller* might have terrifying emotion but mixed sentiment.
>
> This metric isolates the book's ability to *trigger the human nervous system*.

---

## 4. Average Sentiment Score
`avg_sentiment_score`

> [!info] Definition
> The directional emotional opinion of the crowd — how positive or negative readers feel about the book on average. Unlike `sentiment_strength` (which strips direction), this preserves the **polarity** of the opinion.

### How to Calculate
1. For each review, the NLP model produces a `sentiment_score` ranging from **-1.0** (extremely negative) to **+1.0** (extremely positive)
2. Group all reviews by `book_id`
3. Calculate the **mean** of `sentiment_score` for each book
4. Store as `avg_sentiment_score` in the `book_emotion_summary` collection

### Interpretation
| Score Range  | Meaning                                                |
| ------------ | ------------------------------------------------------ |
| +0.5 to +1.0 | Overwhelmingly positive — readers love this book       |
| +0.1 to +0.5 | Generally positive with some reservations              |
| -0.1 to +0.1 | Mixed or neutral — divisive or "just okay"             |
| -0.5 to -0.1 | Generally negative — disappointment or frustration     |
| -1.0 to -0.5 | Overwhelmingly negative — readers strongly disliked it |

### Why It Matters
> [!tip] The Direction of the Wind
> `sentiment_strength` tells you *how hard* the wind is blowing. `avg_sentiment_score` tells you *which direction*. A book with high strength but near-zero sentiment is a **battleground** — people love it and hate it in equal measure. A book with high strength AND high positive sentiment is a **universally beloved masterpiece**.
>
> Together they answer: *"Do people care?"* (strength) and *"Do they care positively or negatively?"* (sentiment score).

### Relationship to Other Metrics
- `sentiment_strength` = |avg_sentiment_score| averaged (direction stripped)
- `avg_sentiment_score` = raw directional average (direction preserved)
- Both feed into `engagement_depth_score` and `true_satisfaction`

---

# 🧠 Emotion Profile Metrics

## 5. Per-Book Emotion Averages
`emotion_joy` · `emotion_anger` · `emotion_sadness` · `emotion_fear` · `emotion_surprise`

> [!info] Definition
> The average intensity of each of the 5 core NLP emotions across all reviews for a specific book. These form the book's unique **emotional fingerprint**.

### How to Calculate
1. For each review, the NLP model outputs intensity scores for 5 emotions: joy, anger, sadness, fear, surprise
2. Group all reviews by `book_id`
3. Calculate the **mean** of each emotion column
4. Store all 5 averages in the `book_emotion_summary` collection

### The Five Dimensions

| Field              | Emotion  | Icon |
| ------------------ | -------- | ---- |
| `emotion_joy`      | Joy      | 😊    |
| `emotion_anger`    | Anger    | 😡    |
| `emotion_sadness`  | Sadness  | 😢    |
| `emotion_fear`     | Fear     | 😨    |
| `emotion_surprise` | Surprise | 😲    |

### Interpretation
- Each value represents the average intensity of that emotion across all the book's reviews
- Together they create the book's ==emotional DNA== — no two books have the same fingerprint

### Why It Matters
> [!tip] The Book's Emotional Genome
> This goes beyond "good or bad" into *how* the book makes people feel. A thriller might have: high Fear (0.4), high Surprise (0.3), moderate Anger (0.15), low Joy (0.1), low Sadness (0.05). A romance might have: high Joy (0.45), moderate Sadness (0.25), low everything else.
>
> This enables **emotion-based recommendation**: *"Show me books that feel like a mix of wonder and melancholy."*

---

## 6. Dominant Emotion
`dominant_emotion`

> [!info] Definition
> The single strongest emotion triggered by the book — the one emotional experience that defines what it *feels like* to read this book.

### How to Calculate
1. Take the 5 per-book emotion averages (`emotion_joy`, `emotion_anger`, `emotion_sadness`, `emotion_fear`, `emotion_surprise`)
2. Sort them from highest to lowest
3. The **highest** value wins — its label (e.g., "joy", "fear") becomes the `dominant_emotion`

### Interpretation

| Dominant Emotion | The Book Feels...                           |
| ---------------- | ------------------------------------------- |
| 😊 Joy            | Uplifting, feel-good, heartwarming          |
| 😡 Anger          | Provocative, frustrating, justice-driven    |
| 😢 Sadness        | Melancholic, bittersweet, emotionally heavy |
| 😨 Fear           | Tense, suspenseful, anxiety-inducing        |
| 😲 Surprise       | Unpredictable, twist-heavy, mind-bending    |

### Why It Matters
> [!tip] The One-Word Elevator Pitch
> If a reader asks *"What does this book feel like?"*, the dominant emotion is the instant, data-backed answer. It enables **emotion-based browsing**: filter your entire library by feeling, not just genre.

---

## 7. Secondary Emotion
`secondary_emotion`

> [!info] Definition
> The second-strongest emotion triggered by the book — the emotional undertone that runs beneath the primary experience.

### How to Calculate
1. Take the same sorted list of 5 emotions from `dominant_emotion`
2. The **second-highest** value becomes the `secondary_emotion`

### Interpretation
- The dominant + secondary emotion pair creates the book's **emotional signature**
- Example: *Fear + Surprise* = classic thriller. *Joy + Sadness* = bittersweet romance. *Anger + Fear* = dystopian or war novel.

### Why It Matters
> [!tip] Emotional Depth Beyond One Dimension
> Many books share the same dominant emotion. What makes a Stephen King horror novel feel different from a Shirley Jackson horror novel? The **secondary emotion**. King might be Fear + Anger (visceral, confrontational), while Jackson might be Fear + Sadness (creeping, melancholic).
>
> This pair enables much more nuanced recommendation and categorization than a single emotion ever could.

---

# 📊 Engagement & Behavior Metrics

## 8. Reviewer Engagement Score
`reviewer_engagement_score`

> [!info] Definition
> A measure of the sheer physical and cognitive effort readers put into writing their reviews.

### How to Calculate
1. Measure the *length/word count* of reviews for a book
2. Apply a *log transformation* (to handle massive 10,000-word essays)
3. *Min-Max normalize* from 0.0 to 1.0

### Interpretation
- *1.0* → The average reader writes a multi-paragraph, highly detailed essay
- *0.0* → Readers just drop a single sentence like "Good book."

### Why It Matters
> [!tip] Mental Real Estate
> This is a proxy for *"mental real estate."* If a book occupies a reader's mind so thoroughly that they spend 20 minutes typing out an essay about it on Goodreads, the book has successfully *monopolized their attention*.

---

## 9. Normalized Review Conversion
`normalized_review_conversion`

> [!info] Definition
> The rate at which casual consumers are converted into active advocates.

### How to Calculate
1. Divide `review_count` by `rating_count` (with a minimum of 1 to prevent division by zero)
2. Apply a *log transformation* (`np.log1p`) to smooth out viral spikes
3. *Min-Max normalize* to 0.0–1.0

### Interpretation
- Clicking ⭐⭐⭐⭐⭐ takes *one second*
- Writing a review takes *minutes*
- This measures the percentage of people who felt compelled to cross that barrier

### Why It Matters
> [!tip] The "Compulsion Metric"
> High conversion means the book leaves *"unresolved tension"* in the reader — they have to talk to someone about it, so they turn to the internet. This is the *primary engine of word-of-mouth marketing*.

---

## 10. Engagement Depth Score
`engagement_depth_score`

> [!info] Definition
> The ultimate *master metric* of a book's psychological grip on its audience.

### How to Calculate
A *weighted composite formula*:


$$
(\text{normalized\_review\_conversion} \times 0.3) + (\text{normalized\_sentiment\_strength} \times 0.25) + (\text{avg\_review\_emotion} \times 0.2) + (\text{reviewer\_engagement\_score} \times 0.25)
$$


| Component                     | Weight |
| ----------------------------- | ------ |
| normalized_review_conversion  | 0.30   |
| normalized_sentiment_strength | 0.25   |
| avg_review_emotion            | 0.20   |
| reviewer_engagement_score     | 0.25   |

### Interpretation
- The closer to 1.0, the more intensely the book *consumes* its readers

### Why It Matters
> [!tip] "How Hard Did People Care?"
> It combines *actions* (conversion, length) with *psychology* (emotion, sentiment). A high score here guarantees that a book is *culturally sticky*. It is the ==gold standard metric== of your entire database.

---

# ⭐ Quality & Satisfaction Metrics

## 11. Normalized Rating
`normalized_rating`

> [!info] Definition
> The traditional 5-star rating system, mathematically corrected to show *true variance*.

### How to Calculate
1. Convert the string rating (e.g., "3.37") to a float
2. Find the absolute *min* and *max* ratings present in your database
3. Apply *Min-Max Normalization*:


$$
\frac{\text{rating} - \text{db\_min}}{\text{db\_max} - \text{db\_min}}
$$


### Interpretation
| Example Rating | Normalized |
| -------------- | ---------- |
| 3.37 (worst)   | 0.0        |
| ~4.00          | ~0.5       |
| 4.77 (best)    | 1.0        |

### Why It Matters
> [!tip] Solving "Goodreads Bias"
> Readers rarely rate books below a 3. By stretching the ratings to a true 0–1 scale, you *expose the relative quality* of the books, making it painfully obvious which books are actually underperforming compared to their peers.

---

## 12. True Satisfaction
`true_satisfaction`

> [!info] Definition
> Authenticated quality. The *"Anti-Hype"* metric.

### How to Calculate
A 50/50 blend of conscious rating and subconscious effort:


$$
(\text{normalized\_rating} \times 0.5) + (\text{engagement\_depth\_score} \times 0.5)
$$


### Interpretation
- Roots out *fake, polite, or shallow* 5-star ratings

### Why It Matters
> [!tip] "Respected" vs. "Beloved"
> People often give 5 stars to a classic book just because they feel they "should," but they write a boring, 10-word review. True Satisfaction *demands proof*. To score high here, the crowd must:
> 1. Give it ⭐⭐⭐⭐⭐
> 2. *Back up* those stars with massive, emotional, high-conversion reviews
>
> It separates the *"respected"* books from the *"beloved"* books.

---

## 13. Emotional Complexity Score
`emotional_complexity_score`

> [!info] Definition
> The *"Rollercoaster Index"* measuring emotional variance.

### How to Calculate
1. Calculate the *Standard Deviation* across the 5 core NLP emotions:
   - 😊 Joy · 😡 Anger · 😢 Sadness · 😨 Fear · 😲 Surprise
2. *Min-Max normalize* that deviation across the database
3. *Invert* it: `1 - normalized_deviation`

### Interpretation
- *1.0* → The book makes the reader feel a massive variety of emotions in *equal measure*
- *0.0* → The book triggers only *one single emotion* (e.g., pure joy or pure anger)

### Why It Matters
> [!tip] The Shape of the Narrative
> - *High complexity* → Sweeping epics, intense thrillers, or deep memoirs that pull the reader in multiple psychological directions
> - *Low complexity* → Focused genre-fiction (cozy romance, straightforward comedy) that promises one specific mood and sticks to it

---

# 💰 Value & Longevity Metrics

## 14. Normalized Bang for Buck
`normalized_bang_for_buck`

> [!info] Definition
> The *Return on Investment (ROI)* for the reader's time and money.

### How to Calculate
1. Extract digits from `page_count` and `price`
2. Fill missing data with *database medians*
3. Clip the price to a minimum of \\$0.99 to prevent infinite division
4. Apply the formula:


$$
\text{np.log1p}\left(\frac{\text{pages} \times \text{engagement\_depth}}{\text{price}}\right)
$$


5. *Min-Max normalize* to 0.0–1.0

### Interpretation
- *1.0* → A massive, highly-engaging, cheap (or free) book
- *0.0* → A short, boring, expensive book

### Why It Matters
> [!tip] The Ultimate Consumer-Advocacy Metric
> It bridges the gap between *artistic merit* (Engagement Depth) and *economic reality* (Price per Page). It allows a user to ask:
>
> *"If I only have \\$10 to spend this month, which book will give me the highest volume of premium entertainment?"*

---

## 15. Normalized Timelessness
`normalized_timelessness`

> [!info] Definition
> The *"Staying Power" Index* — a measure of a book's enduring legacy and cultural relevance.

### How to Calculate
1. Calculate the *number of days* since the book was published
2. Apply a *log transformation* (`np.log1p`) — the difference between 1 year old vs. 10 years old matters much more than 100 vs. 110
3. Multiply this "time factor" by the [[#12. True Satisfaction|true_satisfaction]] score
4. *Min-Max normalize* the result across the database to 0.0–1.0

### Interpretation
| Score | Meaning                                                                                            |
| ----- | -------------------------------------------------------------------------------------------------- |
| 1.0   | An older book that still commands massive, highly emotional, 5-star reviews today (a true classic) |
| 0.0   | Either brand new (hasn't had time to prove itself) or old but forgotten (aged poorly)              |

### Why It Matters
> [!tip] The Lindy Effect Applied to Books
> This is the ultimate application of the *Lindy Effect* — the longer something has survived and remained relevant, the longer its remaining life expectancy.
>
> *Marketing and viral trends* drive reading for the first 6 months, but *legacy* drives reading for the next 60 years. This metric separates the temporary "flash-in-the-pan" TikTok trends from the ==permanent cultural touchstones==.
>
> It tells a user: *"This isn't just a good book right now; this is a good book forever."*

---

# 🚀 Virality Metrics

## 16. Normalized Demand Pressure
`normalized_demand_pressure`

> [!info] Definition
> The ratio of **anticipation to action** — how many people *want* to read the book compared to how many have *actually* read and rated it. It measures untapped demand and pre-read hype.

### How to Calculate
1. Divide `want_to_read_count` by `rating_count` (replace 0 with NaN to prevent division by zero)
2. Fill any NaN results with 0
3. Convert to **percentile rank** (0.0–1.0) across the entire database — this distributes the values evenly and prevents outliers from skewing the scale

### Interpretation
| Score | Meaning                                                                                                        |
| ----- | -------------------------------------------------------------------------------------------------------------- |
| ~1.0  | Massive waiting list relative to actual readers — high unrealized demand, the book is "on everyone's TBR list" |
| ~0.5  | Balanced — about as many people want to read it as have read it                                                |
| ~0.0  | Almost everyone who wanted to read it already has — demand is fully converted                                  |

### Why It Matters
> [!tip] The "TBR Pressure Gauge"
> A book with high demand pressure is a **loaded spring** — the audience exists but hasn't converted yet. For publishers this signals: *"This book is about to explode. The audience is primed, they just need a push (a sale, a BookTok mention, a movie deal)."*
>
> A book with LOW demand pressure but HIGH satisfaction is a **hidden gem** — great book, but nobody knows about it yet.

### Relationship to Other Metrics
- Feeds directly into `viral_potential_score` with a weight of **0.20**
- Complements `normalized_review_conversion` — conversion measures who DID act, demand pressure measures who WANTS to act

---

## 17. Viral Potential Score
`viral_potential_score`

> [!info] Definition
> A composite prediction of how likely a book is to blow up on social media, BookTok, or through word-of-mouth. It combines behavioral signals (engagement, conversion, demand) with psychological signals (emotion, sentiment) into a single virality index.

### How to Calculate
A *weighted composite formula*:


$$
(\text{engagement\_depth\_score} \times 0.35) + (\text{normalized\_review\_conversion} \times 0.25) + (\text{avg\_emotion\_intensity} \times 0.05) + (\text{normalized\_sentiment\_strength} \times 0.15) + (\text{normalized\_demand\_pressure} \times 0.20)
$$


| Component                       | Weight | Why This Weight                                                             |
| ------------------------------- | ------ | --------------------------------------------------------------------------- |
| `engagement_depth_score`        | 0.35   | The strongest predictor — deep engagement = people care enough to spread it |
| `normalized_review_conversion`  | 0.25   | People who write reviews are the ones who post on social media too          |
| `normalized_demand_pressure`    | 0.20   | A large "want to read" audience is fuel for viral ignition                  |
| `normalized_sentiment_strength` | 0.15   | Polarizing books get talked about more than "meh" books                     |
| `avg_emotion_intensity`         | 0.05   | Emotional arousal contributes but is less predictive alone                  |

### Interpretation
- Closer to **1.0** → The book has all the ingredients to go viral
- Closer to **0.0** → The book is unlikely to generate organic buzz

### Why It Matters
> [!tip] The "Will It Trend?" Predictor
> This metric answers the question every publisher, marketer, and author asks: *"If I put this book in front of people, will they talk about it?"*
>
> A high score means the book has: deep engagement (people care), high conversion (people write about it), strong demand pressure (people are waiting for it), and intense sentiment (people feel strongly). That combination is the ==exact formula for virality==.

---

## 18. Viral Label
`viral_label`

> [!info] Definition
> A human-readable categorical label that classifies the book's viral potential into one of three tiers, using **dynamic percentile thresholds** calculated from the actual database distribution.

### How to Calculate
1. Calculate `viral_potential_score` for all books
2. Find the **90th percentile** → this becomes the "High" threshold
3. Find the **50th percentile** → this becomes the "Moderate" threshold
4. Apply labels:

| Condition               | Label                          |
| ----------------------- | ------------------------------ |
| Score ≥ 90th percentile | 🔥 **High Viral Potential**     |
| Score ≥ 50th percentile | ⚡ **Moderate Viral Potential** |
| Score < 50th percentile | 💤 **Low Viral Potential**      |

### Why Dynamic Thresholds?
- Static thresholds (e.g., "above 0.7 = high") break when your data distribution changes
- Percentile-based thresholds **automatically adjust** as new books are added
- The top 10% is ALWAYS "High" regardless of absolute score values

### Why It Matters
> [!tip] The Traffic Light for Publishers
> Not everyone wants to read a decimal number. The viral label turns a complex composite score into an instant decision:
>
> 🔥 **High** → *"Prioritize marketing budget here. This book is ready to blow up."*
> ⚡ **Moderate** → *"Solid potential. Needs a strategic push — maybe a targeted campaign."*
> 💤 **Low** → *"Don't force it. Focus resources elsewhere or reposition the book."*

---

# 🏆 Comparative Metrics

## 19. Standout Scores
`standout_scores`

> [!info] Definition
> A per-genre comparative ratio that measures how a book's [[#12. True Satisfaction|true_satisfaction]] stacks up against the *average satisfaction of all books within that specific genre*. Stored as an array of objects on the book's document, with an accompanying `top_genre_standout_score` string.

### What It Looks Like

```json
[
  {"genre": "Science Fiction", "standout_score": 1.15},
  {"genre": "Fantasy", "standout_score": 0.95}
]
```

### How to Calculate


$$
\text{standout\_score} = \frac{\text{true\_satisfaction}}{\text{avg\_satisfaction (for that genre)}}
$$


**Full Pipeline:**
1. **Extract** — Query `books` for IDs, genres, and `true_satisfaction`. Query `genre_analysis` for `avg_satisfaction` per genre.
2. **Flatten** — Explode each book's genres list (3 genres = 3 rows).
3. **Merge** — Map genre-level `avg_satisfaction` onto each row.
4. **Calculate** — Divide book's `true_satisfaction` by genre's `avg_satisfaction`.
5. **Re-Group** — Package scores back into array format per book.
6. **Extract Top** — Find highest score, format as string (e.g., `"Science Fiction: 1.15"`).
7. **Update** — Bulk-write array and top-genre string to `books` collection.

### Interpretation
| Score | Meaning                                    |
| ----- | ------------------------------------------ |
| > 1.0 | The book *outperforms* the genre average   |
| = 1.0 | The book *matches* the genre average       |
| < 1.0 | The book *underperforms* the genre average |

### Why It Matters
> [!tip] The "Context Equalizer"
> Raw ratings don't tell the whole story — Romance naturally rates higher than Academic texts. The standout score normalizes against peers, enabling ==apples-to-apples comparison==.
>
> Books belong to multiple genres. A book might be an incredible Sci-Fi novel but a terrible Romance. This array tells you *exactly which niche the book excels in the most*.