from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone

import json
import numpy as np 
from PIL import Image
import os
import io
from base64 import b64encode

from .image_to_pixels import resize, to_pixels, add_grid


from .models import User, Picture, Tag
from .forms import RegisterUserForm

# Where pictures are stored:
PATH_PICTURES = "./pixelpictures/static/pixelpictures/pictures"

def index(request):
    # Default values of search and sort:
    search = ''
    if request.GET.get("search"):
        search = request.GET.get("search")
        tags = Tag.objects.filter(tag__contains=search)
        all_pictures = Picture.objects.filter(tags__in=tags, public=True).distinct()
        
    else:
        all_pictures = Picture.objects.filter(public=True)

    if request.GET.get("sort"):
        sort = request.GET.get("sort")
    else:
        sort = 'new'

    if sort == 'views':
        all_pictures = all_pictures.order_by('-views')
    else:
        all_pictures = all_pictures.order_by('-timestamp')

    paginator = Paginator(all_pictures, 20)
    page_number = request.GET.get('page')
    page_pictures = paginator.get_page(page_number)

    return render(request, "pixelpictures/index.html", {
        "pictures": page_pictures,
        "search_value": search,
        "sort_value": sort
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "pixelpictures/login.html", {
                'message': "Incorrect username or password."
            })
        
    return render(request, "pixelpictures/login.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    form = RegisterUserForm()

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))

    return render(request, "pixelpictures/register.html", {
        'form': form
    })

def create(request):
    return render(request, "pixelpictures/create.html")

def view_picture(request, key):
    try:
        picture = Picture.objects.get(pk=key)
    except Picture.DoesNotExist:
        return HttpResponse("This picture does not exists.")

    if picture.user != request.user:
        if not picture.public:
            return HttpResponse("You do not have access to this picture.")
        picture.views += 1
        picture.save()

    return render(request, "pixelpictures/view_picture.html", {
        'picture': picture
    })

def modify_picture(request, key):
    try:
        picture = Picture.objects.get(pk=key)
    except Picture.DoesNotExist:
        return HttpResponse("This picture does not exists.")

    if picture.user != request.user: 
        return HttpResponse("You cannot modify this picture.")

    height = len(picture.image)
    width = len(picture.image[0])

    return render(request, "pixelpictures/create.html", {
        'picture': picture,
        'width': width,
        'height': height
    })

def user_pictures(request):
    if not request.user.is_authenticated:
        return HttpResponse("Login required.")
    
    user = request.user
    private_pictures = Picture.objects.filter(user=user, public=False).order_by('-timestamp')
    public_pictures = Picture.objects.filter(user=user, public=True).order_by('-timestamp')

    return render(request, "pixelpictures/user_pictures.html", {
        "private": private_pictures,
        "public": public_pictures
    })

# API

def update_tags(picture, new_tags):
    # picture is Picture instance, new_tags is a list of tags
    current_tags = [row.tag for row in Tag.objects.filter(picture=picture)]

    for current_tag in current_tags:
        if current_tag not in new_tags:
            Tag.objects.get(tag=current_tag, picture=picture).delete()
    
    for new_tag in new_tags:
        if new_tag not in current_tags:
            Tag.objects.create(picture=picture, tag=new_tag)
        

def save_image(request):
    if request.method != 'POST' and request.method != 'PUT':
        return JsonResponse({"error": "POST or PUT request required"}, status=400)

    data = json.loads(request.body)
    new_image = data.get("image")
    public = data.get("public")
    tags = data.get("tags")
    palette = data.get("palette")
    new_timestamp = timezone.now()
    
    if request.method == 'POST':

        if not request.user.is_authenticated: 
            return JsonResponse({"message": "You have to log in to save a picture."}, status=200)

        picture = Picture.objects.create(
            image = new_image,
            user = request.user,
            public = public,
            palette = palette,
            timestamp = new_timestamp
        )
        update_tags(picture, tags)
        picture.save()

        prev_timestamp = new_timestamp

    elif request.method == 'PUT':

        key = data.get("key")

        try:
            picture = Picture.objects.get(pk=key)
            prev_timestamp = picture.timestamp

            # Only who created the picture can modify it
            if request.user != picture.user:
                return JsonResponse({
                    "error": "Cannot modify a picture not created by you."
                }, status=400)

            picture.image = new_image
            picture.public = public
            picture.palette = palette
            picture.timestamp = new_timestamp
            update_tags(picture, tags)
            picture.save()
        except Picture.DoesNotExist:
            return JsonResponse({
                "error": f"Picture with primary key {key} does not exists."
            }, status=400)
    
    # Store picture or modified picture in pictures folder.
    height = len(new_image)
    width = len(new_image[0])
    image = Image.fromarray(np.array(new_image).astype(np.uint8)).resize((width * 18, height * 18), resample=Image.NEAREST)

    if os.path.isfile(f"{PATH_PICTURES}/{picture.pk}_{prev_timestamp.strftime('%Y%m%d_%H%M%S')}.png"):
        os.remove(f"{PATH_PICTURES}/{picture.pk}_{prev_timestamp.strftime('%Y%m%d_%H%M%S')}.png")

    image.save(f"{PATH_PICTURES}/{picture.pk}_{new_timestamp.strftime('%Y%m%d_%H%M%S')}.png")

    return JsonResponse({"message": "Picture saved correctly.", "key": picture.pk}, status=200)
    
def delete_picture(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)
    key = data.get("key")

    try: 
        picture = Picture.objects.get(pk=key)
    except Picture.DoesNotExist:
        return JsonResponse({
                    "message": "This picture does not exists."
                }, status=400)
    
    if request.user != picture.user:
         return JsonResponse({
                    "message": "You cannot delete a picture that is not yours!"
                }, status=400)
    
    os.remove(f"{PATH_PICTURES}/{picture.pk}_{picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png")
    picture.delete()
    return JsonResponse({
        "message": "Picture deleted successfully."
    }, status=200)

def resize_image(request):

    if request.method == "POST":

        image_src = request.FILES['img']
        height = int(request.POST['height'])
        width = int(request.POST['width'])

        if height <= 0 or width <= 0:
            return JsonResponse({"error": "Height and width cannot be negative."}, status=400)

        try:
            image = Image.open(image_src)
        except: 
            return JsonResponse({"error": "Not supported file format."}, status=400)

        resized_image = np.array(resize(width, height, image))

        return JsonResponse({"sample_image": resized_image.tolist()}, status=200)

    return HttpResponseRedirect(reverse('create'))

def image_to_pixels(request):

    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)
        
    data = json.loads(request.body)
    image = data.get('image')
    palette = data.get('palette')

    pixels_image = to_pixels(image, palette)

    return JsonResponse({"pixels_image": pixels_image}, status=200)

def download_options(request): 

    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    key = data.get('key')
    start_row = int(data.get('start_row'))
    start_col = int(data.get('start_col'))
    dir_rows = data.get('dir_rows')
    dir_cols = data.get('dir_cols')
    grid_color = tuple(data.get('grid_color'))
    size_cell = int(data.get('size_cell'))
    step = int(data.get('step'))

    picture = Picture.objects.get(pk=key)

    image_with_grid = add_grid(Image.open(f"{PATH_PICTURES}/{picture.pk}_{picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png"), start_row, start_col, dir_rows, dir_cols, grid_color, size_cell, step)
    # Encode image data in base64 https://stackoverflow.com/a/70849754/21044513
    image_io = io.BytesIO()
    image_with_grid.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

    return JsonResponse({'source': dataurl}, status=200)
        

