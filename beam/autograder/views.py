from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from .models import Group, Student
from django.urls import reverse_lazy


def test_view(request):
    return HttpResponse("Hello, world!")


class GroupList(generic.ListView):
    model = Group

    template_name = "RC_beam/group_list.html"
    context_object_name = "group_list"
    # there is no need to specify two above variables; Django uses them by default
