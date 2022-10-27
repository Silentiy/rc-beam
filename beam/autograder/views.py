from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic, View
import autograder.models as md
from .forms import (ConcreteStudentAnswersForm, ReinforcementStudentAnswersForm, GirderGeometryForm,
                    MomentsForcesForm, InitialReinforcementForm, CalculatedReinforcementMiddleStudentForm,
                    CalculatedReinforcementLeftStudentForm, CalculatedReinforcementRightStudentForm,
                    CalculatedReinforcementForm,
                    BearingCapacityMiddleBotStudentForm, BearingCapacityLeftBotStudentForm,
                    BearingCapacityRightBotStudentForm,
                    BearingCapacityMiddleTopStudentForm, BearingCapacityLeftTopStudentForm,
                    BearingCapacityRightTopStudentForm)
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from autograder.services import validation, girder_length, slab_height
from django.db.models import Model


class GroupList(generic.ListView):
    model = md.Group

    template_name = "RC_beam/group_list.html"
    context_object_name = "group_list"


class StudentList(generic.ListView):
    model = md.Student

    def get_group_id(self):
        return self.kwargs['group_id']

    def get_queryset(self):
        """ Return a list of students from group with given 'group_id' """
        group_id = self.get_group_id()
        return md.Student.objects.filter(group_id=group_id)

    def get_context_data(self, **kwargs):
        group_id = self.get_group_id()
        context = super(md.StudentList, self).get_context_data(**kwargs)
        context["group_id"] = group_id
        context["group_name"] = md.Group.objects.filter(pk=group_id)[0]
        return context


@login_required
def redirect(request):
    user_id = request.user.pk
    user_name = request.user.username
    return HttpResponseRedirect(reverse_lazy("grader:student_personal", args=[user_name]))


