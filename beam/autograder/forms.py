from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from autograder.models import (Student,
                               ConcreteStudentAnswers, ReinforcementStudentAnswers, GirderGeometry,
                               MomentsForces)
from django.utils.safestring import mark_safe


class ConcreteStudentAnswersForm(ModelForm):
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


class ReinforcementStudentAnswersForm(ModelForm):
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
    class Meta:
        model = GirderGeometry
        exclude = ("student", "slab")

        labels = {"girder_flange_bevel_height": "Высота скоса полки, см",
                  "girder_flange_slab_height": "Высота прямого участка полки",
                  "girder_wall_height": "Высота стенки",
                  "girder_wall_width": "Ширина стенки",
                  "girder_flange_bevel_width": "Ширина скоса полки",
                  "girder_height": "Высота сечения ригеля",
                  "girder_flange_full_width": "Ширина полки ригеля",
                  "girder_flange_console_widths": "Вылет полки ригеля",
                  "girder_length": "Длина ригеля"}
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
        self.sslab = kwargs.pop('sslab')
        super(GirderGeometryForm, self).__init__(*args, **kwargs)

        self.fields["girder_height"].widget.attrs["readonly"] = True
        self.fields["girder_flange_console_widths"].widget.attrs["readonly"] = True
        self.fields["girder_flange_full_width"].widget.attrs["readonly"] = True

        self.fields["girder_flange_bevel_height"].widget.attrs["min"] = 10
        self.fields["girder_flange_bevel_height"].widget.attrs["max"] = 30

    def clean_girder_wall_height(self):
        data = self.cleaned_data
        girder_wall_height = data["girder_wall_height"]
        slab_height = self.sslab.slab_height / 10
        if girder_wall_height != slab_height:
            raise ValidationError(gettext_lazy('Высота стенки ригеля должна быть равна высоте плиты,'
                                               ' опирающейся на ригель'))
        return girder_wall_height


class MomentsForcesForm(ModelForm):
    class Meta:
        model = MomentsForces
        exclude = ("student",)

        labels = {
            "middle_section_moment_top": mark_safe(
                "Момент в сечении 1-1, растягивающий верхнюю грань, M<sub>1-1</sub><sup>в</sup> [кНсм]"),
            "middle_section_moment_bot": mark_safe(
                "Момент в сечении 1-1, растягивающий нижнюю грань, M<sub>1-1</sub><sup>н</sup> [кНсм]"),
            "middle_section_status": "Усилия в середине пролёта",

            "left_support_moment_top": mark_safe(
                "Момент в сечении 2-2, растягивающий верхнюю грань, M<sub>2-2</sub><sup>в</sup> [кНсм]"),
            "left_support_moment_bot": mark_safe(
                "Момент в сечении 2-2, растягивающий нижнюю грань, M<sub>2-2</sub><sup>н</sup> [кНсм]"),
            "left_support_shear_force": mark_safe(
                "Перерезывающая сила в сечении 2-2, Q<sub>2-2</sub> [кН]"),
            "left_support_status": "Усилия на опоре слева",

            "right_support_moment_top": mark_safe(
                "Момент в сечении 3-3, растягивающий верхнюю грань, M<sub>3-3</sub><sup>в</sup> [кНсм]"),
            "right_support_moment_bot": mark_safe(
                "Момент в сечении 3-3, растягивающий нижнюю грань, M<sub>3-3</sub><sup>н</sup> [кНсм]"),
            "right_support_shear_force": mark_safe(
                "Перерезывающая сила в сечении 3-3, Q<sub>3-3</sub> [кН]"),
            "right_support_status": "Усилия на опоре справа",
        }

    def __init__(self, *args, **kwargs):
        super(MomentsForcesForm, self).__init__(*args, **kwargs)
        self.fields["middle_section_status"].widget.attrs["disabled"] = True
        self.fields["right_support_status"].widget.attrs["disabled"] = True
        self.fields["left_support_status"].widget.attrs["disabled"] = True
        instance = getattr(self, 'instance', None)
        # print(type(instance))

        if instance.middle_section_status is True:
            self.fields["middle_section_moment_top"].widget.attrs["readonly"] = True
            self.fields["middle_section_moment_bot"].widget.attrs["readonly"] = True
        if instance.left_support_status is True:
            self.fields["left_support_moment_top"].disabled = True
            self.fields["left_support_moment_bot"].disabled = True
            self.fields["left_support_shear_force"].disabled = True
        if instance.right_support_status is True:
            self.fields["right_support_moment_top"].widget.attrs["readonly"] = True
            self.fields["right_support_moment_bot"].widget.attrs["readonly"] = True
            self.fields["right_support_shear_force"].widget.attrs["readonly"] = True

    def clean_middle_section_status(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.middle_section_status
        else:
            return self.cleaned_data['middle_section_status']

    def clean_left_support_status(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.left_support_status
        else:
            return self.cleaned_data['left_support_status']

    def clean(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and instance.middle_section_status is True:
            self.cleaned_data['middle_section_moment_top'] = instance.middle_section_moment_top
            self.cleaned_data['middle_section_moment_bot'] = instance.middle_section_moment_bot
