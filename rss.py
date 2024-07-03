import feedparser
import requests
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from html import unescape

def get_rss_feed(url):
    """
    Pega o feed RSS de uma URL e retorna um objeto feedparser.FeedParser.

    Args:
        url: A URL do feed RSS.

    Returns:
        Um objeto feedparser.FeedParser.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return feedparser.parse(response.content)
    else:
        raise Exception(f"Falha ao obter feed RSS: {response.status_code}")

def get_recent_entries(feed, start_time, keywords):
    """
    Pega as entradas do feed RSS publicadas a partir de um horário específico e que contêm palavras-chave específicas.

    Args:
        feed: Um objeto feedparser.FeedParser.
        start_time: Um objeto datetime que representa o horário de início.
        keywords: Uma lista de palavras-chave para filtrar as entradas.

    Returns:
        Uma lista de tuplas contendo o título, o link e o resumo das entradas recentes que contêm as palavras-chave.
    """
    recent_entries = []
    for entry in feed.entries:
        if 'published_parsed' in entry:
            pub_date = datetime(*entry.published_parsed[:6])
            if pub_date >= start_time:
                # Verifica se alguma palavra-chave está no título ou no conteúdo usando regex case sensitive
                entry_content = entry.title + " " + entry.summary
                if any(re.search(keyword, entry_content) for keyword in keywords):
                    summary = entry.summary if 'summary' in entry else 'No summary available'
                    summary = clean_html(summary)
                    recent_entries.append((entry.title, entry.link, summary))
    return recent_entries

def clean_html(raw_html):
    """
    Remove tags HTML de uma string e decodifica entidades HTML.

    Args:
        raw_html: Uma string contendo HTML.

    Returns:
        Uma string sem tags HTML e com entidades HTML decodificadas.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    return unescape(text)

def read_keywords(filename):
    """
    Lê um arquivo de texto contendo palavras-chave e retorna uma lista de palavras-chave.

    Args:
        filename: O nome do arquivo de texto.

    Returns:
        Uma lista de palavras-chave.
    """
    if not os.path.isfile(filename):
        print(f"O arquivo {filename} não foi encontrado.")
        return []

    try:
        with open(filename, 'r') as f:
            keywords = [line.strip() for line in f]
        return keywords
    except IOError as e:
        print(f"Ocorreu um erro ao ler o arquivo {filename}: {e}")
        return []

def process_rss_file(rss_filename, keywords_filename):
    """
    Processa um arquivo de texto contendo URLs de feeds RSS e imprime o título, o link e o resumo das entradas publicadas a partir da meia-noite do dia anterior até a hora atual que contêm palavras-chave específicas.
    Salva os resultados em um arquivo com o nome `resenha_*datadehoje*`.

    Args:
        rss_filename: O nome do arquivo de texto com URLs de feeds RSS.
        keywords_filename: O nome do arquivo de texto com palavras-chave para filtrar as entradas.
    """
    if not os.path.isfile(rss_filename):
        print(f"O arquivo {rss_filename} não foi encontrado.")
        return

    keywords = read_keywords(keywords_filename)
    if not keywords:
        print("Nenhuma palavra-chave encontrada para filtrar as notícias.")
        return

    now = datetime.now()
    yesterday_midnight = datetime(now.year, now.month, now.day) - timedelta(days=1)
    today_date = now.strftime("%Y-%m-%d")
    output_filename = f"resenha_{today_date}.txt"

    with open(output_filename, 'w') as output_file:
        output_file.write(f"Resenha diária do dia {today_date}\n\n")

        try:
            with open(rss_filename, 'r') as f:
                for line in f:
                    url = line.strip()
                    try:
                        feed = get_rss_feed(url)
                        recent_entries = get_recent_entries(feed, yesterday_midnight, keywords)
                        if recent_entries:
                            output_file.write(f"URL: {url}\n")
                            for title, link, summary in recent_entries:
                                output_file.write(f"Título: {title}\n")
                                output_file.write(f"Link: {link}\n")
                                output_file.write(f"Resumo: {summary}\n")
                                output_file.write("\n")
                    except Exception as e:
                        print(f"Falha ao processar URL: {url}")
                        print(e)
        except IOError as e:
            print(f"Ocorreu um erro ao ler o arquivo {rss_filename}: {e}")

if __name__ == "__main__":
    rss_filename = "caminho/ absoluto/url.txt"
    keywords_filename = "caminho/absoluto/filtro.txt"
    process_rss_file(rss_filename, keywords_filename)
