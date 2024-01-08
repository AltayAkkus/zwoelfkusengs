from django.urls import path
from .views import register, user_login, user_logout, index
from .views import create_group, join_group, group_detail, generate_token, group_admin, delete_token, leave_group
from .views import create_article, article_detail
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import delete_article, create_rental, delete_rental

urlpatterns = [
    # ... other paths ...
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', index, name='index'),
    path('create-group/', create_group, name='create_group'),
    path('join-group/', join_group, name='join_group'),
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('group/<int:group_id>/admin', group_admin, name='group_admin'),
    path('generate-token/<int:group_id>/', generate_token, name='generate_token'),
    path('delete-token/<int:token_id>/', delete_token, name="delete_token"),
    path('leave-group/<int:group_id>/', leave_group, name='leave_group'),
    path('create-article/<int:group_id>/', create_article, name='create_article'),
    path('group/<int:group_id>/article/<int:article_id>/', article_detail, name='article_detail'),
    path('delete-article/<int:article_id>', delete_article, name='delete_article'),
    path('create-rental/<int:article_id>/', create_rental, name='create_rental'),
    path('delete-rental/<int:rental_id>/', delete_rental, name='delete_rental'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
