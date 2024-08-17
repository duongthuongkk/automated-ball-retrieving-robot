
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')
def appVideo(request):
    return render(request, 'video.html')