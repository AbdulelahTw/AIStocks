import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "NEWS_API_KEY"
url = 'https://newsapi.org/v2/everything'

# Top 10 AI companies, for strict filtering
ai_companies = [
    "Nvidia", "Microsoft", "Google", "Meta", "AMD",
    "TSMC", "Broadcom", "Palantir", "Amazon", "Super Micro Computer"
]

# Query is focused on AI in the title or main context
company_query = " OR ".join(ai_companies)
q = f'(AI OR "artificial intelligence" OR "machine learning") AND ({company_query})'

# Date range: last 7 days
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=7)

params = {
    'q': q,
    'from': start_date.isoformat(),
    'to': end_date.isoformat(),
    'language': 'en',
    'sortBy': 'publishedAt',
    'pageSize': 100,
    'apiKey': API_KEY
}

all_articles = []
max_pages = 3

for page in range(1, max_pages + 1):
    params['page'] = page
    resp = requests.get(url, params=params)
    data = resp.json()

    if data.get('status') != 'ok':
        print(f"❌ Error {data.get('code')}: {data.get('message')}")
        break

    articles = data.get('articles', [])
    if not articles:
        break

    for art in articles:
        headline = art.get('title', '')
        desc = art.get('description', '')
        # Filter: at least one company in the title or description, and "AI" or "artificial intelligence" in title/desc
        relevant = (
            any(company.lower() in (headline + desc).lower() for company in ai_companies)
            and (
                "ai" in headline.lower() or
                "artificial intelligence" in headline.lower() or
                "ai" in desc.lower() or
                "artificial intelligence" in desc.lower()
            )
        )
        if not relevant:
            continue

        all_articles.append({
            'PublishedAt': art['publishedAt'][:10],
            'Title': headline,
            'Source': art['source']['name'],
            'URL': art['url'],
            'Description': desc,
        })

    total = data.get('totalResults', 0)
    if page * params['pageSize'] >= total:
        break

# Save
df = pd.DataFrame(all_articles)
print(f"✅ Retrieved {len(df)} AI-related articles from {start_date} to {end_date}.")
df.to_csv("data/ai_news_feed.csv", index=False)
