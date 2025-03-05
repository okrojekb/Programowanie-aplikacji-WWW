# forms.py
from django import forms

from book_site.models import BookReview, Reservation
from book_site.widgets import StarRatingWidget


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New password", min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm password", min_length=8)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview

        fields = ['review_text', 'stars']
        widgets = {'review_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
                   'stars': StarRatingWidget, }

    def is_valid(self):
        if not super().is_valid():
            return False
        cleaned_data = super().clean()

        review_text = cleaned_data.get("review_text")
        stars = cleaned_data.get("stars")
        if not review_text or not stars:
            return False
        return True


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['book']

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')

        if Reservation.objects.filter(book=book).exists():
            raise forms.ValidationError("This book is already reserved.")

        return cleaned_data
