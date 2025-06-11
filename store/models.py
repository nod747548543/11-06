import random
from django.db import models
from django.contrib.auth.models import User

# --- Modèles de base (indépendants de Game) ---
class Platform(models.Model):
    rawg_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    games_count = models.PositiveIntegerField(null=True, blank=True)
    image_background = models.URLField(max_length=500, null=True, blank=True)
    image = models.URLField(max_length=500, null=True, blank=True)
    year_start = models.PositiveIntegerField(null=True, blank=True)
    year_end = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Developer(models.Model):
    rawg_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    games_count = models.PositiveIntegerField(null=True, blank=True)
    image_background = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    rawg_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    games_count = models.PositiveIntegerField(null=True, blank=True)
    image_background = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    rawg_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    games_count = models.PositiveIntegerField(null=True, blank=True)
    image_background = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# --- Modèles liés à Game ---
class Game(models.Model):
    rawg_id = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(max_length=100)
    name = models.CharField(max_length=255)
    released = models.DateField(null=True, blank=True)
    tba = models.BooleanField(default=False)
    background_image = models.URLField(max_length=500, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    rating_top = models.PositiveIntegerField(default=0)
    ratings_count = models.PositiveIntegerField(default=0)
    metacritic = models.PositiveIntegerField(null=True, blank=True)
    playtime = models.PositiveIntegerField(default=0)
    suggestions_count = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(null=True, blank=True)
    esrb_rating = models.CharField(max_length=50, null=True, blank=True)

    platforms = models.ManyToManyField(Platform, blank=True)
    developers = models.ManyToManyField(Developer, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_games', blank=True)
    
    stock = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.stock is None:
            self.stock = random.randint(100, 500)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Addition(models.Model):
    game = models.ForeignKey(Game, related_name='additions', on_delete=models.CASCADE)
    rawg_id = models.IntegerField(unique=True)
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    released = models.DateField(null=True, blank=True)
    background_image = models.URLField(max_length=500, null=True, blank=True)
    metacritic = models.IntegerField(null=True, blank=True)
    playtime = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    rating_top = models.IntegerField(default=0)
    esrb_rating = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Trailer(models.Model):
    game = models.ForeignKey(Game, related_name='trailers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    preview = models.URLField()
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.game.name}"


class Achievement(models.Model):
    game = models.ForeignKey(Game, related_name='achievements', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.URLField(null=True, blank=True)
    percent = models.FloatField(default=0.0)
    rawg_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.percent}%)"


# --- Modèles d'interaction utilisateur ---
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.game.price

    def __str__(self):
        return f"{self.quantity} x {self.game.name}"


class GameKey(models.Model):
    key = models.CharField(max_length=50, unique=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game)  # Relation ManyToMany avec les jeux

    def __str__(self):
        return self.user.username
    
class ActivationKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    key = models.CharField(max_length=20, unique=True)
    activated = models.BooleanField(default=False)
    activated_on = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.key} - {self.game.name} ({'Activated' if self.activated else 'Not Activated'})"

