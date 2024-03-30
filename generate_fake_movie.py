import os
import django
from django.contrib.auth import get_user_model


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "htmx.settings")
django.setup()


from films.models import Film, UserFilms
from faker import Faker
from films.utils import get_max_order


user  = get_user_model().objects.get(id=1)

fake = Faker()
   

for _ in range(100):
    try:
        film = Film(name=fake.text(10))
        film.save()
    except:
        pass


print(f'Fake data generation completed ')

# Add film to the user


for film in Film.objects.all():
    if not UserFilms.objects.filter(user=user, film=film).exists():
        UserFilms.objects.create(
            user=user,
            film=film,
            order=get_max_order(user)
        )


print(f'Fake data generation completed ')