from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    email = forms.EmailField(required=True, error_messages={'required': 'Email is required.'})
    first_name = forms.CharField(max_length=30, required=True, error_messages={'required': 'First name is required.'})
    last_name = forms.CharField(max_length=150, required=True, error_messages={'required': 'Last name is required.'})
    phone_number = forms.CharField(max_length=15, required=True, validators=[phone_regex],
                                   error_messages={'required': 'Phone number is required.'})
    country = forms.CharField(max_length=100, required=True, error_messages={'required': 'Country is required.'})
    city = forms.CharField(max_length=100, required=True, error_messages={'required': 'City is required.'})

    class Meta:
        model = User

        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'country',
                  'city']
        error_messages = {
            'username': {'required': 'Username is required.', 'unique': 'A user with that username already exists.'},
            'password1': {'min_length': 'Password must be at least 8 characters long.'},
            'password2': {'mismatch': 'The two password fields didn’t match.'},
            'country': {'required': 'Username is required.', 'unique': 'A user with that username already exists.'},
        }

    custom_error_messages = {'invalid_country': 'Country name must start with a capital letter.',
                             'invalid_city': 'City name must start with a capital letter.',
                             'invalid_first_name': 'First name must start with a capital letter.',
                             'invalid_last_name': 'Last name must start with a capital letter.'
                             }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_country(self):
        country = self.cleaned_data.get('country')

        if country and not country[0].isupper():
            raise ValidationError(self.custom_error_messages['invalid_country'],
                                  code='invalid_country')
        return country

    def clean_city(self):
        city = self.cleaned_data.get('city')

        if city and not city[0].isupper():
            raise ValidationError(self.custom_error_messages['invalid_city'],
                                  code='invalid_city')
        return city

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name[0].isupper():
            raise ValidationError(
                self.custom_error_messages['invalid_first_name'], code='invalid_first_name')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name[0].isupper():
            raise ValidationError(
                self.custom_error_messages['invalid_last_name'],
                code='invalid_last_name')
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False

        if commit:
            user.save()

        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': self.cleaned_data['phone_number'],
                'country': self.cleaned_data['country'],
                'city': self.cleaned_data['city']
            }
        )

        if not created:
            user_profile.phone_number = self.cleaned_data['phone_number']
            user_profile.country = self.cleaned_data['country']
            user_profile.city = self.cleaned_data['city']
            user_profile.save()

        return user
