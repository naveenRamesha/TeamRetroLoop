from django.urls import path
from feedback import views
urlpatterns = [path("", views.collection), path("<int:card_id>/", views.detail)]
