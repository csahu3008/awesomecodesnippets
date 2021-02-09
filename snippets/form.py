from .models import CustomUser,Snippet
from django import forms
from pygments.styles import get_all_styles


STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

        
class SnippetCreateForm(forms.ModelForm):
    class Meta:
        model=Snippet
        exclude=('coder',)
        widgets = { 
            'title': forms.TextInput(attrs={'class': 'input'}),
            'code': forms.Textarea(attrs={'class': 'textarea'}),
            'tags':forms.TextInput(attrs={'class': 'input'}),
            'language':forms.Select(attrs={'class': 'select'}),
            'style':forms.Select(attrs={'class': 'select'}),
                
        }

class StyleForm(forms.Form):
    style = forms.ChoiceField(choices=STYLE_CHOICES,widget=forms.widgets.Select(attrs={"class":"style"}))
    dark_mode=forms.BooleanField(widget=forms.widgets.CheckboxInput( attrs={"class":"dark_mode"}) )
    lines_display=forms.BooleanField(widget=forms.widgets.CheckboxInput( attrs={"class":"lines_display"}) )



from allauth.account.forms import SignupForm
class MyCustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(required=True)
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Name'
        })
 
    def save(self, request):
        name = self.cleaned_data.pop('name')
        user = super(MyCustomSignupForm, self).save(request)
        return user
