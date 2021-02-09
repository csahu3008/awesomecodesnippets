from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=('detail',)
        widgets = { 
            'detail': forms.Textarea(attrs={'placeholder': 'Message !'}),
        }