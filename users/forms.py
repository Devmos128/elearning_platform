from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StatusUpdate


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)
    profile_picture = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 
                 'profile_picture', 'bio', 'date_of_birth', 'phone_number', 'password1', 'password2')


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What\'s on your mind?'}),
        }


class UserSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Search for users...'})
    )
    user_type = forms.ChoiceField(
        choices=[('', 'All'), ('student', 'Student'), ('teacher', 'Teacher')],
        required=False
    )
