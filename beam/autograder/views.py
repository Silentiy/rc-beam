from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic, View
from .models import Group, Student, ConcreteStudentAnswers, ConcreteAnswersStatistics
from .forms import ConcreteStudentAnswersForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from autograder.services import validation


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
def redirect(request):
    user_id = request.user.pk
    user_name = request.user.username
    return HttpResponseRedirect(reverse_lazy("grader:student_personal", args=[user_name]))


class StudentPersonalView(View):

    def is_owner(self):
        owner = False
        if self.kwargs["user_name"] == self.request.user.username:
            owner = True
        return owner

    def get_student(self):
        user_name = self.kwargs["user_name"]
        user_id = User.objects.get_by_natural_key(username=user_name)
        return Student.objects.get(user_id=user_id)

    def get_student_id(self):
        student = self.get_student()
        return student.pk

    def get_student_name(self):
        student = self.get_student()
        return student.full_name

    def get_student_group_name(self):
        student = self.get_student()
        group_id = student.group_id
        group = Group.objects.get(pk=group_id)
        return group.group_name

    def get_current_form(self):
        return ConcreteStudentAnswers.objects.filter(student_id=self.get_student_id()).first()

    def get(self, request, **kwargs):
        concrete_answer = self.get_current_form()
        concrete_statistics = ConcreteAnswersStatistics.objects.filter(student_id=self.get_student_id()).first()

        if concrete_statistics is not None:
            concrete_statistics_dict = model_to_dict(concrete_statistics, exclude=["id", "student"])
        else:
            concrete_statistics_dict = dict()

        if concrete_answer is not None:
            form = ConcreteStudentAnswersForm(instance=concrete_answer)
        else:
            form = ConcreteStudentAnswersForm()

        return render(request, "autograder/student_personal.html", {"form": form,
                                                                    "owner": self.is_owner(),
                                                                    "stat": concrete_statistics_dict})

    def post(self, request, **kwargs):
        student_id = self.get_student_id()
        concrete_answer = self.get_current_form()

        if concrete_answer is not None:
            form = ConcreteStudentAnswersForm(request.POST, instance=concrete_answer)
        else:
            form = ConcreteStudentAnswersForm(None)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.student_id = student_id
            answer.save()
            validation.validate_answers(self.get_student())
        return redirect(request)
