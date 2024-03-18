import json

def generate_news_links(articles):
    """
    Generates HTML markup for news article links.
    
    Parameters:
    - articles: A dictionary where keys are article titles and values are article URLs.
    
    Returns:
    - A list of HTML strings for each news link.
    """
    return [f'<a href="{url}" target="_blank">{title}</a>' for title, url in articles.items()]

def display_news_links(news_i, news_links):
    """
    Displays news links on the provided Streamlit container.
    
    Parameters:
    - news_i: The Streamlit container or page to display the news links on.
    - news_links: A list of HTML strings containing news links.
    """
    for link in news_links:
        news_i.markdown(link, unsafe_allow_html=True)

def load_articles_from_json(json_file_path):
    """
    Loads news articles from a JSON file.
    
    Parameters:
    - json_file_path: Path to the JSON file containing news articles.
    
    Returns:
    - A dictionary where keys are article titles and values are article URLs.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    articles = {article['title']: article['url'] for article in data['articles']}
    return articles

def display_news(news_i):
    """
    Displays a list of news articles on a Streamlit container or page.
    
    Parameters:
    - news_i: The Streamlit container or page to display the news on.
    """
    articles = load_articles_from_json('articles.json')
    news_links = generate_news_links(articles)
    display_news_links(news_i, news_links)