from django.urls import path
from .views import trip_plan_view

urlpatterns = [
    path('plan/', trip_plan_view, name='trip-plan'),
]