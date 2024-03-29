from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower

class User(AbstractUser):
    pass


class Film(models.Model):
    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(User, related_name='films', through='UserFilms') # this related will help us to get all films of a user like user.films.all()
    photo = models.ImageField(upload_to='film_photos/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = [Lower('name')]


# if you face with issues if you have not created the UserFilms model before the migration, you can create it manually but check this link for help https://stackoverflow.com/questions/26927705/django-migration-error-you-cannot-alter-to-or-from-m2m-fields-or-add-or-remove

class UserFilms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()


    class Meta:
        ordering = ['order']