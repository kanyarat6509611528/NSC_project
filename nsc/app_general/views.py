from django.http.response import HttpResponse
from django.shortcuts import render
from .models import Phobias
from .models import Add_pb

def home(request):
    return render(request, 'app_general/home.html')

# --------------------------------------------------------------------------- 

def about(request):
    return render(request, 'app_general/about.html')

# --------------------------------------------------------------------------- 

def stat(request):
    phobias = Phobias.objects.all().order_by('name_ENG')
    context = {
        'phobias': phobias
    }
    
    if request.method == 'POST':
        pb_data = request.POST.get('answer')
        if pb_data:
            Add_pb.objects.create(pb_data=pb_data)
    
    return render(request, 'app_general/stat.html', context)