from django import forms
from .models import Profile
import pytz
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class RecommendationFilterForm(forms.Form):
    category = forms.ChoiceField(
        choices=[
            ('all', 'All'),
            ('stress_relief', 'Stress Relief'),
            ('sleep', 'Sleep'),
            ('focus', 'Focus'),
            ('anxiety_relief', 'Anxiety Relief'),    
            ('motivation', 'Motivation'),          
            ('mindfulness', 'Mindfulness'),       
        ],
        initial='all',
        required=False,
        widget=forms.Select(attrs={
    'onchange': 'this.form.submit();',
    'class': 'get-select'  
})
    )


class AddToPlannerForm(forms.Form):
    scheduled_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    scheduled_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label='Your Bio', required=False)
    profile_pic = forms.ImageField(label='Profile Picture', required=False)
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones], label='Timezone', initial='UTC')

    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio', 'timezone']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email Address"
        self.fields['username'].label = "Username"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
        


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if not user.username:
            user.username = self.cleaned_data['email']
        if commit:
            user.save()
            self.save_m2m()
        return user