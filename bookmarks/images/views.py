from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm

# Create your views here.

@login_required
def image_create(request):
    if request.method == 'POST':
        #form is sent 
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            #form is valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)

            #Assign current user to the imtem
            new_image.users = request.user
            new_image.save()

            messages.success(request, 'Image added successfully')

            #redirect to new created item detail
            return redirect(new_image.get_absolute_url())
        else:
            #build form with data provided by the bookmarklet via get 
            form = ImageCreateForm(data=request.GET)
            
        return render(request, 'images/image/create.html', {'section': 'images', 'form': form})
