from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    def __str__(self):
        return self.username
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_of_groups')
    members = models.ManyToManyField(CustomUser, related_name='members_of_groups')

class InviteToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_revoked = models.BooleanField(default=False)

# Article Model, that has a name, and a description, and a maximum rental time
class Article(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_rental_time = models.DurationField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='article_pictures', blank=True)

# Rental Model, that has a start and end date, and a user and an article
class Rental(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
