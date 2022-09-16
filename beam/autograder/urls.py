from django.urls import path
from . import views

app_name = 'grader'
urlpatterns = [
    path('', views.GroupList.as_view(), name='group_list'),
    path('groups/<int:group_id>', views.StudentList.as_view(), name='student_list'),
    path('groups/<int:group_id>/<int:stud_id>/', views.student_personal_view, name='student_personal'),
]
