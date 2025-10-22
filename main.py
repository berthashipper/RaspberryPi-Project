from sense_hat import SenseHat
import requests
import time
import spacy
from textblob import TextBlob
import re
import string

sense = SenseHat()
nlp = spacy.load("en_core_web_sm")

# --- get top CNN news ---
mediastack_api_key = "5b65d5410513dd141509eeabf3c41b2b"
url = (
    f"http://api.mediastack.com/v1/news?"
    f"access_key={mediastack_api_key}&languages=en&countries=us"
    f"&sources=cnn&limit=30&sort=published_desc"
)
res = requests.get(url)
data = res.json()

# --- Remove duplicates, filter CNN articles ---
seen_urls = set()
articles = []
for article in data.get("data", []):
    if article.get("source", "").lower().find("cnn") != -1 and article.get("url") not in seen_urls:
        seen_urls.add(article.get("url"))
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "source": article.get("source"),
            "published_at": article.get("published_at")
        })

articles = articles[:30]

# --- get informative multi-word keywords from title + description ---
months = {
    "january","february","march","april","may","june","july",
    "august","september","october","november","december"
}
stop_words = {"on", "in", "at", "of", "the", "a", "an"}

def extract_keyword_phrase(title, description):
    text = f"{title} {description or ''}"
    doc = nlp(text)

    # get proper noun chunks first
    proper_chunks = [chunk.text for chunk in doc.noun_chunks if any(tok.pos_ == "PROPN" for tok in chunk)]
    if proper_chunks:
        keyword = proper_chunks[0]
    else:
        # fallback: first noun chunk <= 5 words
        noun_chunks = [chunk.text for chunk in doc.noun_chunks if 1 <= len(chunk.text.split()) <= 5]
        keyword = noun_chunks[0] if noun_chunks else None

    # remove generic placeholders, months, stopwords, numbers, punctuation
    if keyword:
        keyword_words = [w for w in keyword.split()
                         if w.lower() not in months
                         and w.lower() not in stop_words
                         and w.lower() != "news"
                         and not re.fullmatch(r"[\d\W]+", w)]
        keyword = " ".join(keyword_words).strip()
        if not keyword:
            keyword = None

    # fallback: first meaningful word in title
    if not keyword:
        for word in title.split():
            word_lower = word.lower().strip(string.punctuation)
            if word_lower not in months and word_lower not in stop_words and word_lower != "news" and len(word_lower) > 1:
                keyword = word
                break

    return keyword or "Article"

# --- get keywords and sentiment ---
for article in articles:
    article['keyword'] = extract_keyword_phrase(article['title'], article['description'])
    article['textblob_score'] = TextBlob(f"{article['title']} {article['description'] or ''}").sentiment.polarity

# --- map sentiment/topic to color ---
def sentiment_to_color(article):
    text = f"{article['title']} {article['description'] or ''}".lower()

    war_terms = ["war", "attack", "conflict", "missile", "bomb", "hurricane", "disaster", "brutal"]
    positive_terms = ["wins", "peace", "celebrates", "agreement", "success", "victory"]

    if any(term in text for term in war_terms):
        color = [255, 0, 0]  # red
        reason = "war/disaster"
    elif any(term in text for term in positive_terms):
        color = [0, 255, 0]  # green
        reason = "positive"
    else:
        score = article['textblob_score']
        if score > 0.2:
            color = [0, 255, 0]
            reason = f"textblob positive ({score:.2f})"
        elif score < -0.2:
            color = [255, 0, 0]
            reason = f"textblob negative ({score:.2f})"
        else:
            color = [255, 255, 0]
            reason = f"textblob neutral ({score:.2f})"
    return color, reason

# --- debug print ---
for i, article in enumerate(articles, start=1):
    color, reason = sentiment_to_color(article)
    print(f"{i}. {article['title']}")
    print(f"   Keyword: {article['keyword']}")
    print(f"   TextBlob polarity: {article['textblob_score']:.2f}")
    print(f"   Reason for color: {reason}")
    print("-" * 50)

# --- display each keyword ---
for article in articles:
    keyword = article['keyword']
    color, _ = sentiment_to_color(article)
    sense.clear(color)
    sense.show_message(keyword, scroll_speed=0.05, text_colour=color)
    time.sleep(0.3)

sense.clear()