class StudentPersonalView(View):
    forms_with_errors = dict()

    models_dict = {
        "initial_data_models": {
            "GirderGeometry": [md.GirderGeometry, GirderGeometryForm],
            "Concrete": [md.ConcreteStudentAnswers, ConcreteStudentAnswersForm, md.Concrete,
                         md.ConcreteAnswersStatistics],
            "Reinforcement": [md.ReinforcementStudentAnswers, ReinforcementStudentAnswersForm,
                              md.Reinforcement, md.ReinforcementAnswersStatistics],
            "MomentsForces": [md.MomentsForces, MomentsForcesForm],
            "InitialReinforcement": [md.InitialReinforcement, InitialReinforcementForm]
        },
        "reinforcement_calculations_models": {
            "CalculatedReinforcementMiddle": [md.CalculatedReinforcementMiddleStudent,
                                              CalculatedReinforcementMiddleStudentForm,
                                              md.CalculatedReinforcementMiddleProgram,
                                              md.CalculatedReinforcementMiddleStatistics],
            "CalculatedReinforcementLeft": [md.CalculatedReinforcementLeftStudent,
                                            CalculatedReinforcementLeftStudentForm,
                                            md.CalculatedReinforcementLeftProgram,
                                            md.CalculatedReinforcementLeftStatistics],
            "CalculatedReinforcementRight": [md.CalculatedReinforcementRightStudent,
                                             CalculatedReinforcementRightStudentForm,
                                             md.CalculatedReinforcementRightProgram,
                                             md.CalculatedReinforcementRightStatistics]
        },
        "reinforcement_placement_models": {
            "CalculatedReinforcement": [md.CalculatedReinforcement, CalculatedReinforcementForm]
        },
        "capacity_calculations_models": {
            "BearingCapacityMiddleBot": [md.BearingCapacityMiddleBotStudent, BearingCapacityMiddleBotStudentForm,
                                         md.BearingCapacityMiddleBotProgram, md.BearingCapacityMiddleBotStatistics, ],
            "BearingCapacityLeftBot": [md.BearingCapacityLeftBotStudent, BearingCapacityLeftBotStudentForm,
                                       md.BearingCapacityLeftBotProgram, md.BearingCapacityLeftBotStatistics, ],
            "BearingCapacityRightBot": [md.BearingCapacityRightBotStudent, BearingCapacityRightBotStudentForm,
                                        md.BearingCapacityRightBotProgram, md.BearingCapacityRightBotStatistics, ],
            "BearingCapacityMiddleTop": [md.BearingCapacityMiddleTopStudent, BearingCapacityMiddleTopStudentForm,
                                         md.BearingCapacityMiddleTopProgram, md.BearingCapacityMiddleTopStatistics, ],
            "BearingCapacityLeftTop": [md.BearingCapacityLeftTopStudent, BearingCapacityLeftTopStudentForm,
                                       md.BearingCapacityLeftTopProgram, md.BearingCapacityLeftTopStatistics, ],
            "BearingCapacityRightTop": [md.BearingCapacityRightTopStudent, BearingCapacityRightTopStudentForm,
                                        md.BearingCapacityRightTopProgram, md.BearingCapacityRightTopStatistics, ],

        }
    }

    def get_statistics_models(self):
        statistics_models = list()
        for block_name, block_dict in self.models_dict.items():
            for model_name, models_list in block_dict.items():
                if len(models_list) > 2:
                    statistics_models.append(models_list[3])
        return statistics_models

    def is_owner(self):
        owner = False
        if self.kwargs["user_name"] == self.request.user.username:
            owner = True
        return owner

    def get_student(self):
        user_id = User.objects.get_by_natural_key(username=self.get_user_name())
        return md.Student.objects.get(user_id=user_id)

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
        group = md.Group.objects.get(pk=group_id)
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
        girder_geometry = md.GirderGeometry.objects.filter(student_id=self.get_student_id()).first()
        if girder_geometry is not None:
            return girder_geometry.girder_height
        else:
            return None

    # we do not want to show some forms before previous forms are successfully filled
    def update_student_opened_blocks(self):
        student = self.get_student()
        current_blocks = self.get_instance(md.StudentOpenForms)
        opened_blocks_number = 0
        opened_forms_names = list()

        for block_name, block_models in self.models_dict.items():
            number_models_in_block = len(list(block_models.items()))
            for key, value in block_models.items():
                if self.get_instance(value[0]) is not None and key in block_models.keys():
                    opened_forms_names.append(key)

            opened_forms_number = len(opened_forms_names)

            if opened_forms_number == number_models_in_block:  # all models in block are filled
                opened_blocks_number += 1
                md.StudentOpenForms.objects.update_or_create(student=student,
                                                             defaults={"max_opened_form_number": opened_blocks_number})
            opened_forms_names.clear()

    def get_student_models_dict(self):
        current_blocks = self.get_instance(md.StudentOpenForms)

        if current_blocks is not None:  # we have instance in table "StudentOpenForm" for this student
            opened_blocks_number = current_blocks.max_opened_form_number + 1  # one form more to show
        else:
            opened_blocks_number = 1  # one block is opened for everyone

        student_models_blocks = dict(list(self.models_dict.items())[:opened_blocks_number])

        student_models_dict = dict()
        for key, value in student_models_blocks.items():
            student_models_dict.update(value)

        return student_models_dict

    def get(self, request, **kwargs):
        forms = dict()

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
                                                       initial_reinforcement=self.get_instance(md.InitialReinforcement))
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
                                                               md.InitialReinforcement))
                    else:  # usual form
                        form = form_model()

            forms[model_name] = form

        statistics_dict = dict()
        for statistics_model in self.get_statistics_models():
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
                                                   initial_reinforcement=self.get_instance(md.InitialReinforcement))
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
                                                   initial_reinforcement=self.get_instance(md.InitialReinforcement))
            else:
                form = model_form(request.POST or None)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.student = self.get_student()
            answer.save()
            self.update_student_opened_blocks()

            validation.validate_answers(self.get_student(), student_models_dict, submit_button_name)

        else:
            self.forms_with_errors[submit_button_name] = form
            self.forms_with_errors["user"] = request.user

        redirect_url = f"{reverse('grader:student_personal', args=(request.user,))}#{submit_button_name}"
        return HttpResponseRedirect(redirect_url)
