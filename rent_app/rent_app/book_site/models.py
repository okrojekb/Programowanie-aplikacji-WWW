from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=127)
    author = models.CharField(max_length=31)
    available = models.BooleanField()
    pub_date = models.DateField()
    date_added = models.DateField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12, validators=[
        RegexValidator(regex='^\d{9}$', message='Phone number must be 9 digits', code='invalid_phone_number')])
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review_text = models.TextField()
    stars = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'


class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Reservation for {self.book.title} by {self.user.username}"

    def is_valid(self):
        if self.pickup_date >= timezone.now() and self.is_active:
            book = get_object_or_404(Book, id=self.book.id)

            book.available = False
            book.save()
            return True
        else:
            book = get_object_or_404(Book, id=self.book.id)

            book.available = True
            book.save()

            return False


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'stars', 'created_at')
    search_fields = ('book__title', 'user__username')
    list_filter = ('stars', 'created_at')


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'available', 'pub_date', 'date_added')
    search_fields = ('title', 'author')
    list_filter = ('available', 'pub_date')
    ordering = ('-date_added',)
    fields = ('title', 'author', 'available', 'pub_date')
    list_display_links = ('title', 'author')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'country', 'city')
    search_fields = ('user__username', 'phone_number', 'country', 'city')


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reserved_at', 'pickup_date', 'is_active')
    list_filter = ('is_active', 'reserved_at', 'pickup_date')
    search_fields = ('book__title', 'user__username')


admin.site.register(Reservation, ReservationAdmin)

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Book, BookAdmin)

admin.site.register(BookReview, BookReviewAdmin)
