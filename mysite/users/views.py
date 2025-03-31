from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Movie, MovieReaction, Friendship

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
    
    # Get friend requests
    pending_requests = Friendship.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender')
    
    # Get accepted friends
    friends = Friendship.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        status='accepted'
    )
    
    friend_users = []
    for friendship in friends:
        if friendship.sender == request.user:
            friend_users.append(friendship.receiver)
        else:
            friend_users.append(friendship.sender)
    
    context = {
        'liked_movies': [reaction.movie for reaction in liked_reactions],
        'disliked_movies': [reaction.movie for reaction in disliked_reactions],
        'pending_requests': pending_requests,
        'friends': friend_users
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Check if the viewed user is a friend
    is_friend = Friendship.objects.filter(
        (Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)),
        status='accepted'
    ).exists()
    
    # Get friend status
    friendship_status = None
    friendship_id = None
    
    try:
        friendship = Friendship.objects.get(
            (Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user))
        )
        friendship_status = friendship.status
        friendship_id = friendship.id
    except Friendship.DoesNotExist:
        pass
    
    # Get the user's liked and disliked movies (only visible to friends)
    liked_movies = []
    disliked_movies = []
    
    if is_friend or request.user == user:
        liked_reactions = MovieReaction.objects.filter(
            user=user, 
            reaction_type='like'
        ).select_related('movie')
        
        disliked_reactions = MovieReaction.objects.filter(
            user=user, 
            reaction_type='dislike'
        ).select_related('movie')
        
        liked_movies = [reaction.movie for reaction in liked_reactions]
        disliked_movies = [reaction.movie for reaction in disliked_reactions]
    
    context = {
        'profile_user': user,
        'liked_movies': liked_movies,
        'disliked_movies': disliked_movies,
        'is_friend': is_friend,
        'friendship_status': friendship_status,
        'friendship_id': friendship_id,
        'is_self': request.user == user
    }
    
    return render(request, 'users/view_profile.html', context)

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

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    
    if query:
        # Search for users by username
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        
        # Get friendship status for each user
        user_data = []
        for user in users:
            friendship_status = None
            friendship_id = None
            
            try:
                friendship = Friendship.objects.get(
                    (Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user))
                )
                friendship_status = friendship.status
                friendship_id = friendship.id
            except Friendship.DoesNotExist:
                pass
                
            user_data.append({
                'user': user,
                'friendship_status': friendship_status,
                'friendship_id': friendship_id
            })
    else:
        user_data = []
    
    return render(request, 'users/search_users.html', {'user_data': user_data, 'query': query})

@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    # Check if friendship already exists
    if Friendship.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
    ).exists():
        messages.info(request, 'A friendship request already exists with this user.')
        return redirect('users:search_users')
    
    # Create friendship request
    Friendship.objects.create(
        sender=request.user,
        receiver=receiver,
        status='pending'
    )
    
    messages.success(request, f'Friend request sent to {receiver.username}!')
    return redirect('users:search_users')

@login_required
def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, receiver=request.user)
    friendship.status = 'accepted'
    friendship.save()
    
    messages.success(request, f'You are now friends with {friendship.sender.username}!')
    return redirect('users:profile')

@login_required
def reject_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, receiver=request.user)
    friendship.status = 'rejected'
    friendship.save()
    
    messages.info(request, f'Friend request from {friendship.sender.username} declined.')
    return redirect('users:profile')

@login_required
def remove_friend(request, friendship_id):
    # First try to get the friendship
    friendship = get_object_or_404(Friendship, id=friendship_id, status='accepted')
    
    # Check if the user is part of this friendship
    if friendship.sender != request.user and friendship.receiver != request.user:
        messages.error(request, "You don't have permission to remove this friendship.")
        return redirect('users:friend_list')
    
    other_user = friendship.receiver if friendship.sender == request.user else friendship.sender
    friendship.delete()
    
    messages.info(request, f'You are no longer friends with {other_user.username}.')
    return redirect('users:friend_list')

@login_required
def friend_list(request):
    # Get accepted friends
    friendships = Friendship.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        status='accepted'
    ).select_related('sender', 'receiver')
    
    friends = []
    for friendship in friendships:
        if friendship.sender == request.user:
            friends.append({
                'user': friendship.receiver,
                'friendship_id': friendship.id
            })
        else:
            friends.append({
                'user': friendship.sender,
                'friendship_id': friendship.id
            })
    
    return render(request, 'users/friend_list.html', {'friends': friends})
