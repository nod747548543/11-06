# Importation des modules nécessaires
from django.core.paginator import Paginator  # Permet de diviser les résultats en plusieurs pages
from django.shortcuts import render, get_object_or_404, redirect  # Fonctions pour afficher des pages et récupérer des objets
from .models import Game, Cart, CartItem  # Importation des modèles Game, Cart et CartItem pour la gestion des jeux et du panier
from django.http import JsonResponse,HttpResponseRedirect  # Permet de renvoyer des réponses JSON (utilisé dans les appels AJAX)
from django.contrib.auth.decorators import login_required  # Décorateur pour sécuriser l'accès aux vues nécessitant une authentification
from django.utils.http import urlsafe_base64_encode  # Permet d'encoder des identifiants en format sécurisé pour l'URL
from django.contrib.auth import get_user_model  # Permet d'obtenir le modèle utilisateur personnalisé, si utilisé
from django.contrib.auth import authenticate, login  # Fonctions pour authentifier et connecter un utilisateur
from django.contrib.auth.forms import AuthenticationForm  # Formulaire d'authentification fourni par Django
from django.contrib import messages  # Permet d'afficher des messages d'information ou d'erreur à l'utilisateur
from .forms import CustomUserCreationForm
from django.contrib.auth import login
import json
from store.utils import generate_game_key
from .forms import ActivateGameKeyForm
from .models import GameKey, Game
from .models import ActivationKey
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Genre, Developer


import stripe  # Librairie pour gérer les paiements avec Stripe
from django.conf import settings  # Permet d'accéder aux paramètres du fichier settings.py, comme la clé API Stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Configurer Stripe avec la clé secrète (commentée pour l'instant)
#stripe.api_key = settings.STRIPE_SECRET_KEY

# Vue pour afficher la liste des jeux
def game_list(request):
    query = request.GET.get('search', '')  # Récupère la requête de recherche depuis l'URL
    platform = request.GET.get('platform', '')  # Récupère le paramètre de plateforme depuis l'URL
    show_adult = request.GET.get('show_adult', '0') == '1'  # Vérifie si l'option de montrer les jeux adultes est activée

    games = Game.objects.all()  # Récupère tous les jeux

    selected_genre = request.GET.get('genre', '')
    selected_dev = request.GET.get('developer', '')


    if not show_adult:
        games = games.exclude(esrb_rating='18+')  # Exclut les jeux 18+ si l'option n'est pas activée

    if query:
        games = games.filter(name__icontains=query)  # Filtre les jeux par nom si une recherche est effectuée

    if platform:
        games = games.filter(platforms__name__icontains=platform).distinct()  # Filtre par plateforme

    if selected_genre:
        games = games.filter(genres__name=selected_genre)

    if selected_dev:
        games = games.filter(developers__name=selected_dev)

    paginator = Paginator(games, 14)  # Pagine les jeux, 14 jeux par page
    page_number = request.GET.get('page')  # Récupère le numéro de la page
    page_obj = paginator.get_page(page_number)  # Récupère les jeux pour la page courante
    genres = Genre.objects.all()
    developers = Developer.objects.all()

    return render(request, 'store/game_list.html', {
        'page_obj': page_obj,
        'search_query': query,
        'platform': platform,
        'show_adult': show_adult,
        'genres': genres,
        'developers': developers,
        'genres': Genre.objects.all(),
        'developers': Developer.objects.all(),
    })

# Vue pour afficher les détails d'un jeu spécifique
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)  # Récupère le jeu ou renvoie une erreur 404 si le jeu n'est pas trouvé
    return render(request, 'store/game_detail.html', {'game': game})  # Rend le template avec les détails du jeu

# Vue pour la recherche de jeux via AJAX
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.template.loader import render_to_string

