import random  # Permet de générer des nombres aléatoires (utilisé pour générer un prix aléatoire)
import requests  # Permet d'effectuer des requêtes HTTP pour interagir avec l'API Rawg
from .models import Game, Platform, Developer, Tag, Genre, Trailer, Addition, Achievement  # Importation des modèles pour enregistrer les données dans la base

# Clé API et URL de l'API Rawg
API_KEY = '28e12bdf3e3243ad964f70e9bea3994e'  # Clé d'authentification pour l'API Rawg
BASE_URL = 'https://api.rawg.io/api/games'  # URL de l'API pour récupérer les jeux

# Mapping des ID ESRB (pour les évaluations d'âge) vers des âges réels
ESRB_ID_TO_AGE = {
    1: 3,   # Tout public
    2: 7,   # Tout public 10+
    3: 12,  # Adolescents
    4: 16,  # Matures
    5: 18   # Réservé aux adultes
}

# Fonction principale pour importer des jeux depuis l'API Rawg
def import_games(query="", platforms="4,187,18,1,186,7", start_date="2021-01-01", end_date="2025-12-31"):
    print(f"Importing games for query: {query}")  # Affiche la requête utilisée pour l'importation
    page = 1  # Initialisation de la première page de résultats

    while True:  # Boucle pour récupérer les jeux page par page
        response = requests.get(BASE_URL, params={  # Effectue une requête GET pour récupérer les jeux
            'key': API_KEY,
            'search': query,  # Requête de recherche
            'platforms': platforms,  # Plateformes filtrées
            'dates': f'{start_date},{end_date}',  # Plage de dates pour les jeux
            'ordering': '-released',  # Trie les jeux par date de sortie, les plus récents en premier
            'page_size': 40,  # Nombre de jeux par page
            'page': page  # Numéro de la page
        })

        # Vérification du succès de la requête API
        if response.status_code != 200:
            print(f"API Error {response.status_code}")  # Affiche l'erreur si la requête échoue
            break

        data = response.json()  # Parse la réponse JSON de l'API
        results = data.get('results', [])  # Récupère les résultats (les jeux)

        # Si aucun résultat n'est trouvé, on arrête la boucle
        if not results:
            break

        print(f"Found {len(results)} results on page {page}.")  # Affiche le nombre de jeux trouvés sur cette page

        for item in results:  # Pour chaque jeu dans les résultats
            game_id = item['id']  # Récupère l'ID du jeu

            # Requêtes pour obtenir des informations détaillées sur le jeu
            detail_response = requests.get(f"{BASE_URL}/{game_id}", params={'key': API_KEY})  # Détails du jeu
            trailer_response = requests.get(f"{BASE_URL}/{game_id}/movies", params={'key': API_KEY})  # Trailers du jeu
            addition_response = requests.get(f"{BASE_URL}/{game_id}/additions", params={'key': API_KEY})  # Additions/DLCs du jeu
            achievement_response = requests.get(f"{BASE_URL}/{game_id}/achievements", params={'key': API_KEY})  # Réalisations du jeu

            # Initialisation des variables pour les informations détaillées
            description = ""
            trailer_url = ""
            age_rating = None
            tags = []
            genres = []
            developers = []

            if detail_response.status_code == 200:  # Si la requête pour les détails est réussie
                detail_data = detail_response.json()  # Parse la réponse JSON

                description = detail_data.get('description_raw', '')  # Récupère la description brute du jeu

                # Création ou récupération des tags associés au jeu
                tags = [
                    Tag.objects.get_or_create(
                        rawg_id=t['id'],
                        defaults={'name': t['name'], 'slug': t['slug']}
                    )[0]
                    for t in detail_data.get('tags', [])  # Récupère la liste des tags du jeu
                ]

                # Création ou récupération des genres associés au jeu
                genres = [
                    Genre.objects.get_or_create(
                        rawg_id=g['id'],
                        defaults={'name': g['name'], 'slug': g['slug']}
                    )[0]
                    for g in detail_data.get('genres', [])  # Récupère la liste des genres du jeu
                ]

                # Conversion de la notation ESRB en âge réel si disponible
                esrb = detail_data.get('esrb_rating')
                if esrb and 'id' in esrb:
                    age_rating = ESRB_ID_TO_AGE.get(esrb['id'], None)  # Convertit l'ID ESRB en âge

                # Création ou récupération des développeurs associés au jeu
                developers = [Developer.objects.get_or_create(rawg_id=d['id'], name=d['name'], slug=d['slug'])[0] for d in detail_data.get('developers', [])]

            # Récupération du trailer vidéo du jeu
            if trailer_response.status_code == 200:
                videos = trailer_response.json().get('results', [])
                if videos:
                    trailer_url = videos[0].get('data', {}).get('max') or videos[0].get('data', {}).get('480')  # URL du trailer

            # Création ou récupération des plateformes associées au jeu
            platforms_list = [Platform.objects.get_or_create(rawg_id=p['platform']['id'], name=p['platform']['name'], slug=p['platform']['slug'])[0] for p in item.get('platforms', [])]

            # Génération d'un prix aléatoire entre 15 et 45 USD
            price = round(random.uniform(15.0, 45.0), 2)

            # Mise à jour ou création du jeu dans la base de données
            game, created = Game.objects.update_or_create(
                rawg_id=item['id'],
                defaults={
                    'name': item['name'],
                    'description': description,
                    'released': item.get('released'),
                    'background_image': item.get('background_image'),
                    'rating': item.get('rating', 0.0),
                    'rating_top': item.get('rating_top', 0),
                    'esrb_rating': age_rating,
                    'price': price  # Ajoute un prix aléatoire
                }
            )

            # Association des plateformes avec le jeu
            game.platforms.set(platforms_list)

            # Association des tags avec le jeu
            game.tags.set(tags)

            # Association des genres avec le jeu
            game.genres.set(genres)

            # Association des développeurs avec le jeu
            game.developers.set(developers)

            # Ajout du trailer vidéo associé
            # Ajout de tous les trailers disponibles
            if trailer_response.status_code == 200:
                trailers = trailer_response.json().get('results', [])
                for trailer in trailers:
                    Trailer.objects.get_or_create(
                        game=game,
                        name=trailer.get('name', 'Trailer'),
                        defaults={
                            'preview': trailer.get('preview'),
                            'video_url': trailer.get('data', {}).get('max') or trailer.get('data', {}).get('480')
                        }
                    )



            # Ajout des Additions (DLC, éditions spéciales, etc.)
            if addition_response.status_code == 200:
                additions = addition_response.json().get('results', [])
                for addition_item in additions:
                    Addition.objects.get_or_create(
                        game=game,
                        rawg_id=addition_item['id'],
                        defaults={
                            'name': addition_item['name'],
                            'released': addition_item.get('released'),
                            'background_image': addition_item.get('background_image'),
                            'metacritic': addition_item.get('metacritic'),
                            'rating': addition_item.get('rating', 0.0),
                            'rating_top': addition_item.get('rating_top', 0),
                            'esrb_rating': addition_item.get('esrb_rating', {}).get('name', '') if addition_item.get('esrb_rating') else ''
                        }
                    )

            # Ajout des réalisations du jeu
            if achievement_response.status_code == 200:
                achievements = achievement_response.json().get('results', [])
                for achievement_item in achievements:
                    Achievement.objects.get_or_create(
                        game=game,
                        rawg_id=achievement_item['id'],
                        defaults={
                            'name': achievement_item['name'],
                            'description': achievement_item.get('description'),
                            'image': achievement_item.get('image'),
                            'percent': achievement_item.get('percent', 0.0)
                        }
                    )

            print(f"Imported: {item['name']} (Price: ${price}, Age: {age_rating or 'N/A'})")  # Affiche le jeu importé avec son prix et sa classification

        page += 1  # Passe à la page suivante
