from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()

forms.ClearableFileInput.initial_text = 'Текущий файл'
forms.ClearableFileInput.input_text = 'Изменить'
forms.ClearableFileInput.clear_checkbox_label = 'Удалить'


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class RegistrationForm(UserCreationForm):
    email = forms.CharField(
        required=True,
        label='Email',
        help_text='Введите email адрес',
        widget=forms.EmailInput(attrs={'type': 'email'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if '@' not in email or '.' not in email:
            raise forms.ValidationError('Введите корректный email адрес')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже есть')

        return email
