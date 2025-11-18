from sense_hat import SenseHat
import requests
import time
import spacy
from textblob import TextBlob
import re
import string
from datetime import datetime

sense = SenseHat()
nlp = spacy.load("en_core_web_sm")

CENTER_START = 2  # center dot start for 4x4 white divider

# GLOBAL: sentiment_to_color
def sentiment_to_color(article):
    """
    Returns a smooth gradient from green (positive) to red (negative)
    based on TextBlob polarity (-1 → 1).
    War/disaster keyword overrides force red.
    Positive override keywords force bright green.
    """

    text = f"{article['title']} {article['description'] or ''}".lower()

    war_terms = ["war", "attack", "conflict", "missile", "bomb", "hurricane", "disaster", "brutal"]
    positive_terms = ["wins", "peace", "celebrates", "agreement", "success", "victory"]

    # --- Hard overrides ---
    if any(t in text for t in war_terms):
        return [255, 0, 0], "war/disaster (override)"

    if any(t in text for t in positive_terms):
        return [0, 255, 0], "positive keyword (override)"

    # --- Continuous color scale ---
    score = article["textblob_score"]  # range -1..1

    # Normalize score → 0..1
    t = (score + 1) / 2

    # Interpolate between red → yellow → green
    # red = (255, 0, 0)
    # yellow = (255, 255, 0)
    # green = (0, 255, 0)

    if t < 0.5:
        # red → yellow
        r = 255
        g = int(510 * t)     # increases 0 → 255
        b = 0
    else:
        # yellow → green
        r = int(510 * (1 - t))  # decreases 255 → 0
        g = 255
        b = 0

    return [r, g, b], f"gradient ({score:.2f})"


# GLOBAL: display_article
def display_article(art):
    """Scroll the selected article's title and description, then return."""
    color, _ = sentiment_to_color(art)

    sense.clear([0, 0, 0])
    sense.show_message(
        f"Title: {art['title']}",
        scroll_speed=0.05,
        text_colour=color
    )

    time.sleep(0.5)
    sense.clear()


# MAIN FUNCTION
def display_bbc_news():
    # --- fetch articles ---
    mediastack_api_key = "5b65d5410513dd141509eeabf3c41b2b"
    url = f"http://api.mediastack.com/v1/news?access_key={mediastack_api_key}&languages=en&countries=us&sources=bbc&limit=30&sort=published_desc"
    res = requests.get(url)
    data = res.json()

    seen_urls = set()
    articles = []
    for article in data.get("data", []):
        if article.get("url") not in seen_urls:
            seen_urls.add(article.get("url"))
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "source": article.get("source"),
                "published_at": article.get("published_at")
            })
    articles = articles[:9]

    # --- keywords & sentiment ---
    months = {"january","february","march","april","may","june","july","august","september","october","november","december"}
    stop_words = {"on", "in", "at", "of", "the", "a", "an"}

    def extract_keyword_phrase(title, description):
        text = f"{title} {description or ''}"
        doc = nlp(text)
        proper_chunks = [chunk.text for chunk in doc.noun_chunks if any(tok.pos_ == "PROPN" for tok in chunk)]
        keyword = proper_chunks[0] if proper_chunks else (
            next((chunk.text for chunk in doc.noun_chunks if 1 <= len(chunk.text.split()) <= 5), None)
        )
        if keyword:
            keyword_words = [
                w for w in keyword.split()
                if w.lower() not in months and
                   w.lower() not in stop_words and
                   w.lower() != "news" and
                   not re.fullmatch(r"[\d\W]+", w)
            ]
            keyword = " ".join(keyword_words).strip() or None
        if not keyword:
            for word in title.split():
                w = word.lower().strip(string.punctuation)
                if (
                    w not in months and
                    w not in stop_words and
                    w != "news" and
                    len(w) > 1
                ):
                    keyword = word
                    break
        return keyword or "Article"

    for article in articles:
        article['keyword'] = extract_keyword_phrase(article['title'], article['description'])
        article['textblob_score'] = TextBlob(
            f"{article['title']} {article['description'] or ''}"
        ).sentiment.polarity

    # --- debug print ---
    for i, article in enumerate(articles, start=1):
        color, reason = sentiment_to_color(article)
        print(f"{i}. {article['title']}")
        print(f"   Keyword: {article['keyword']}")
        print(f"   TextBlob polarity: {article['textblob_score']:.2f}")
        print(f"   Reason for color: {reason}")
        print("-" * 50)

    # --- display intro ---
    if articles:
        dates = [
            datetime.fromisoformat(a['published_at'].replace('Z','+00:00'))
            for a in articles
        ]
        intro_message = f"BBC Articles {min(dates).strftime('%b %d')} to {max(dates).strftime('%b %d')}"
        sense.clear([0,0,255])
        sense.show_message(intro_message, scroll_speed=0.05, text_colour=[255,255,255])
        sense.clear()

        # white center dot
        for i in range(CENTER_START, CENTER_START + 4):
            for j in range(CENTER_START, CENTER_START + 4):
                sense.set_pixel(i, j, [255,255,255])
        time.sleep(0.5)
        sense.clear()

    # --- display keywords ---
    for article in articles:
        keyword = article['keyword']
        color, _ = sentiment_to_color(article)
        sense.clear(color)
        sense.show_message(keyword, scroll_speed=0.05, text_colour=color)
        time.sleep(0.3)

        # white square
        for i in range(CENTER_START, CENTER_START + 4):
            for j in range(CENTER_START, CENTER_START + 4):
                sense.set_pixel(i, j, [255,255,255])
        time.sleep(0.5)
        sense.clear()

    # --- horizontal 3x3 grid ---
    boxes = [
        (0,0),(3,0),(6,0),
        (0,3),(3,3),(6,3),
        (0,6),(3,6),(6,6)
    ]

    article_colors = [sentiment_to_color(a)[0] for a in articles]
    box_articles = {i: articles[i] for i in range(len(articles))}

    def draw_grid(highlight_idx=None):
        sense.clear()
        for idx, (x0, y0) in enumerate(boxes):
            color = article_colors[idx]
            for dx in range(2):
                for dy in range(2):
                    if idx == highlight_idx:
                        sense.set_pixel(x0+dx, y0+dy, [255,255,255])
                    else:
                        sense.set_pixel(x0+dx, y0+dy, color)

    selected = 0
    draw_grid(selected)

    # --- joystick navigation ---
    while True:
        for event in sense.stick.get_events():
            if event.action != 'pressed':
                continue
            if event.direction == 'up' and selected >= 3:
                selected -= 3
            elif event.direction == 'down' and selected <= 5:
                selected += 3
            elif event.direction == 'left' and selected % 3 != 0:
                selected -= 1
            elif event.direction == 'right' and selected % 3 != 2:
                selected += 1
            elif event.direction == 'middle':
                display_article(box_articles[selected])

            draw_grid(selected)


if __name__ == "__main__":
    display_bbc_news()