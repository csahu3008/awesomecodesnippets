from .models import CustomUser,Snippet
from django import forms
from pygments.styles import get_all_styles


STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

        
class SnippetCreateForm(forms.ModelForm):
    class Meta:
        model=Snippet
        exclude=('coder',)

class StyleForm(forms.Form):
    style = forms.ChoiceField(choices=STYLE_CHOICES,widget=forms.widgets.Select(attrs={"class":"style"}))
    dark_mode=forms.BooleanField(widget=forms.widgets.CheckboxInput( attrs={"class":"dark_mode"}) )
    lines_display=forms.BooleanField(widget=forms.widgets.CheckboxInput( attrs={"class":"lines_display"}) )