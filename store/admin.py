from django.contrib import admin
from .models import Game, GameKey
from .utils import generate_game_key

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(GameKey)
class GameKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'game', 'user', 'activated')
