from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    body = forms.CharField(required=False,
                           widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Enter your name')
    }))

    email = forms.EmailField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Enter your email')
    }))

    body = forms.CharField(label='', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': _('Type your comment here...'),
        'rows': '4',
        'cols': '50'
    }))

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control rounded',
        'placeholder': _('Search this blog')
    }))
