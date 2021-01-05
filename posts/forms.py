from django import forms

from .models import Group, Post


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
