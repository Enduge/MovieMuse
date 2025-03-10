from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Movie, MovieReaction

from .forms import UpdateAvatarForm

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('movie')
        else:
            messages.info(request, 'Try again! Username or password is incorrect.')

    context = {}
    return render(request, 'users/login.html', context)

def logout_page(request):
    logout(request)
    return redirect('users:login')

def register_page(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('movie')
    else:
        form = UserCreationForm()
    return render(request,"users/register.html",{"form": form})

@login_required
def profile(request):
    # Get the user's liked and disliked movies
    liked_reactions = MovieReaction.objects.filter(
        user=request.user, 
        reaction_type='like'
    ).select_related('movie')
    
    disliked_reactions = MovieReaction.objects.filter(
        user=request.user, 
        reaction_type='dislike'
    ).select_related('movie')
    
    context = {
        'liked_movies': [reaction.movie for reaction in liked_reactions],
        'disliked_movies': [reaction.movie for reaction in disliked_reactions]
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def change_avatar(request):
    user_profile = request.user.profile

    if request.method == "POST":
        form = UpdateAvatarForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")  # Redirect after a successful update
    else:
        form = UpdateAvatarForm(instance=user_profile)

    return render(request, "users/change_avatar.html", {"form": form})  # Ensure GET requests return a response

@require_POST
@login_required
def react_to_movie(request):
    imdb_id = request.POST.get('imdb_id')
    title = request.POST.get('title')
    year = request.POST.get('year')
    poster = request.POST.get('poster')
    genre = request.POST.get('genre')
    rated = request.POST.get('rated')
    director = request.POST.get('director')
    reaction_type = request.POST.get('reaction_type')
    
    # Ensure reaction type is valid
    if reaction_type not in ['like', 'dislike']:
        return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'}, status=400)
    
    # Get or create the movie
    movie, created = Movie.objects.get_or_create(
        imdb_id=imdb_id,
        defaults={
            'title': title,
            'year': year,
            'poster': poster,
            'genre': genre,
            'rated': rated,
            'director': director
        }
    )
    
    # Check if the user already has a reaction to this movie
    try:
        reaction = MovieReaction.objects.get(user=request.user, movie=movie)
        
        # If the reaction is the same, remove it (toggle off)
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            return JsonResponse({
                'status': 'success',
                'action': 'removed',
                'message': f'Removed {reaction_type} for {movie.title}'
            })
        else:
            # If the reaction is different, update it
            reaction.reaction_type = reaction_type
            reaction.save()
            return JsonResponse({
                'status': 'success',
                'action': 'updated',
                'message': f'Updated to {reaction_type} for {movie.title}'
            })
            
    except MovieReaction.DoesNotExist:
        # Create a new reaction
        MovieReaction.objects.create(
            user=request.user,
            movie=movie,
            reaction_type=reaction_type
        )
        return JsonResponse({
            'status': 'success',
            'action': 'added',
            'message': f'Added {reaction_type} for {movie.title}'
        })
