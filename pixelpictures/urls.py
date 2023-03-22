from django.urls import path
from . import views 

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("create", views.create, name="create"),
    path("picture/<key>", views.view_picture, name="view_picture"),
    path("modify/<key>", views.modify_picture, name="modify_picture"),
    path("profile", views.user_pictures, name="user_pictures"),
    path("sample", views.resize_image, name="resize_image"),
    path("save", views.save_image, name="save"),
    path("delete", views.delete_picture, name="delete_picture"),
    path("image_to_pixels", views.image_to_pixels, name="image_to_pixels"),
    path("download", views.download_options, name="download")
]