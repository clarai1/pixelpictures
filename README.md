# PixelPictures

PixelPictures is a web application developed with Django, that lets users create pixel-art pictures.  
The main purpose of the application is to simplify the generation of pixelated images for creative hobbies, such as crocheting, knitting, cross-stitching, etc.  
It can also be a place to find inspiration by navigating the publicly available pictures created by users.

The particularity of this application is that not only it allows to create a pixelated picture from scratch, but it also allows to upload an image file, choose desired height, width, and colors, and start drawing from a pre-drawn pixelated picture.

## Example:
Uploaded image            |  Converted and adjusted image
:-------------------------:|:-------------------------:
![Mandalorian image](pixelpictures/static/pixelpictures/manda.png)  |  ![Mandalorian pixelated image](pixelpictures/static/pixelpictures/manda_pixelated.png)

# Distinctiveness and Complexity

This project is distinct from all others in the course because the focus is on the elaboration and creation of images.   
In addition to the creative part, the application is also a sort of archive for pixelated images created by the users.

There are essentially two main features of the app:
- the most complex one is the image processing, which includes creating, storing, and downloading images;
- the archive feature makes it easier to navigate through public pictures by sorting and searching.

In the next two sections, these two features are explained in more detail, showing distinctiveness and complexity of the project.

## Image Processing

On the *create* page, the user can create new pixelated pictures. The drawing part is entirely controlled by JavaScript: the image viewed by the user on this page is an HTML table whose cells change color interactively.

To create a pixelated picture, one can choose to start drawing on a prefilled table. In particular, the user can upload an image that is first resized, then modified such that only colors present in the palette chosen by the user appear in the picture. This is done by changing each color in the resized image with the closest color in the palette. The closest color is determined using a weighted euclidean distance for RGB colors.

Saving the picture for the first time creates a Picture object in the database that contains all information related to that picture (image itself as an array, colors palette, user who created it, and public option).
The picture is stored in the database as an array, however, when creating a new picture, a `.png` file in the `static/pixelpictures/pictures` folder is created to easily show the image in the homepage, profile page, or view page.
If something happens to the file, the database still contains the information to generate the image.

Another image processing feature concerns the download of pictures. When viewing the picture, anyone can download it as it is or can apply a grid on it with the count of rows and columns.

The manipulation of images in the back-end is done using Pillow.

## Archive features

When creating a picture, the user can decide to keep it private, and store it only in the personal profile page, or make it public so that everyone can see it in the homepage. In the latter case, adding tags will let the picture appear when the words searched are contained in the tags.

The homepage shows 20 pictures per page and the pictures can be sorted by most recent or by most popular.  
The chronological sorting depends on the timestamp field of the Picture object, which is updated every time a picture is saved.  
The popularity sorting depends on the views value of the Picture object, which is increased by one every time a user, which is not the creator of the picture, views the picture. 

# Structure of the project

The project consists of only one Django app called *pixelpictures*.  
In the `pixelpictures` folder, apart from the default Django files, are present the following files:

- `views.py`: contains all the *view functions* to run the application and the *API* for the JavaScript code to update the page asynchronously.
- `image_to_pixels.py`: contains all the functions to manipulate images in the back-end.
- `models.py`: contains the three models used by the application: 
    - the default `User` model, 
    - the `Picture` model that stores the created pictures with all relevant information, 
    - and the `Tag` model, which stores the tags of each picture and lets the search function be possible.  
- `forms.py`: contains a form to simplify the registration of new users.

Moreover, the `pixelpictures` folder contains the following folders:

### `static/pixelpictures`

which contains: 

- folder `pictures`, where `.png` files representing the pictures in the database are stored.
- JavaScript files: 
    - `drawing.js`: contains functions regarding drawing or getting the image in the HTML table,
    - `options_create.js`: controls all the possible options for an image,
    - `palette.js`: controls the palette of the picture,
    - `to_pixels.js`: contains functions to call the API to manipulate images,
    - `utils.js`: contains functions to convert from hexadecimal format of color to RGB, and to convert from string RGB format to array,
    - `view_picture.js`: controls the view page of pictures and download options.
- Cascading Style Sheet, icon image, and the font for the grid numbers.

### `templates/pixelpictures`

which contains:

- `layout.html`: layout for each HTML page,
- `index.html`: homepage,
- `create.html`: create page,
- `login.html`, `register.html`: to manage users,
- `user_pictures.html`: personal profile page where the user can see all the created pictures,
- `view_picture.html`: view page of a picture.

### `templatetags` 

which contains filters for the Django templates

### `tests`

which contains some tests for the whole application.   
To run them use the command: 

    python manage.py test

# How to run the application

Clone this repository. Navigate in the project folder, and install all requirements:

    pip install -r requirements.txt

To start the application run the following command in the terminal:

    python manage.py runserver





