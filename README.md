🎮 GameKeys - Setup Guide
⚙️ Environnement virtuel
Crée un environnement virtuel (si ce n'est pas déjà fait) :

bash

        python -m venv env

Active-le :

git bash

        source env/Scripts/activate



📦 Installation des dépendances
Mets à jour pip :

bash

        python -m pip install --upgrade pip
Installe les paquets nécessaires :

bash

        pip install django requests django-environ djangorestframework
Détail des paquets :
django : le framework web

requests : pour appeler des APIs externes (comme RAWG)

django-environ : pour gérer les variables d'environnement via un fichier .env (pratique et sécurisé)

djangorestframework : pour ajouter une API REST au projet (si nécessaire)

📝 Enregistrer les dépendances
Après installation, sauvegarde-les dans requirements.txt :


https://docs.allauth.org/en/dev/installation/quickstart.html
pip install django-allauth



bash

pip freeze > requirements.txt
🚀 Lancer le projet
Une fois les dépendances installées et l’environnement activé :

bash

python manage.py runserver
Accède au site ici :
👉 http://127.0.0.1:8000

pip install stripe



stripe doc : https://docs.stripe.com/testing