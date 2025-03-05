from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from openpyxl import Workbook

from book_site.create_account_form import UserRegistrationForm
from book_site.forms import SetNewPasswordForm, BookReviewForm
from book_site.models import Book, Reservation, UserProfile
from .models import BookReview


def index(request):
    return render(request, 'book_site/index.html')


def home_redirect(request):
    return HttpResponseRedirect('book_site/')


def profile_redirect(request):
    return HttpResponseRedirect('login')


def login_redirect(request):
    return HttpResponseRedirect('login')


def catalogue_redirect(request):
    return HttpResponseRedirect('catalogue/')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile_redirect')
    else:
        form = AuthenticationForm()
    return render(request, 'book_site/log_panel.html', {'form': form})


@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login_redirect')
    else:
        reservations = Reservation.objects.filter(user=request.user)
        for reservation in reservations:
            reservation.is_valid = reservation.is_valid()
        context = {
            'reservations': reservations,
        }
        return render(request, 'book_site/profile.html', context)


def confirmRegistration(request):
    return render(request, 'book_site/info_email_sent.html')


def successfulVerification(request):
    return render(request, 'book_site/info_verification_success.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
            domain = get_current_site(request).domain
            link = f'http://{domain}/book_site/activate/{uid}/{token}/'
            mail_subject = 'Potwierdź swój e-mail'
            message = render_to_string('book_site/activation_email.html', {
                'user': user,
                'link': link,
            })
            send_mail(mail_subject, message, 'admin@bookToGO.com', [user.email])

            return redirect('confirmRegistration')
    else:
        form = UserRegistrationForm()

    return render(request, 'book_site/sign_up_panel.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('successfulVerification')
    else:
        if user is not None:
            user.delete()
        messages.error(request, "Link is inactive.")
        return redirect('register')


def catalogue(request):
    reservations = Reservation.objects.all()
    for reservation in reservations:
        reservation.is_valid = reservation.is_valid()
    query = request.GET.get('search')
    criteria = request.GET.get('criteria', 'title')
    if query:
        if criteria == 'title':
            books = Book.objects.filter(Q(title__icontains=query))
            paginator = Paginator(books, 10)
        elif criteria == 'author':
            books = Book.objects.filter(Q(author__icontains=query))
            paginator = Paginator(books, 10)
        else:
            books = Book.objects.all()
            paginator = Paginator(books, 10)
    else:
        books = Book.objects.all()
        paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_site/catalogue.html', context={'page_obj': page_obj})


def password_reset_redirect(request):
    return HttpResponseRedirect('password_reset/')


def password_reset1(request):
    error_message = None
    print('start')
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        print('post')
        if form.is_valid():
            email = form.cleaned_data['email']
            print(email)
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = user.pk
                domain = get_current_site(request).domain
                reset_link = request.build_absolute_uri(f'http://{domain}/book_site/reset/{uid}/{token}/')
                send_mail(
                    'Reset your password',
                    f'Click the link to reset your password: {reset_link}',
                    'noreply@mywebsite.com',
                    [email]
                )
                messages.success(request,
                                 'If the email address is associated with an account, we have sent a reset link.')
                return redirect('password_reset_done1')
            except User.DoesNotExist:
                print("except")
                error_message = 'No account found with that email address.'
        else:
            error_message = 'No account found with that email address'
    else:
        form = PasswordResetForm()
    return render(request, 'registration1/password_reset.html', {'form': form,
                                                                 'error_message': error_message})


def password_reset_done1(request):
    return render(request, 'registration1/password_reset_done.html')


def password_reset_confirm1(request, uidb64, token):
    try:
        uid = int(uidb64)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Your password has been successfully reset!')
                return redirect('login_redirect')
        else:
            form = SetNewPasswordForm()

        return render(request, 'registration1/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('password_reset1')


def password_reset_complete1(request):
    return render(request, 'registration1/password_reset_complete.html')


def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = BookReview.objects.filter(book=book)
    review_to_edit = None

    if request.method == 'POST':
        if 'delete_review' in request.POST:
            review_id = request.POST.get('review_id')
            review = get_object_or_404(BookReview, pk=review_id, user=request.user)
            review.delete()
            return redirect('book_details', book_id=book.id)
        else:
            review_id = request.POST.get('review_id')
            if review_id:
                review = get_object_or_404(BookReview, pk=review_id, user=request.user)
                form = BookReviewForm(request.POST, instance=review)
                review_to_edit = review
            else:
                form = BookReviewForm(request.POST)

            user_reviewed = BookReview.objects.filter(book=book, user=request.user).exists()

            if user_reviewed and not review_id:
                form.add_error(None, "You have already reviewed this book.")
            else:
                if form.is_valid():
                    review = form.save(commit=False)
                    review.book = book
                    review.user = request.user
                    review.save()

                    return redirect('book_details', book_id=book.id)
                else:
                    form.add_error(None, "You need to choose a star rating")
    else:
        review_id = request.GET.get('review_id')
        if review_id:
            review = get_object_or_404(BookReview, pk=review_id, user=request.user)
            form = BookReviewForm(instance=review)
            review_to_edit = review
        else:
            form = BookReviewForm()

    context = {
        'book': book,
        'reviews': reviews,
        'form': form,
        'review_to_edit': review_to_edit,
    }
    return render(request, 'book_site/book_details.html', context)


@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if not book.available:
        return render(request, 'book_site/reservation_popup.html', {
            'message': "This book is already reserved"
        })

    reservation = Reservation.objects.create(
        book=book,
        user=request.user,
        pickup_date=timezone.now() + timedelta(days=3)
    )

    book.available = False
    book.save()
    return render(request, 'book_site/reservation_popup.html', {
        'message': f"You have successfully reserved '{book.title} by '{book.author}'.\nYou can pick it up by {reservation.pickup_date.strftime('%Y-%m-%d %H:%M')}.",
    })


def reserve_not_logged(request):
    return render(request, 'book_site/popup_reservation_not_logged.html')


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    book = reservation.book
    book.available = True
    book.save()
    reservation.delete()
    return redirect('profile')


@login_required
def profile_settings_view(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)

    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST' and 'delete_account' in request.POST:
        user.is_active = False
        user.save()
        return redirect('login_redirect')
    return render(request, 'book_site/profile_settings.html', {'user': user, 'profile': profile})


@login_required
def profile_reviews_view(request):
    if not request.user.is_authenticated:
        return redirect('login_redirect')
    else:
        reviews = BookReview.objects.filter(user=request.user)
        context = {
            'reviews': reviews,
        }
        return render(request, 'book_site/profile_reviews.html', context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(BookReview, id=review_id, user=request.user)
    review.delete()
    return redirect('profile_reviews_view')


@login_required
def export_to_excelReview(request):
    if not request.user.is_authenticated:
        return redirect('login_redirect')
    else:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Your Book Reviews'

        headers = ['Book Title', 'Book Author', 'Stars', "Review Text"]
        worksheet.append(headers)

        for obj in BookReview.objects.filter(user=request.user):
            data = [obj.book.title, obj.book.author, obj.stars, obj.review_text]
            worksheet.append(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="your_reviews_data.xlsx"'

        workbook.save(response)
        return response


@login_required
def export_to_excelReservation(request):
    if not request.user.is_authenticated:
        return redirect('login_redirect')
    else:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Your Book Reservations'

        headers = ['Book Title', 'Book Author', 'Status', "Pickup Date"]
        worksheet.append(headers)

        for obj in Reservation.objects.filter(user=request.user):
            data = [obj.book.title,
                    obj.book.author,
                    obj.book.available,
                    obj.pickup_date.replace(tzinfo=None) if isinstance(obj.pickup_date, datetime) else obj.pickup_date
                    ]
            worksheet.append(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="your_reservations_data.xlsx"'

        workbook.save(response)
        return response
