from django import forms
from django.contrib import auth
#from django.contrib.auth.models import User
from dashboard.models import Classroom
from dashboard.models import User
from django.contrib.auth.forms import PasswordChangeForm

class UploadFileForm(forms.Form):
    file = forms.FileField()
    
    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        
        self.fields['file'].label=''

class ChooseClassForm(forms.Form):
    # class_id = forms.ModelChoiceField(Classroom.objects.values_list('id_class', flat=True), empty_label='Select Class')
    idquery = Classroom.objects.values_list('id_class', flat=True)
    idquery_choices = [('', 'Select Class')] + [(id, id) for id in idquery]
    class_id = forms.ChoiceField(idquery_choices, required=False, widget=forms.Select())

user_roles = (
              ('Admin', 'Admin'),
              ('Teacher', 'Teacher'),
              ('Director', 'Director')
            )

class CreateUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Placeholder':'Username'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Password'}) ,required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Confirm your Password'}) ,required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'type':'email', 'Placeholder':'Email Address'}) ,required=True)
    
    token = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Placeholder':'Token'}), required=True)
    
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'email', 'password1', 'password2', 'token']:
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
        
class CustomChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Current Password'}) ,required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'New Password'}) ,required=True)
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Confirm your New Password'}) ,required=True)
    
    def __init__(self, *args, **kwargs):
        super(CustomChangeForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].label=''

class CustomSetPasswordForm(auth.forms.SetPasswordForm):
    
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Type your new Password'}), required=True)
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type':'password', 'Placeholder':'Confirm your new Password'}), required=True)
        
class CustomPasswordResetForm(auth.forms.PasswordResetForm):
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'Placeholder':'Email'}))

class RequestNewTokenForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'type':'email', 'Placeholder':'Email Address'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'Placeholder':'Enter a message explaining Who you are.'}) ,required=True)
    
    def __init__(self, *args, **kwargs):
        super(RequestNewTokenForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['email', 'description']:
            self.fields[fieldname].label=''
            
class GenerateTokenForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'type':'email', 'Placeholder':'Email Address'}), required=True)
    role = forms.ChoiceField(choices=user_roles, widget=forms.Select(attrs={'class':'form-control'}), required=True)
    class_id = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Placeholder':'Class ID'}))
    school_id = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Placeholder':'School ID'}))
    
    def __init__(self, *args, **kwargs):
        super(GenerateTokenForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['email', 'class_id']:
            self.fields[fieldname].label=''
    