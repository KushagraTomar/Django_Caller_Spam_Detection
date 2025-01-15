from django.urls import path
from .views import UserRegistrationView, UserLoginView, MarkPhoneNumberAsSpamView, SearchUserByUserNameView, SearchUserByPhoneNumberView, CreateContactView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('mark_spam/', MarkPhoneNumberAsSpamView.as_view(), name='mark-spam'),
    path('search-name/', SearchUserByUserNameView.as_view(), name='search-user-by-name'),
    path('search-phone/', SearchUserByPhoneNumberView.as_view(), name='search-user-by-phone'),
    path('create-contact/', CreateContactView.as_view(), name='create-contact'),
]