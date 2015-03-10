from django import forms
from django.contrib.auth.models import User
from dashboard.models import Classroom


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ChooseClassForm(forms.Form):
    class_id = forms.ModelChoiceField(Classroom.objects.values_list('id_class', flat=True), empty_label='Select Class')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'groups')