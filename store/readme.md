Modèles de base (indépendants de Game)
1. Platform
rawg_id : Identifiant unique de la plateforme dans l'API Rawg.

name : Nom de la plateforme (ex. "PC", "PlayStation").

slug : Slug pour l'URL (format URL-friendly du nom).

games_count : Nombre de jeux disponibles sur cette plateforme.

image_background : URL de l'image de fond associée à la plateforme.

image : URL de l'image représentant la plateforme.

year_start et year_end : Années de lancement et de fin de disponibilité de la plateforme (si applicable).

La méthode __str__() renvoie le nom de la plateforme pour une lecture plus simple dans l'administration.

2. Developer
rawg_id : Identifiant unique du développeur dans l'API Rawg.

name : Nom du développeur.

slug : Slug du développeur pour les URLs.

games_count : Nombre de jeux développés.

image_background : URL de l'image de fond du développeur.

description : Description du développeur.

La méthode __str__() renvoie le nom du développeur.

3. Tag
rawg_id : Identifiant unique du tag dans l'API Rawg.

name : Nom du tag (ex. "Action", "Adventure").

slug : Slug du tag pour les URLs.

games_count : Nombre de jeux associés à ce tag.

image_background : URL de l'image de fond associée au tag.

description : Description du tag.

La méthode __str__() renvoie le nom du tag.

4. Genre
rawg_id : Identifiant unique du genre dans l'API Rawg.

name : Nom du genre (ex. "FPS", "RPG").

slug : Slug du genre pour les URLs.

games_count : Nombre de jeux associés à ce genre.

image_background : URL de l'image de fond du genre.

description : Description du genre.

La méthode __str__() renvoie le nom du genre.

Modèles liés à Game
5. Game
rawg_id : Identifiant unique du jeu dans l'API Rawg.

slug : Slug du jeu pour l'URL.

name : Nom du jeu.

released : Date de sortie du jeu.

tba : Champ booléen pour savoir si le jeu est à venir (TBA = To Be Announced).

background_image : URL de l'image de fond du jeu.

rating, rating_top, ratings_count : Note globale du jeu, note maximale possible et nombre de notes.

metacritic : Score Metacritic du jeu.

playtime : Temps de jeu moyen en minutes.

suggestions_count : Nombre de suggestions liées au jeu.

updated : Date de la dernière mise à jour du jeu.

esrb_rating : Classification ESRB (ex. "Everyone", "Mature").

Relations ManyToMany :

platforms : Plateformes sur lesquelles le jeu est disponible.

developers : Développeurs du jeu.

tags : Tags associés au jeu.

genres : Genres associés au jeu.

La méthode __str__() renvoie le nom du jeu.

6. Addition
game : Clé étrangère vers le modèle Game, pour associer une addition (DLC, édition spéciale, etc.) au jeu.

rawg_id, slug, name : Identifiants et informations de l'addition (DLC ou édition spéciale).

released : Date de sortie de l'addition.

background_image : URL de l'image de fond de l'addition.

metacritic, rating, rating_top, esrb_rating : Scores et classification ESRB associés à l'addition.

La méthode __str__() renvoie le nom de l'addition.

7. Trailer
game : Clé étrangère vers le modèle Game, pour associer un trailer au jeu.

name : Nom du trailer.

preview : URL de la vidéo de preview.

video_url : URL de la vidéo complète du trailer (facultatif).

La méthode __str__() renvoie le nom du trailer ainsi que le nom du jeu auquel il est associé.

8. Achievement
game : Clé étrangère vers le modèle Game, pour associer une réalisation au jeu.

name : Nom de la réalisation.

description : Description de la réalisation.

image : URL de l'image associée à la réalisation.

percent : Pourcentage de joueurs ayant débloqué cette réalisation.

La méthode __str__() renvoie le nom de la réalisation et son pourcentage.

Modèles d'interaction utilisateur
9. Cart
user : Clé étrangère vers le modèle User, associant un panier à un utilisateur.

created_at : Date de création du panier.

Méthode total_price : Calcule le prix total du panier en additionnant le prix de chaque item.

Méthode __str__() : Renvoie une représentation textuelle du panier, incluant le nom de l'utilisateur.

10. CartItem
cart : Clé étrangère vers le modèle Cart, liant cet item à un panier.

game : Clé étrangère vers le modèle Game, liant cet item à un jeu spécifique.

quantity : Quantité du jeu dans le panier.

Méthode total_price : Calcule le prix total de cet item (prix du jeu multiplié par sa quantité).

Méthode __str__() : Renvoie une représentation textuelle de l'item dans le panier, incluant la quantité et le nom du jeu.
















admin.py :


from django.contrib import admin : Ce module permet d'interagir avec l'interface d'administration de Django. Il fournit des outils pour enregistrer et personnaliser les modèles qui seront gérés via l'interface admin.

from .models import Game : Ce code importe le modèle Game que tu as défini dans models.py. Il permet ensuite de l'enregistrer dans l'interface d'administration.

admin.site.register(Game) : Cette ligne enregistre le modèle Game dans l'interface d'administration de Django. Cela permet de gérer les objets Game directement depuis l'interface web de l'administration de Django, sans avoir à interagir directement avec la base de données.

Résultat :
Après avoir exécuté ce code et démarré le serveur Django, tu pourras gérer les jeux via l'interface d'administration en accédant à /admin. Tu pourras ajouter, modifier ou supprimer des objets de type Game directement depuis cette interface.

Si tu souhaites personnaliser davantage l'apparence ou les fonctionnalités de l'administration pour le modèle Game (par exemple, ajouter des filtres, des champs de recherche, ou des champs affichés), tu pourrais créer une classe ModelAdmin et l'enregistrer de manière plus détaillée.