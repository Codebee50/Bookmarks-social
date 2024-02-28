from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from actions.utils import create_action
import redis
from django.conf import settings

#connect to redis
r = redis.Redis(host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)

# Create your views here.
@login_required
def image_ranking(request):
    #get image ranking dictionary

    #zrange is used to obtain the elements in a sorted set
    #Using 0 as the lowest and -1 as the highest score, you are telling Redis to return all elements in the sorted set
    image_ranking = r.zrange('img_ranking', 0, -1, desc=True)[:10]
    print(image_ranking)
    image_ranking_ids = [int(id) for id in image_ranking]

    #get most viewed images
    most_viewed = list(Image.objects.filter(
        id__in=image_ranking_ids
    ))

    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {
        'section': 'images', 
        'most_viewed': most_viewed
    })
@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)#paginate over the images, retireving 8 images per page
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')

    try: 
        images = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver the first page
        images = paginator.page(1)
    except EmptyPage:#page is out of range
        if images_only:
            #if ajax request and page is out of range
            #return an empty page
            return HttpResponse('')
        
        #if page is out of range, return last page of results
        images = paginator.page(paginator.num_pages)


    if images_only:
        return render(request, 'images/image/list_images.html', {'section': 'images', 'images': images})
    
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)

            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass

        return JsonResponse({'status': 'error'})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)

    #incr increaments the value of a given key by 1 and returns the final value
    #the code below increaments the views for the image 
    #e.g image:33:views is a key name and the value is increamented
    total_views = r.incr(f'image:{image.id}:views')

    #increament image ranking by 1
    #zincrby is used to increament the scroe of a member in a sorted set
    #imcreament the score of image.id by 1 in a sorted set of name img_ranking
    r.zincrby('img_ranking', 1, image.id)
    print('increamented')
    return render(request, 
                  'images/image/detail.html', 
                  { 'section': 'images',
                    'image': image, 
                    'total_views': total_views})


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
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')

            #redirect to new created image detail view
            return redirect(new_image.get_absolute_url())
    else:
            #build form with data provided by the bookmarklet via get 
        form = ImageCreateForm(data=request.GET)
            
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})
