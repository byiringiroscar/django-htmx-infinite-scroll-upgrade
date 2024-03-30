import os
import django
from django.contrib.auth import get_user_model


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "htmx.settings")
django.setup()


from films.models import Film
from faker import Faker

fake = Faker()

try:
    user = get_user_model().objects.get(id=1)
except:
    print('user with id 1 not found')
   

for _ in range(100):
    try:
        film = Film(name=fake.text(10))
        film.save()
    except:
        pass


print(f'Fake data generation completed ')