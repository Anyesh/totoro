from django.urls import path

from .views import (
    acceptFriendRequest,
    deleteFriendRequest,
    getFriendRequests,
    getFriends,
    getFriendSuggestions,
    sendFriendRequest,
)

urlpatterns = [
    # auth token required in header for all requests
    path("friends/", getFriends),  # GET request
    path("friends/requests/", getFriendRequests),  # GET request
    path("friends/request/send/", sendFriendRequest),  # POST request
    path("friends/request/accept/", acceptFriendRequest),  # PUT request
    path("friends/request/delete/<int:pk>/", deleteFriendRequest),  # DELETE request
    path("friends/suggestions/", getFriendSuggestions),  # GET request
    # path('friend/unfriend',''), #DELETE request
]
