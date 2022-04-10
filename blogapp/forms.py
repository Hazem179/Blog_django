from django import forms
from taggit.forms import TagField
from .models import Comment,Post

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=32)
    email = forms.EmailField()
    to = forms.EmailField()
    comment = forms.CharField(required=False,widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name','email','body')


class SearchForm(forms.Form):
    query = forms.CharField()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','body','status','tags','author')
