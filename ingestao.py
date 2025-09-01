import datetime
import json
import requests
import os

# Configurações da API do TMDB
tmdb_api_key = '7b93e36810f90f67e1da86093710e3d2'
action_genre_id = 28  # ID do gênero Ação no TMDB
adventure_genre_id = 12  # ID do gênero Aventura no TMDB

# Função para buscar dados da API do TMDB
def fetch_tmdb_data(api_key, genre_id, page):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}&page={page}"
    response = requests.get(url)
    return response.json()

# Buscar e salvar os dados
def salvar_json():
    genres = {'Action': action_genre_id, 'Adventure': adventure_genre_id}
    all_movies = []
    for genre, genre_id in genres.items():
        # Busca a primeira página para obter total_pages
        first_page = fetch_tmdb_data(tmdb_api_key, genre_id, 1)
        total_pages = first_page.get('total_pages', 1)
        all_movies.extend(first_page.get('results', []))
        for page in range(2, total_pages + 1):
            data = fetch_tmdb_data(tmdb_api_key, genre_id, page)
            all_movies.extend(data.get('results', []))
    os.makedirs('data/raw', exist_ok=True)
    path = "data/raw/filmes_raw.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    return {
        'statusCode': 200,
        'body': json.dumps('Dados buscados e salvos com sucesso')
    }


if __name__ == "__main__":

    salvar_json()