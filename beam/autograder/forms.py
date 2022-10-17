from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from autograder.models import (Student,
                               ConcreteStudentAnswers, ReinforcementStudentAnswers, GirderGeometry,
                               MomentsForces, InitialReinforcement)
from django.utils.safestring import mark_safe


class ConcreteStudentAnswersForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Исходные данные по бетону", disabled=True)

    class Meta:
        model = ConcreteStudentAnswers
        fields = ["stud_concrete_class", "stud_R_b_n", "stud_R_bt_n", "stud_R_b", "stud_R_bt", "stud_E_b"]
        labels = {"stud_concrete_class": "Класс бетона по заданию",
                  "stud_R_b_n": mark_safe(
                      "Нормативное сопротивление бетона сжатию, R<sub>bn</sub> [кН/см<sup>2</sup>]"),
                  "stud_R_bt_n": "Нормативное сопротивление бетона растяжению",
                  "stud_R_b": "Расчётное сопротивление бетона сжатию",
                  "stud_R_bt": "Расчётное сопротивление бетона растяжению",
                  "stud_E_b": "Начальный модуль упругости бетона"
                  }

    def __init__(self, *args, **kwargs):
        super(ConcreteStudentAnswersForm, self).__init__(*args, **kwargs)


class ReinforcementStudentAnswersForm(ModelForm):
    verbose_name = forms.CharField(required=False, initial="Исходные данные по арматуре", disabled=True)

    class Meta:
        model = ReinforcementStudentAnswers
        exclude = ("student",)
        labels = {"stud_reinforcement_class": "Класс продольной арматуры по заданию",
                  "stud_R_s_ser": "Нормативное сопротивление арматуры растяжению",
                  "stud_R_s": "Расчётное сопротивление арматуры растяжению",
                  "stud_R_sc_l": "Расчётное сопротивление арматуры сжатию при действии длительных нагрзок",
                  "stud_R_sc_sh": "Расчётное сопротивление арматуры сжатию при действии кратковременных нагрузок",
                  "stud_R_sw": "Расчётное сопротивление хомутов",
                  "stud_alpha_R": "Параметр alpha_R",
                  "stud_xi_R": "Параметр xi_R"}


class GirderGeometryForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Геометрия сечения ригеля", disabled=True)

    class Meta:
        model = GirderGeometry
        exclude = ("student", "slab", "girder_effective_flange_width")

        labels = {"girder_flange_bevel_height": "Высота скоса полки, см",
                  "girder_flange_slab_height": "Высота прямого участка полки",
                  "girder_wall_height": "Высота стенки",
                  "girder_wall_width": "Ширина стенки",
                  "girder_flange_bevel_width": "Ширина скоса полки",
                  "girder_height": "Высота сечения ригеля",
                  "girder_flange_full_width": "Ширина полки ригеля",
                  "girder_flange_console_widths": "Вылет полки ригеля",
                  "girder_length": "Длина ригеля",
                  }
        error_messages = {
            "girder_flange_bevel_height": {
                'min_value': gettext_lazy(
                    'Высота скоса полки должна быть более или равна %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Высота скоса полки должна быть менее или равна %(limit_value)s см')
            },
            "girder_flange_slab_height": {
                'min_value': gettext_lazy(
                    'Высота прямого участка полки должна быть более или равна %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Высота прямого участка полки должна быть менее или равна %(limit_value)s см')
            },
            "girder_wall_width": {
                'min_value': gettext_lazy('Ширина стенки должна быть более или равна %(limit_value)s см'),
                'max_value': gettext_lazy('Ширина стенки должна быть менее или равна %(limit_value)s см')
            },
            'girder_flange_bevel_width': {
                'min_value': gettext_lazy('Ширина скоса полки должна быть более или равна %(limit_value)s см'),
                'max_value': gettext_lazy('Ширина скоса полки должна быть менее или равна %(limit_value)s см')
            }
        }

    def __init__(self, *args, **kwargs):
        self.slab = kwargs.pop('slab')
        self.answer_girder_length = kwargs.pop("girder_length")
        super(GirderGeometryForm, self).__init__(*args, **kwargs)

        self.fields["girder_height"].disabled = True
        self.fields["girder_flange_console_widths"].disabled = True
        self.fields["girder_flange_full_width"].disabled = True

        self.fields["girder_flange_bevel_height"].widget.attrs["min"] = 10
        self.fields["girder_flange_bevel_height"].widget.attrs["max"] = 30

    def clean_girder_wall_height(self):
        data = self.cleaned_data
        girder_wall_height = data["girder_wall_height"]
        slab_height = self.slab.slab_height / 10
        if girder_wall_height != slab_height:
            raise ValidationError(gettext_lazy('Высота стенки ригеля должна быть равна высоте плиты,'
                                               ' опирающейся на ригель'))
        return girder_wall_height

    def clean_girder_length(self):
        data = self.cleaned_data
        girder_length = data["girder_length"]
        answer_girder_length = self.answer_girder_length
        if girder_length != answer_girder_length:
            raise ValidationError(gettext_lazy('Уточните конструктивную длину ригеля'))
        return girder_length


class MomentsForcesForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Усилия в сечениях ригеля", disabled=True)

    class Meta:
        model = MomentsForces
        exclude = ("student",)

        labels = {
            "middle_section_moment_top": mark_safe(
                "Момент в сечении 1-1, растягивающий верхнюю грань, M<sub>1-1</sub><sup>в</sup> [кНсм]"),
            "middle_section_moment_bot": mark_safe(
                "Момент в сечении 1-1, растягивающий нижнюю грань, M<sub>1-1</sub><sup>н</sup> [кНсм]"),
            "middle_section_status": "Усилия в середине пролёта приняты",

            "left_support_moment_top": mark_safe(
                "Момент в сечении 2-2, растягивающий верхнюю грань, M<sub>2-2</sub><sup>в</sup> [кНсм]"),
            "left_support_moment_bot": mark_safe(
                "Момент в сечении 2-2, растягивающий нижнюю грань, M<sub>2-2</sub><sup>н</sup> [кНсм]"),
            "left_support_shear_force": mark_safe(
                "Перерезывающая сила в сечении 2-2, Q<sub>2-2</sub> [кН]"),
            "left_support_status": "Усилия на опоре слева приняты",

            "right_support_moment_top": mark_safe(
                "Момент в сечении 3-3, растягивающий верхнюю грань, M<sub>3-3</sub><sup>в</sup> [кНсм]"),
            "right_support_moment_bot": mark_safe(
                "Момент в сечении 3-3, растягивающий нижнюю грань, M<sub>3-3</sub><sup>н</sup> [кНсм]"),
            "right_support_shear_force": mark_safe(
                "Перерезывающая сила в сечении 3-3, Q<sub>3-3</sub> [кН]"),
            "right_support_status": "Усилия на опоре справа приняты",
        }

    def __init__(self, *args, **kwargs):
        super(MomentsForcesForm, self).__init__(*args, **kwargs)
        self.fields["middle_section_status"].disabled = True
        self.fields["right_support_status"].disabled = True
        self.fields["left_support_status"].disabled = True
        instance = getattr(self, 'instance', None)
        # print(type(instance))

        if instance.middle_section_status is True:
            self.fields["middle_section_moment_top"].disabled = True
            self.fields["middle_section_moment_bot"].disabled = True
        if instance.left_support_status is True:
            self.fields["left_support_moment_top"].disabled = True
            self.fields["left_support_moment_bot"].disabled = True
            self.fields["left_support_shear_force"].disabled = True
        if instance.right_support_status is True:
            self.fields["right_support_moment_top"].disabled = True
            self.fields["right_support_moment_bot"].disabled = True
            self.fields["right_support_shear_force"].disabled = True


class InitialReinforcementForm(ModelForm):

    verbose_name = forms.CharField(label="header", required=False, initial="Предварительное армирование", disabled=True)

    class Meta:
        model = InitialReinforcement
        # fields = "__all__"
        exclude = ("student", )

    def __init__(self, *args, **kwargs):
        self.girder_height = kwargs.pop('girder_height')
        super(InitialReinforcementForm, self).__init__(*args, **kwargs)
        # self.fields['section_1_top_d_external'].widget = forms.HiddenInput()

    def get_effective_depths(self, section: int, surface: str):
        student_id = self.student
        student_girder_height = GirderGeometry.objects.get(student_id=student_id).girder_height
        distance_to_reinforcement = getattr(self, f"section_{section}_{surface}_distance")
        return student_girder_height - distance_to_reinforcement