def search_games(request):
    query = request.GET.get('query', '').strip()
    show_adult = request.GET.get('show_adult', '0') == '1'
    platform = request.GET.get('platform', '').strip()
    genre_param = request.GET.get('genre', '').strip()
    developer_param = request.GET.get('developer', '').strip()

    games = Game.objects.all()

    if query:
        games = games.filter(name__icontains=query)

    if platform:
        games = games.filter(platforms__name__icontains=platform)

    if genre_param:
        genre_list = genre_param.split(',')
        games = games.filter(genres__name__in=genre_list)

    if developer_param:
        dev_list = developer_param.split(',')
        games = games.filter(developers__name__in=dev_list)

    if not show_adult:
        games = games.exclude(esrb_rating='18+')

    games = games.distinct()

    # Cas spécial AUTOCOMPLÉTION (avec query + input => max 10 résultats simples en JSON)
    if query and 'autocomplete' in request.GET:
        games = games[:10]
        results = []
        for game in games:
            results.append({
                'id': game.id,
                'name': game.name,
                'image_url': game.background_image or '/static/img/no-image.png',  # adapte selon ton modèle
            })
        return JsonResponse({'results': results})

    # Sinon, cas FILTRAGE classique (retourne le HTML à injecter)
    games = games[:30]
    html = render_to_string('store/includes/game_list_items.html', {
        'page_obj': games,
        'user': request.user,
    }, request=request)
    return JsonResponse({'html': html})




# Vue pour ajouter un jeu au panier

from django.shortcuts import redirect

def add_to_cart(request, game_id):
    cart = json.loads(request.COOKIES.get('cart', '[]'))
    found = False

    for item in cart:
        if isinstance(item, dict) and item.get('game_id') == game_id:
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({'game_id': game_id, 'quantity': 1})

    response = redirect('cart_detail')
    response.set_cookie('cart', json.dumps(cart))
    return response



# Vue pour afficher le détail du panier


def cart_detail(request):
    raw_cart = request.COOKIES.get('cart', '[]')
    try:
        cart = json.loads(raw_cart)
    except json.JSONDecodeError:
        cart = []

    cart_items = []
    total_price = 0

    for item in cart:
        if not isinstance(item, dict):
            continue

        game_id = item.get('game_id')
        quantity = item.get('quantity', 1)

        if not game_id:
            continue

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            continue

        item_total = game.price * quantity
        total_price += item_total

        cart_items.append({
            'game': game,
            'quantity': quantity,
            'total_price': item_total
        })

    return render(request, 'store/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })




def checkout(request):
    cart = request.COOKIES.get('cart')
    if not cart:
        return redirect('cart_detail')

    cart_data = json.loads(cart)
    
    line_items = []
    for item in cart_data:
        try:
            game = Game.objects.get(id=item['game_id'])
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(game.price * 100),
                    'product_data': {
                        'name': game.name,
                    },
                },
                'quantity': item['quantity'],
            })
        except Game.DoesNotExist:
            continue


# Fonction pour créer une session de paiement Stripe (commentée)
@login_required
@csrf_exempt
def create_checkout_session(request):
    cart = get_cart_data(request)
    line_items = []

    for game_id, quantity in cart.items():
        game = Game.objects.get(id=game_id)
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'unit_amount': int(game.price * 100),  # en centimes
                'product_data': {
                    'name': game.name,
                },
            },
            'quantity': quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/complete_purchase/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/cart/'),
    )

    return JsonResponse({'id': session.id})


# Vue pour la connexion de l'utilisateur


#def login_view(request):
#    if request.method == "POST":
#        form = AuthenticationForm(request, data=request.POST)  # Crée un formulaire d'authentification avec les données soumises
#        if form.is_valid():
#            user = form.get_user()  # Récupère l'utilisateur authentifié
#            login(request, user)  # Connecte l'utilisateur
#            return redirect('home')  # Redirige vers la page d'accueil après la connexion
#        else:
#            messages.error(request, "Identifiants invalides")  # Affiche un message d'erreur si les identifiants sont incorrects
#    else:
#        form = AuthenticationForm()  # Crée un formulaire vide si la méthode est GET
#
#    return render(request, 'store/login.html', {'form': form})  # Rend le template de la page de connexion avec le formulaire
#
#def register_view(request):
#    if request.method == "POST":
#        form = CustomUserCreationForm(request.POST)
#        if form.is_valid():
#            user = form.save()
#            login(request, user)
#            return redirect('home')
#    else:
#        form = CustomUserCreationForm()
#    
#    return render(request, 'store/register.html', {'form': form})


