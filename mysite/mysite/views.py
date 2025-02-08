from django.shortcuts import render, redirect

def homepage(request):
    return render(request, 'homepage.html')

def movie(request):
    return render(request, 'movie.html')
