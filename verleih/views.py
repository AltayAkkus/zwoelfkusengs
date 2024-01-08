from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, JoinGroupForm
from .models import CustomUser
from .models import Group, InviteToken, Article, Rental
from .forms import CreateGroupForm, GenerateTokenForm, generate_random_token, CreateArticleForm
from django.contrib.auth.decorators import login_required
import random, string
from datetime import datetime
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("register is valid!")
            user = form.save()
            login(request, user)
            return redirect('index')  # replace 'home' with the URL name of your home page
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        print("here")
        if form.is_valid():
            print("valid")
            user = form.get_user()
            login(request, user)
            # Check if the user is active and logged in
            if user.is_active:
                print("valid user")
                # Successful login
                return redirect('index')  # replace 'index' with the URL name of your home page
            else:
                # Inactive user, handle accordingly
                print("invalid user")
                return render(request, 'registration/login.html', {'form': form, 'error_message': 'Account is not active.'})
        else:
            print("invalid login details")
            # Invalid login details, handle accordingly
            return render(request, 'registration/login.html', {'form': form, 'error_message': 'Invalid email or password.'})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')  # replace 'home' with the URL name of your home page

def index(request):
    if request.user.is_authenticated:
        # User is logged in, render template for authenticated users
        groups = Group.objects.filter(members=request.user)
        context = {'groups': groups}
        return redirect('join_group')
    else:
        # User is not logged in, render template for non-authenticated users
        return render(request, 'landing/index.html')
@login_required
def create_group(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            group.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = CreateGroupForm()
    return render(request, 'internal/group_new.html')

@login_required
def join_group(request):
    invalidToken = False

    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            try:
                invite_token = InviteToken.objects.get(token=token, is_revoked=False)
                group = invite_token.group
                group.members.add(request.user)
                group.save()
                return redirect('group_detail', group_id=group.id)
            except InviteToken.DoesNotExist:
                print("token invalid")
                form.add_error('token', 'Invalid token or token has been revoked.')
                invalidToken = True
    else:
        form = JoinGroupForm()

    return render(request, 'internal/group_join.html', {'form': form, 'invalidToken': invalidToken})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    print(request.user.id)
    is_member =  group.members.filter(id=request.user.id).exists()
    articles = Article.objects.filter(group=group)
    if is_member:
        print("is member")
        context = {
            'group': group,
            'articles': articles,
        }
        if request.user == group.admin:
            print("is admin!")
            context['invite_tokens'] = InviteToken.objects.filter(group=group)
        print(context)
        return render(request, 'internal/group_detail.html', context)
    else:
        return redirect('index')

@login_required
def group_admin(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    context = {
        'group': group,
    }
    if request.user == group.admin:
        context['invite_tokens'] = InviteToken.objects.filter(group=group)
        return render(request, 'internal/group_admin.html', context)
    else:
        return redirect('group_detail', group_id=group.id)

@login_required
def generate_token(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user != group.admin:
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
            token = generate_random_token(64)
            InviteToken.objects.create(token=token, group=group)
            return redirect('group_admin', group_id=group.id)
    return redirect('group_admin', group_id=group.id)

def generate_random_token(length):
    # Generate a random token using letters and digits
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@login_required
def delete_token(request, token_id):
    # Retrieve the invite token
    invite_token = get_object_or_404(InviteToken, pk=token_id)

    # Check if the user is the admin of the group associated with the token
    if request.user != invite_token.group.admin:
        return redirect('group_detail', group_id=invite_token.group.id)

    # Delete the token
    invite_token.delete()

    return redirect('group_admin', group_id=invite_token.group.id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    # Check if the user is the admin of the group
    if request.user == group.admin:
        # If the user is the admin, delete the group
        group.delete()
        return redirect('index')  # Replace with the appropriate URL

    # If the user is not the admin, remove the user from the group
    if request.user in group.members.all():
        group.members.remove(request.user)

    return redirect('index')

@login_required
def create_article(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.user != group.admin:
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        print("post")
        form = CreateArticleForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            article = form.save(commit=False)
            article.group = group
            article.save()
    return redirect('group_admin', group_id=group.id)

@login_required
def article_detail(request, group_id, article_id):
    group = get_object_or_404(Group, pk=group_id)
    article = get_object_or_404(Article, pk=article_id)
    rentals = Rental.objects.filter(article=article).order_by('-start_date')
    if request.user not in group.members.all():
        return redirect('index')

    context = {
        'group': group,
        'article': article,
        'rentals': rentals
    }
    if request.session.get('error'):
        context['error'] = request.session['error']
        del request.session['error']
        
    return render(request, 'internal/article_detail.html', context)

@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    group = article.group
    if request.user != group.admin:
        return redirect('group_detail', group_id=group.id)
    article.delete()
    return redirect('group_admin', group_id=group.id)

@login_required
def create_rental(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    group = article.group
    if request.user not in group.members.all():
        return redirect('index')
    if request.method == 'POST':
        start_date_string = request.POST.get("start", "")
        start_date = datetime.strptime(start_date_string,  "%m/%d/%Y")
        start_date = timezone.make_aware(start_date)
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_string = request.POST.get("end", "")
        end_date = datetime.strptime(end_date_string,  "%m/%d/%Y")
        end_date = timezone.make_aware(end_date)
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
        # If the article is not already rented, create a new rental. If it is rented, return an error message. Article has no "is_rented" method, use a filter. There can be rentals to article, but it remains free. Check if todays date falls within a rental of the article.
        if not Rental.objects.filter(article=article, start_date__lte=start_date, end_date__gte=end_date).exists():

            rental = Rental.objects.create(start_date=start_date, end_date=end_date, user=request.user, article=article)
            rental.save()
            return redirect('article_detail', group_id=group.id, article_id=article.id)
        else:
            # return a redirect that tells article detail that an error occured
            request.session['error'] = "Article already rented"
            return redirect('article_detail', group_id=group.id, article_id=article.id)            
    return redirect('article_detail', group_id=group.id, article_id=article.id)

@login_required
def delete_rental(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id)
    group = rental.article.group
    if request.user != rental.user and request.user != group.admin:
        return redirect('article_detail', group_id=group.id, article_id=rental.article.id)
    rental.delete()
    return redirect('article_detail', group_id=group.id, article_id=rental.article.id)