def generate_key_for_user(user, game):
    key = generate_game_key()
    while GameKey.objects.filter(key=key).exists():
        key = generate_game_key()
    return GameKey.objects.create(user=user, game=game, key=key)




import string
import random

def generate_key():
    return '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))





def get_cart_data(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '[]'))
    except json.JSONDecodeError:
        cart = []

    cart_data = {}

    for item in cart:
        if isinstance(item, dict):
            game_id = item.get('game_id')
            quantity = item.get('quantity', 1)
            cart_data[str(game_id)] = quantity
        elif isinstance(item, int):
            cart_data[str(item)] = cart_data.get(str(item), 0) + 1

    return cart_data



@login_required
def activate_game_key(request):
    if request.method == 'POST':
        form = ActivateGameKeyForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            try:
                game_key = GameKey.objects.get(key=key, activated=False)
                game_key.user = request.user
                game_key.activated = True
                game_key.save()

                request.user.profile.games.add(game_key.game)  # si tu as cette relation
                messages.success(request, "Jeu activé avec succès !")
                return redirect('profile')
            except GameKey.DoesNotExist:
                form.add_error('key', "Clé invalide ou déjà utilisée.")
    else:
        form = ActivateGameKeyForm()
    return render(request, 'store/activate_game_key.html', {'form': form})

def complete_purchase(request):
    cart_cookie = request.COOKIES.get('cart')
    if not cart_cookie:
        return redirect('cart_detail')  # panier vide

    try:
        cart = json.loads(cart_cookie)
    except json.JSONDecodeError:
        return redirect('cart_detail')

    line_items = []
    for item in cart:
        try:
            game = Game.objects.get(id=item['game_id'])
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': game.name,
                    },
                    'unit_amount': int(game.price * 100),  # Stripe attend des centimes
                },
                'quantity': item['quantity'],
            })
        except Game.DoesNotExist:
            continue

    if not line_items:
        return redirect('cart_detail')  # rien à acheter

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/purchase_complete/?session_id={CHECKOUT_SESSION_ID}'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )

    return redirect(session.url)

