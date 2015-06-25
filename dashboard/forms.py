from django import forms
#from django.contrib.auth.models import User
from dashboard.models import Classroom
from models import User
from django.utils.translation import ugettext_lazy as _

class UploadFileForm(forms.Form):
    file = forms.FileField()


class ChooseClassForm(forms.Form):
    # class_id = forms.ModelChoiceField(Classroom.objects.values_list('id_class', flat=True), empty_label='Select Class')
    idquery = Classroom.objects.values_list('id_class', flat=True)
    idquery_choices = [('', 'Select Class')] + [(id, id) for id in idquery]
    class_id = forms.ChoiceField(idquery_choices, required=False, widget=forms.Select())

class CreateUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Placeholder':'Username'}) ,required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Password'}) ,required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Confirm your Password'}) ,required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'type':'email', 'Placeholder':'Email Address'}) ,required=True)
    
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label=''
    
    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        exclude = ('username.help_text', 'password2.help_text')
        
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')
        