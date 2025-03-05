from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('', views.home_redirect, name='home_redirect'),
    path('catalogue', views.catalogue, name='catalogue'),
    path('catalogue', views.catalogue_redirect, name='catalogue_redirect'),
    path('profile', views.profile, name='profile'),
    path('profile', views.profile_redirect, name='profile_redirect'),
    path('login', views.login_view, name='login'),
    path('login', views.login_redirect, name='login_redirect'),
    path('register', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('confirmRegistration', views.confirmRegistration, name='confirmRegistration'),
    path('successfulVerification', views.successfulVerification, name='successfulVerification'),
    path('password_reset/', views.password_reset1, name='password_reset1'),
    path('password_reset/', views.password_reset_redirect, name='password_reset1_redirect'),
    path('password_reset/done1/', views.password_reset_done1, name='password_reset_done1'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm1, name='password_reset_confirm1'),
    path('reset/done/', views.password_reset_complete1, name='password_reset_complete1'),
    path('book/<int:book_id>/', views.book_details, name='book_details'),
    path('reserve_book/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('reserve_book/notLogged', views.reserve_not_logged, name='reserve_not_logged'),
    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('profile/settings', views.profile_settings_view, name='profile_settings_view'),
    path('profile/reviews', views.profile_reviews_view, name='profile_reviews_view'),
    path('cancel_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('profile/reviews/export/', views.export_to_excelReview, name='export_to_excelReview'),
    path('profile/reservations/export/', views.export_to_excelReservation, name='export_to_excelReservation'),

]
