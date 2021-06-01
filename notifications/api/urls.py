from django.urls import path

from .views import getNotifications, markAllAsSeen, markAsSeen

urlpatterns = [
    path("api/notifications/", getNotifications),
    path("api/notifications/<int:pk>/", markAsSeen),
    path("api/notifications/seen/", markAllAsSeen),
]
