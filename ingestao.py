import datetime
import json
import requests
import os
import logging
import dotenv

dotenv.load_dotenv()

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Configurações da API do TMDB
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GENRES = {
    "Action": 28,     # Ação
    "Adventure": 12   # Aventura
}

# Função para buscar dados do TMDB
def fetch_tmdb_data(api_key: str, genre_id: int, page: int) -> dict:
    """
    Busca filmes da API do TMDB por gênero e página.
    """
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {"api_key": api_key, "with_genres": genre_id, "page": page}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao buscar dados do TMDB: {e}")
        return {}

# Função para extrair filmes de um gênero
def extract_movies(api_key: str, genre_id: int) -> list:
    """
    Extrai todos os filmes de um gênero (com paginação até 500).
    """
    all_movies = []
    first_page = fetch_tmdb_data(api_key, genre_id, 1)

    if not first_page:
        return []

    total_pages = min(first_page.get("total_pages", 1), 500)  # limite da API
    all_movies.extend(first_page.get("results", []))

    for page in range(2, total_pages + 1):
        data = fetch_tmdb_data(api_key, genre_id, page)
        if data:
            all_movies.extend(data.get("results", []))
        else:
            break

    return all_movies


# Função para salvar filmes em JSON
def save_json(movies: list, genre: str) -> str:
    """
    Salva filmes em JSON particionado por data e gênero.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    path = f"data/raw/{today}"
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"filmes_{genre.lower()}_raw.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)

    logging.info(f"Arquivo salvo: {file_path}")
    return file_path


def main():
    if not TMDB_API_KEY:
        logging.error("API Key não encontrada! Defina a variável de ambiente TMDB_API_KEY.")
        return

    for genre, genre_id in GENRES.items():
        logging.info(f"Extraindo filmes do gênero: {genre}")
        movies = extract_movies(TMDB_API_KEY, genre_id)
        if movies:
            save_json(movies, genre)
        else:
            logging.warning(f"Nenhum filme encontrado para {genre}.")


if __name__ == "__main__":
    main()
