from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.game_list, name='home'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),

    # Recherche AJAX & scroll infini
    path('search/', views.search_games, name='search_games'),
    path('load-more-games/', views.load_more_games, name='load_more_games'),

    # Panier
    path('add-to-cart/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/ajax/update/', views.ajax_update_cart, name='ajax_update_cart'),
    path('remove-from-cart/<int:game_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Paiement & Clés
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('complete_purchase/', views.complete_purchase, name='complete_purchase'),
    path('purchase_complete/', views.purchase_complete, name='purchase_complete'),
    path('activer-clé/', views.activate_game_key, name='activate_game_key'),

    # Fonctions sociales
    path('like/<int:game_id>/', views.like_game, name='like_game'),
    path('wishlist/add/<int:game_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    # Compte utilisateur (à vérifier selon ton choix avec AllAuth)
    path('settings/', views.account_settings, name='account_settings'),
    path('delete/', views.account_delete, name='account_delete_request'),

    # AllAuth
    path('accounts/', include('allauth.urls')),
]
