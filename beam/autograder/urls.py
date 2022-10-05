from django.urls import path
from . import views

app_name = 'grader'
urlpatterns = [
    path('redirect/', views.redirect, name='redirect'),
    path('user/<str:user_name>/', views.StudentPersonalView.as_view(), name='student_personal'),
]
