from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from .models import Group, Student
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

class GroupList(generic.ListView):
    model = Group

    template_name = "RC_beam/group_list.html"
    context_object_name = "group_list"
    # there is no need to specify two above variables; Django uses them by default


class StudentList(generic.ListView):
    model = Student

    def get_group_id(self):
        return self.kwargs['group_id']

    def get_queryset(self):
        """ Return a list of students from group with given 'group_id' """
        group_id = self.get_group_id()
        return Student.objects.filter(group_id=group_id)

    def get_context_data(self, **kwargs):
        group_id = self.get_group_id()
        context = super(StudentList, self).get_context_data(**kwargs)
        context["group_id"] = group_id
        context["group_name"] = Group.objects.filter(pk=group_id)[0]
        return context


@login_required
def student_personal_view(request):
    user_id = request.user.pk
    student = Student.objects.get(user_id=user_id)
    student_id = student.pk
    student_name = student.full_name
    group_id = student.group_id
    group = Group.objects.get(pk=group_id)
    group_name = group.group_name
    return HttpResponse(f"Hello, {student_name} from {group_name}")
