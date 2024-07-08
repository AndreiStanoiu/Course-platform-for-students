from django.forms import ModelForm
from licenta.models import Homework, Profile, Feedback, Note, SolvedHomeWork
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class GiveFeedback(ModelForm):
    class Meta:
        model = Feedback
        fields =  ['content']

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']
        
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['fullname', 'user_type', 'is_bachelor', 'is_masters', 'year']


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'file', 'content']


class HomeWorkForm(ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Homework
        fields = ['title', 'due_date', 'file']


class SolvedHomeWorkForm(forms.ModelForm):
    #file = forms.FileField(widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
    class Meta:
        model = SolvedHomeWork
        fields = ['file']