from django.urls import path

from teams import views


urlpatterns = [
    path("", views.team_collection, name="team-collection"),
    path("<int:team_id>/", views.team_detail, name="team-detail"),
    path("<int:team_id>/members/", views.membership_collection, name="membership-collection"),
    path(
        "<int:team_id>/members/<int:user_id>/",
        views.membership_detail,
        name="membership-detail",
    ),
]

