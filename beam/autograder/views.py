from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic, View
from .models import (Group, Student,
                     ConcreteStudentAnswers, ConcreteAnswersStatistics,
                     ReinforcementStudentAnswers, ReinforcementAnswersStatistics,
                     GirderGeometry, SlabHeight,
                     MomentsForces, InitialReinforcement,
                     CalculatedReinforcementMiddleStudent, CalculatedReinforcementMiddleStatistics,
                     CalculatedReinforcementLeftStudent, CalculatedReinforcementLeftStatistics,
                     CalculatedReinforcementRightStudent, CalculatedReinforcementRightStatistics)
from .forms import (ConcreteStudentAnswersForm, ReinforcementStudentAnswersForm, GirderGeometryForm,
                    MomentsForcesForm, InitialReinforcementForm, CalculatedReinforcementMiddleStudentForm,
                    CalculatedReinforcementLeftStudentForm, CalculatedReinforcementRightStudentForm)
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from autograder.services import validation, girder_length
from django.db import models
from django.db.models import Model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


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
    models_dict = {"GirderGeometry": [GirderGeometry, GirderGeometryForm],
                   "Concrete": [ConcreteStudentAnswers, ConcreteStudentAnswersForm],
                   "Reinforcement": [ReinforcementStudentAnswers, ReinforcementStudentAnswersForm],
                   "MomentsForces": [MomentsForces, MomentsForcesForm],
                   "InitialReinforcement": [InitialReinforcement, InitialReinforcementForm],
                   "CalculatedReinforcementMiddle": [CalculatedReinforcementMiddleStudent,
                                                     CalculatedReinforcementMiddleStudentForm],
                   "CalculatedReinforcementLeft": [CalculatedReinforcementLeftStudent,
                                                   CalculatedReinforcementLeftStudentForm],
                   "CalculatedReinforcementRight": [CalculatedReinforcementRightStudent,
                                                    CalculatedReinforcementRightStudentForm],
                   }

    statistics_models = [ConcreteAnswersStatistics, ReinforcementAnswersStatistics,
                         CalculatedReinforcementMiddleStatistics,
                         CalculatedReinforcementLeftStatistics, CalculatedReinforcementRightStatistics]

    forms_with_errors = {}

    def is_owner(self):
        owner = False
        if self.kwargs["user_name"] == self.request.user.username:
            owner = True
        return owner

    def get_student(self):
        user_id = User.objects.get_by_natural_key(username=self.get_user_name())
        return Student.objects.get(user_id=user_id)

    def get_student_id(self):
        student = self.get_student()
        return student.pk

    def get_student_name(self):
        student = self.get_student()
        return student.full_name

    def get_user_name(self):
        return self.kwargs["user_name"]

    def get_student_group_name(self):
        student = self.get_student()
        group_id = student.group_id
        group = Group.objects.get(pk=group_id)
        return group.group_name

    def get_instance(self, db_model: Model):
        return db_model.objects.filter(student_id=self.get_student_id()).first()

    def get_statistics_instance(self, db_model: Model):
        return db_model.objects.filter(student_id=self.get_student_id()).first()

    def get_slab(self):
        return SlabHeight.objects.get(student_id=self.get_student_id())

    def get_girder_length(self):
        return girder_length.determine_girder_length(student=self.get_student())

    def get_girder_height(self):
        girder_geometry = GirderGeometry.objects.filter(student_id=self.get_student_id()).first()
        if girder_geometry is not None:
            return girder_geometry.girder_height
        else:
            return None

    def get(self, request, **kwargs):
        forms = dict()

        for model_name, models_list in self.models_dict.items():
            answer_model = models_list[0]
            form_model = models_list[1]
            answer = self.get_instance(answer_model)
            if answer is not None:
                if form_model is GirderGeometryForm:  # we need to pass extra arguments for this form
                    form = GirderGeometryForm(instance=answer, slab=self.get_slab(),
                                              girder_length=self.get_girder_length())
                elif form_model is InitialReinforcementForm:  # and to this as well
                    form = InitialReinforcementForm(instance=answer, girder_height=self.get_girder_height())
                else:  # usual form
                    form = form_model(instance=answer)
            else:  # answer was not saved, there could be errors in form.
                if self.forms_with_errors.get(model_name) and \
                        self.forms_with_errors["user"].username == request.user.username:
                    form = self.forms_with_errors[model_name]
                else:  # no errors, return empty form
                    if form_model is GirderGeometryForm:  # we need pass extra args to this form
                        form = GirderGeometryForm(slab=self.get_slab(),
                                                  girder_length=self.get_girder_length())
                    elif form_model is InitialReinforcementForm:
                        form = InitialReinforcementForm(girder_height=self.get_girder_height())
                    else:  # usual form
                        form = form_model()

            forms[model_name] = form

        statistics_dict = dict()
        for statistics_model in self.statistics_models:
            statistics = self.get_statistics_instance(statistics_model)
            if statistics is not None:
                statistics_dict.update(model_to_dict(statistics, exclude=["id", "student"]))

        return render(request, "autograder/student_personal.html", {"forms": forms,
                                                                    "owner": self.is_owner(),
                                                                    "student_name": self.get_student_name(),
                                                                    "stat": statistics_dict,
                                                                    "forms_names": list(self.models_dict.keys()),
                                                                    }
                      )

    def post(self, request, **kwargs):

        for key in self.models_dict.keys():
            if key in request.POST:
                submit_button_name = key

        answer_instance = self.get_instance(self.models_dict[submit_button_name][0])
        model_form = self.models_dict[submit_button_name][1]

        if answer_instance is not None:
            if model_form is GirderGeometryForm:
                form = GirderGeometryForm(request.POST, instance=answer_instance, slab=self.get_slab(),
                                          girder_length=self.get_girder_length())
            elif model_form is InitialReinforcementForm:
                form = InitialReinforcementForm(request.POST, instance=answer_instance,
                                                girder_height=self.get_girder_height())
            else:
                form = model_form(request.POST, instance=answer_instance)
        else:
            if model_form is GirderGeometryForm:
                form = GirderGeometryForm(request.POST or None, slab=self.get_slab(),
                                          girder_length=self.get_girder_length())
            elif model_form is InitialReinforcementForm:
                form = InitialReinforcementForm(request.POST or None, girder_height=self.get_girder_height())
            else:
                form = model_form(request.POST or None)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.student = self.get_student()
            answer.save()
            if submit_button_name not in ["GirderGeometry", "MomentsForces", "InitialReinforcement"]:
                validation.validate_answers(self.get_student(), submit_button_name)
        else:
            self.forms_with_errors[submit_button_name] = form
            self.forms_with_errors["user"] = request.user

        redirect_url = f"{reverse('grader:student_personal', args=(request.user,))}#{submit_button_name}"
        return HttpResponseRedirect(redirect_url)
