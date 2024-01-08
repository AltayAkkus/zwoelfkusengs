from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import Group, InviteToken, Article

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email does not exist.')
        return email
        
class JoinGroupForm(forms.Form):
    token = forms.CharField(max_length=100)

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GenerateTokenForm(forms.ModelForm):
    class Meta:
        model = InviteToken
        fields = ['token'] 
class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['name', 'description', 'max_rental_time', 'picture']

def generate_random_token():
    # Generate a random token using letters and digits
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))