@login_required
def purchase_complete(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('home')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != 'paid':
            return redirect('home')
    except Exception:
        return redirect('home')

    if request.session.get(f'purchase_complete_{session_id}'):
        keys = request.session.get(f'generated_keys_{session_id}', [])
        return render(request, 'store/complete_purchase.html', {'keys': keys})

    line_items = stripe.checkout.Session.list_line_items(session_id)
    keys = []

    for item in line_items.data:
        game_name = item.description or item.price.product_data.name
        quantity = item.quantity or 1

        try:
            game = Game.objects.get(name=game_name)
        except Game.DoesNotExist:
            continue

        for _ in range(quantity):
            key = generate_key()
            ActivationKey.objects.create(user=request.user, game=game, key=key, activated=False)
            keys.append(key)

    request.session[f'purchase_complete_{session_id}'] = True
    request.session[f'generated_keys_{session_id}'] = keys

    response = render(request, 'store/complete_purchase.html', {'keys': keys})
    response.delete_cookie('cart')
    return response


def thank_you(request):
    return render(request, 'store/thank_you.html')



import json
from django.http import JsonResponse


#@csrf_exempt
#def update_cart(request):
#    if request.method != 'POST':
#        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
#
#    try:
#        data = json.loads(request.body)
#        game_id = str(data.get('game_id'))
#        quantity = int(data.get('quantity', 1))
#        action = data.get('action', '').lower()
#    except (ValueError, json.JSONDecodeError):
#        return JsonResponse({'success': False, 'error': 'Requête invalide'}, status=400)
#
#    cart = json.loads(request.COOKIES.get('cart', '[]'))
#    updated = False
#
#    # Mise à jour ou suppression dans le panier
#    for item in cart:
#        if str(item.get('game_id')) == game_id:
#            if action == 'remove' or quantity <= 0:
#                cart.remove(item)
#            else:
#                item['quantity'] = quantity
#            updated = True
#            break
#
#    # Ajouter un nouvel item si non trouvé et action autorisée
#    if not updated and action != 'remove' and quantity > 0:
#        cart.append({'game_id': int(game_id), 'quantity': quantity})
#
#    # Calcul du total
#    total_price = 0
#    for item in cart:
#        try:
#            game = Game.objects.get(id=item['game_id'])
#            total_price += game.price * item['quantity']
#        except Game.DoesNotExist:
#            continue
#
#    response = JsonResponse({'success': True, 'total_price': round(total_price, 2)})
#    response.set_cookie('cart', json.dumps(cart), max_age=604800)  # 7 jours
#    return response







#@csrf_exempt  # à remplacer par @require_POST avec gestion correcte du token si possible
#@require_POST
#def update_cart_quantity(request):
#    try:
#        data = json.loads(request.body)
#        game_id = int(data.get('game_id'))
#        action = data.get('action')
#
#        # Charger le panier depuis les cookies
#        cart = request.COOKIES.get('cart')
#        cart_data = json.loads(cart) if cart else {}
#
#        game_key = str(game_id)
#        game = Game.objects.get(id=game_id)
#
#        if game_key not in cart_data:
#            return JsonResponse({'success': False, 'message': 'Produit non trouvé dans le panier'})
#
#        if action == 'increment':
#            if cart_data[game_key]['quantity'] < game.stock:
#                cart_data[game_key]['quantity'] += 1
#        elif action == 'decrement':
#            cart_data[game_key]['quantity'] -= 1
#            if cart_data[game_key]['quantity'] <= 0:
#                del cart_data[game_key]
#
#        # Calculs mis à jour
#        total_price = 0
#        for item_id, item in cart_data.items():
#            g = Game.objects.get(id=int(item_id))
#            total_price += g.price * item['quantity']
#
#        # Préparer réponse
#        response = JsonResponse({
#            'success': True,
#            'quantity': cart_data.get(game_key, {}).get('quantity', 0),
#            'item_total': round(game.price * cart_data.get(game_key, {}).get('quantity', 0), 2),
#            'cart_total': round(total_price, 2),
#        })
#
#        # Reposer le cookie avec les données modifiées
#        response.set_cookie('cart', json.dumps(cart_data))
#
#        return response
#
#    except Exception as e:
#        return JsonResponse({'success': False, 'error': str(e)})
    
    
def remove_from_cart(request, game_id):
    cart = json.loads(request.COOKIES.get('cart', '[]'))

    cart = [item for item in cart if not (isinstance(item, dict) and item.get('game_id') == game_id)]

    response = redirect('cart_detail')
    response.set_cookie('cart', json.dumps(cart), max_age=604800)  # 7 jours
    return response
    
    
from django.views.decorators.http import require_POST

#@require_POST
#def update_cart_ajax(request):
#    game_id = request.POST.get('game_id')
#    action = request.POST.get('action')
#
#    cart = request.session.get('cart', {})
#    game = Game.objects.filter(id=game_id).first()
#
#    if not game:
#        return JsonResponse({'success': False, 'error': 'Jeu introuvable.'})
#
#    current_quantity = int(cart.get(game_id, 0))
#
#    if action == 'increment':
#        if current_quantity < game.stock:
#            current_quantity += 1
#        else:
#            return JsonResponse({'success': False, 'error': f"Stock limité à {game.stock}."})
#    elif action == 'decrement':
#        current_quantity = max(0, current_quantity - 1)
#    else:
#        return JsonResponse({'success': False, 'error': 'Action inconnue.'})
#
#    if current_quantity == 0:
#        cart.pop(game_id, None)
#    else:
#        cart[game_id] = current_quantity
#
#    request.session['cart'] = cart
#
#    item_total = current_quantity * game.price
#    total_price = sum(Game.objects.get(id=int(k)).price * v for k, v in cart.items())
#
#    return JsonResponse({
#        'success': True,
#        'game_id': game_id,
#        'quantity': current_quantity,
#        'item_total': f"{item_total:.2f}",
#        'total_price': f"{total_price:.2f}"
#    })


from django.http import HttpRequest

#def increase_quantity(request, game_id):
#    cart = json.loads(request.COOKIES.get('cart', '[]'))
#    updated = False
#
#    for item in cart:
#        if item.get('game_id') == game_id:
#            item['quantity'] += 1
#            updated = True
#            break
#
#    if not updated:
#        cart.append({'game_id': game_id, 'quantity': 1})
#
#    response = redirect('cart_detail')
#    response.set_cookie('cart', json.dumps(cart), max_age=604800)
#    return response
#
#def decrease_quantity(request, game_id):
#    cart = json.loads(request.COOKIES.get('cart', '[]'))
#    new_cart = []
#
#    for item in cart:
#        if item.get('game_id') == game_id:
#            if item['quantity'] > 1:
#                item['quantity'] -= 1
#                new_cart.append(item)
#            # sinon on ne l’ajoute pas (donc supprimé)
#        else:
#            new_cart.append(item)
#
#    response = redirect('cart_detail')
#    response.set_cookie('cart', json.dumps(new_cart), max_age=604800)
#    return response


@csrf_exempt  # à remplacer par @csrf_protect si token géré
@require_POST
def ajax_update_cart(request):
    import json
    data = json.loads(request.body)
    action = data.get("action")
    game_id = int(data.get("game_id"))

    cart = json.loads(request.COOKIES.get("cart", "[]"))
    updated_cart = []
    total_price = 0
    quantity = 0
    item_total = 0
    cart_item_count = 0

    for item in cart:
        if item.get("game_id") == game_id:
            if action == "increment":
                item["quantity"] += 1
                updated_cart.append(item)
            elif action == "decrement":
                item["quantity"] -= 1
                if item["quantity"] > 0:
                    updated_cart.append(item)
            elif action == "remove":
                continue  # on ne le garde pas
        else:
            updated_cart.append(item)

    # Recalculer total panier
    for item in updated_cart:
        try:
            game = Game.objects.get(id=item["game_id"])
            total_price += float(game.price) * item["quantity"]
            cart_item_count += item["quantity"]
            if item["game_id"] == game_id:
                quantity = item["quantity"]
                item_total = float(game.price) * quantity
        except Game.DoesNotExist:
            continue

    response = JsonResponse({
        "success": True,
        "quantity": quantity,
        "item_total": f"{item_total:.2f}",
        "cart_total": f"{total_price:.2f}",
        "cart_item_count": cart_item_count
    })
    response.set_cookie("cart", json.dumps(updated_cart), max_age=604800)
    return response


from django.template.loader import render_to_string


def load_more_games(request):
    page = int(request.GET.get('page', 1))
    search = request.GET.get('search', '')
    platform = request.GET.get('platform', '')
    show_adult = request.GET.get('show_adult', '0') == '1'

    games = Game.objects.all()
    if not show_adult:
        games = games.exclude(esrb_rating='18+')
    if search:
        games = games.filter(name__icontains=search)
    if platform:
        games = games.filter(platforms__name__icontains=platform).distinct()

    paginator = Paginator(games, 14)
    page_obj = paginator.get_page(page)

    html = render_to_string('store/includes/game_list_items.html', {'page_obj': page_obj})

    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next()
    })

@login_required
@require_POST
def like_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.user in game.likes.all():
        game.likes.remove(request.user)
    else:
        game.likes.add(request.user)
    return redirect('home')

@login_required
@require_POST
def add_to_wishlist(request, game_id):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    game = get_object_or_404(Game, id=game_id)
    profile.games.add(game)
    return redirect('home')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

@login_required
def account_settings(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        user.username = username
        user.email = email
        user.save()
        messages.success(request, "Modifications enregistrées.")
        return redirect('account_settings')
    
    return render(request, 'accounts/account_settings.html')

@login_required
def account_delete(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')  # ou vers la page d’accueil après suppression
    
    return render(request, 'accounts/account_delete.html')