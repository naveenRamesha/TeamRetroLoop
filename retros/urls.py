from django.urls import path

from retros import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.retro_collection, name="retro-collection"),
    path("<int:retro_id>/lobby/", views.lobby, name="retro-lobby"),
    path("<int:retro_id>/reveal/", views.reveal, name="retro-reveal"),
    path("<int:retro_id>/advance/", views.advance_retro, name="retro-advance"),
]
