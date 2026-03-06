import feedparser

def fetch_rss_feeds(urls):
    """Lê uma lista de URLs RSS e retorna uma lista de dicionários com as notícias."""
    news_items = []
    
    for url in urls:
        try:
            feed = feedparser.parse(url)
            
            # Obtém o nome da fonte a partir do título do feed ou da própria URL
            fonte = feed.feed.title if 'title' in feed.feed else url
            
            for entry in feed.entries:
                item = {
                    'fonte': fonte,
                    'titulo': entry.title,
                    'link': entry.link,
                    'descricao': entry.get('summary', entry.get('description', ''))
                }
                news_items.append(item)
                
        except Exception as e:
            print(f"Erro ao processar o feed {url}: {e}")
            
    return news_items
