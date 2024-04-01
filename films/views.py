from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from films.models import Film, UserFilms
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from films.utils import get_max_order, reorder
from django.contrib import messages
from django.conf import settings

from films.forms import RegisterForm

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)
    

def check_username(request):
    username  = request.POST.get('username')
    if username:
        if get_user_model().objects.filter(username=username).exists():
            return HttpResponse("<div id='username-error' class='error'>This username already exists</div>")
        else:
            return HttpResponse("<div id='username-success' class='success'>This username is available</div>")
    else:
        return HttpResponse("<div id='username-error' class='error'>Username is required</div>")
    



class FilmList(ListView):
    template_name = 'films.html'
    model = UserFilms
    paginate_by = settings.PAGINATE_BY
    context_object_name = 'films'

    def get_template_names(self):
        if self.request.htmx:
            return 'partials/film-list-elements.html'
        return 'films.html'

    def get_queryset(self):
        return UserFilms.objects.prefetch_related('film').filter(user=self.request.user)
    
@login_required
def add_film(request):
    name = request.POST.get('filmname')
    if name == '':
        return render(request, 'partials/film-list.html', {'films': UserFilms.objects.filter(user=request.user)})
    film = Film.objects.get_or_create(name=name)[0]

    if not UserFilms.objects.filter(user=request.user, film=film).exists():
        UserFilms.objects.create(
            user=request.user,
            film=film,
            order=get_max_order(request.user)
        )

    films = UserFilms.objects.filter(user=request.user)
    messages.success(request, f'Added {name} to list of films!')
    return render(request, 'partials/film-list.html', {'films': films})

@login_required
@require_http_methods(['DELETE'])
def delete_film(request, pk):
    UserFilms.objects.get(pk=pk).delete()
    reorder(request.user)
    films = UserFilms.objects.filter(user=request.user)
    return render(request, 'partials/film-list.html', {'films': films})


@login_required
def search_film(request):
    search_text = request.POST.get('search')
    userfilms  = UserFilms.objects.filter(user=request.user)
    results = Film.objects.filter(name__icontains=search_text).exclude(
        name__in=userfilms.values_list('film__name', flat=True)
    )
    context = {
        'results': results
    }
    return render(request, 'partials/search-results.html', context)


def clear(request):
    return HttpResponse("")


def sort(request):
    film_pks_order = request.POST.getlist('film_order')
    films = []
    updated_films = []
    userfilms = UserFilms.objects.prefetch_related('film').filter(user=request.user)
    for idx, film_pk in enumerate(film_pks_order, start=1):
        # userfilm = UserFilms.objects.get(pk=film_pk)
        userfilm = next(u for u in userfilms if u.pk == int(film_pk))
        if userfilm.order != idx:
            userfilm.order = idx
            updated_films.append(userfilm)
        films.append(userfilm)
    UserFilms.objects.bulk_update(updated_films, ['order'])
    paginator = Paginator(films, settings.PAGINATE_BY)
    page_number = len(film_pks_order) / settings.PAGINATE_BY
    page_obj  = paginator.get_page(page_number)
    return render(request, 'partials/film-list.html', {'films': films, 'page_obj': page_obj})

@login_required
def detail(request, pk):
    userfilm = get_object_or_404(UserFilms, pk=pk)
    context = {
        'userfilm': userfilm
    }
    return render(request, 'partials/film-detail.html', context)


@login_required
def films_partial(request):
    films = UserFilms.objects.filter(user=request.user)
    return render(request, 'partials/film-list.html', {'films': films})


@login_required
def upload_photo(request, pk):
    userfilm = get_object_or_404(UserFilms, pk=pk)
    photo = request.FILES.get('photo')
    userfilm.film.photo.save(photo.name, photo)
    context = {
        'userfilm': userfilm
    }
    return render(request, 'partials/film-detail.html', context)


@login_required
def film_detail_name(request, name):
    film = Film.objects.get(name=name)
    userfilm = get_object_or_404(UserFilms, film=film)
    context = {
        'userfilm': userfilm
    }

    return render(request, 'partials/film-detail.html', context)