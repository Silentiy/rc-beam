from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic, View
from .models import (Group, Student, StudentOpenForms,
                     ConcreteStudentAnswers, ConcreteAnswersStatistics,
                     ReinforcementStudentAnswers, ReinforcementAnswersStatistics,
                     GirderGeometry,
                     MomentsForces, InitialReinforcement, CalculatedReinforcement,
                     CalculatedReinforcementMiddleStudent, CalculatedReinforcementMiddleStatistics,
                     CalculatedReinforcementLeftStudent, CalculatedReinforcementLeftStatistics,
                     CalculatedReinforcementRightStudent, CalculatedReinforcementRightStatistics)
from .forms import (ConcreteStudentAnswersForm, ReinforcementStudentAnswersForm, GirderGeometryForm,
                    MomentsForcesForm, InitialReinforcementForm, CalculatedReinforcementMiddleStudentForm,
                    CalculatedReinforcementLeftStudentForm, CalculatedReinforcementRightStudentForm,
                    CalculatedReinforcementForm)
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from autograder.services import validation, girder_length, slab_height
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
    forms_with_errors = dict()

    models_dict = {  # initial data models
        "GirderGeometry": [GirderGeometry, GirderGeometryForm],
        "Concrete": [ConcreteStudentAnswers, ConcreteStudentAnswersForm],
        "Reinforcement": [ReinforcementStudentAnswers, ReinforcementStudentAnswersForm],
        "MomentsForces": [MomentsForces, MomentsForcesForm],
        "InitialReinforcement": [InitialReinforcement, InitialReinforcementForm],
        # models for reinforcement calculations
        "CalculatedReinforcementMiddle": [CalculatedReinforcementMiddleStudent,
                                          CalculatedReinforcementMiddleStudentForm],
        "CalculatedReinforcementLeft": [CalculatedReinforcementLeftStudent,
                                        CalculatedReinforcementLeftStudentForm],
        "CalculatedReinforcementRight": [CalculatedReinforcementRightStudent,
                                         CalculatedReinforcementRightStudentForm],
        # models with final reinforcement placement
        "CalculatedReinforcement": [CalculatedReinforcement, CalculatedReinforcementForm],
        # models with bearing capacity calculations

    }

    statistics_models = [ConcreteAnswersStatistics, ReinforcementAnswersStatistics,
                         CalculatedReinforcementMiddleStatistics,
                         CalculatedReinforcementLeftStatistics, CalculatedReinforcementRightStatistics]

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

    def get_instance(self, db_model):
        return db_model.objects.filter(student_id=self.get_student_id()).first()

    def get_statistics_instance(self, db_model: Model):
        return db_model.objects.filter(student_id=self.get_student_id()).first()

    def get_slab(self):
        return slab_height.get_slab(self.get_student(), self.get_student_group_name())

    def get_girder_length(self):
        return girder_length.determine_girder_length(student=self.get_student())

    def get_girder_height(self):
        girder_geometry = GirderGeometry.objects.filter(student_id=self.get_student_id()).first()
        if girder_geometry is not None:
            return girder_geometry.girder_height
        else:
            return None

    # we do not want to show some forms before previous forms are successfully filled
    def update_student_models_dict(self):
        student = self.get_student()
        opened_forms_names = list()
        for key, value in self.models_dict.items():
            if self.get_instance(value[0]) is not None:
                opened_forms_names.append(key)
        opened_forms_number = len(opened_forms_names)
        StudentOpenForms.objects.update_or_create(student=student,
                                                  defaults={"max_opened_form_number": opened_forms_number})

    def get_student_models_dict(self):
        opened_forms_number = self.get_instance(StudentOpenForms).max_opened_form_number + 1
        # if opened_forms_number == 0:
        #     opened_forms_number = 1  # we need to start somewhere initial data granted to anyone
        student_models_dict = dict(list(self.models_dict.items())[:opened_forms_number])
        return student_models_dict

    def get(self, request, **kwargs):
        forms = dict()
        self.update_student_models_dict()
        student_models_dict = self.get_student_models_dict()

        for model_name, models_list in student_models_dict.items():
            answer_model = models_list[0]
            form_model = models_list[1]
            answer = self.get_instance(answer_model)
            if answer is not None:
                if form_model is GirderGeometryForm:  # we need to pass extra arguments for this form
                    form = GirderGeometryForm(instance=answer, slab=self.get_slab(),
                                              girder_length=self.get_girder_length())
                elif form_model is InitialReinforcementForm:  # and to this as well
                    form = InitialReinforcementForm(instance=answer, girder_height=self.get_girder_height())
                elif form_model is CalculatedReinforcementForm:  # and to this too
                    form = CalculatedReinforcementForm(instance=answer,
                                                       girder_height=self.get_girder_height(),
                                                       initial_reinforcement=self.get_instance(InitialReinforcement))
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
                    elif form_model is CalculatedReinforcementForm:
                        form = CalculatedReinforcementForm(girder_height=self.get_girder_height(),
                                                           initial_reinforcement=self.get_instance(
                                                               InitialReinforcement))
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
                                                                    "forms_names": list(student_models_dict.keys()),
                                                                    }
                      )

    def post(self, request, **kwargs):

        student_models_dict = self.get_student_models_dict()

        for key in student_models_dict.keys():
            if key in request.POST:
                submit_button_name = key

        answer_instance = self.get_instance(student_models_dict[submit_button_name][0])
        model_form = student_models_dict[submit_button_name][1]

        if answer_instance is not None:
            if model_form is GirderGeometryForm:
                form = GirderGeometryForm(request.POST, instance=answer_instance, slab=self.get_slab(),
                                          girder_length=self.get_girder_length())
            elif model_form is InitialReinforcementForm:
                form = InitialReinforcementForm(request.POST, instance=answer_instance,
                                                girder_height=self.get_girder_height())
            elif model_form is CalculatedReinforcementForm:
                form = CalculatedReinforcementForm(request.POST, instance=answer_instance,
                                                   girder_height=self.get_girder_height(),
                                                   initial_reinforcement=self.get_instance(InitialReinforcement))
            else:
                form = model_form(request.POST, instance=answer_instance)
        else:
            if model_form is GirderGeometryForm:
                form = GirderGeometryForm(request.POST or None, slab=self.get_slab(),
                                          girder_length=self.get_girder_length())
            elif model_form is InitialReinforcementForm:
                form = InitialReinforcementForm(request.POST or None,
                                                girder_height=self.get_girder_height())
            elif model_form is CalculatedReinforcementForm:
                form = CalculatedReinforcementForm(request.POST or None,
                                                   girder_height=self.get_girder_height(),
                                                   initial_reinforcement=self.get_instance(InitialReinforcement))
            else:
                form = model_form(request.POST or None)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.student = self.get_student()
            answer.save()
            self.update_student_models_dict()

            if submit_button_name not in ["GirderGeometry", "MomentsForces",
                                          "InitialReinforcement", "CalculatedReinforcement"]:
                validation.validate_answers(self.get_student())

        else:
            self.forms_with_errors[submit_button_name] = form
            self.forms_with_errors["user"] = request.user

        redirect_url = f"{reverse('grader:student_personal', args=(request.user,))}#{submit_button_name}"
        return HttpResponseRedirect(redirect_url)
