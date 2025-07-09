from django.urls import path
from bet_api.views import UserRegisterView, LoginView, UserProfileView, Usersearch,  GoogleAuthView
from bet_api.views.notification_views import NotificationListView, NotificationMarkReadView
from bet_api.views.transaction_views import TransactionListView

urlpatterns = [
    path('signup/', UserRegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('search-users/', Usersearch.as_view()),
    path('google-auth/', GoogleAuthView.as_view()),
    path('notifications/', NotificationListView.as_view()),
    path('notifications/<int:notification_id>/read/', NotificationMarkReadView.as_view()),
    path('transactions/', TransactionListView.as_view()),
]
