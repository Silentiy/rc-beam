from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic, View
from .models import Group, Student, ConcreteStudentAnswers
from .forms import ConcreteStudentAnswersForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


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
    print("!!!!!!", reverse_lazy("grader:student_personal", args=[user_id]))
    return HttpResponseRedirect(reverse_lazy("grader:student_personal", args=[user_name]))


class StudentPersonalView(View):

    def is_owner(self):
        owner = False
        if self.kwargs["user_name"] == self.request.user.username:
            owner = True
        return owner

    def get_student_id(self):
        user_name = self.kwargs["user_name"]
        user_id = User.objects.get_by_natural_key(username=user_name)
        student = Student.objects.get(user_id=user_id)
        return student.pk

    def get(self, request, **kwargs):
        user_name = kwargs.get("user_name")
        user_id = User.objects.get_by_natural_key(username=user_name)
        student = Student.objects.get(user_id=user_id)
        student_id = student.pk
        student_name = student.full_name
        group_id = student.group_id
        group = Group.objects.get(pk=group_id)
        group_name = group.group_name

        try:
            concrete_answer = ConcreteStudentAnswers.objects.get(student_id=student_id)
        except ObjectDoesNotExist:
            concrete_answer = False

        if concrete_answer is not False:
            form = ConcreteStudentAnswersForm(instance=concrete_answer)
        else:
            form = ConcreteStudentAnswersForm()

        return render(request, "autograder/student_personal.html", {"form": form,
                                                                    "owner": self.is_owner()})

    def post(self, request, **kwargs):
        student_id = self.get_student_id()
        concrete_answer = ConcreteStudentAnswers.objects.filter(student_id=student_id).first()

        if concrete_answer is not None:
            form = ConcreteStudentAnswersForm(request.POST, instance=concrete_answer)
        else:
            form = ConcreteStudentAnswersForm(request.POST or None)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.student_id = student_id
            answer.save()
            # TODO: invoke validation method here
        return redirect(request)
