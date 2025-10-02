from django import forms
from . models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'content']
        labels = {'content': 'Post Content   ', 'image': 'Image (optional)'}
        widgets = {'content': forms.Textarea(attrs={'rows':4, 'cols':60, 'placeholder':'text content'})}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']
        labels = {'text': 'Add a comment'}
        widgets = {'text': forms.Textarea(attrs={'rows':1, 'cols':60})}


