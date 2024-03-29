from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from .models import (ConcreteStudentAnswers, ReinforcementStudentAnswers, GirderGeometry,
                     MomentsForces, InitialReinforcement, CalculatedReinforcement,
                     CalculatedReinforcementMiddleStudent,
                     CalculatedReinforcementLeftStudent,
                     CalculatedReinforcementRightStudent,
                     BearingCapacityMiddleBotStudent, BearingCapacityMiddleTopStudent,
                     BearingCapacityLeftBotStudent, BearingCapacityLeftTopStudent,
                     BearingCapacityRightBotStudent, BearingCapacityRightTopStudent, )
from django.utils.safestring import mark_safe


class ConcreteStudentAnswersForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Исходные данные по бетону", disabled=True)

    class Meta:
        model = ConcreteStudentAnswers
        fields = ["concrete_class", "R_b_n", "R_bt_n", "R_b", "R_bt", "E_b"]
        labels = {"concrete_class": "Класс бетона по заданию",
                  "R_b_n": mark_safe(
                      "Нормативное сопротивление бетона сжатию, R<sub>bn</sub> [кН/см<sup>2</sup>]"),
                  "R_bt_n": mark_safe(
                      "Нормативное сопротивление бетона растяжению, R<sub>btn</sub> [кН/см<sup>2</sup>]"),
                  "R_b": mark_safe(
                      "Расчётное сопротивление бетона сжатию, R<sub>b</sub> [кН/см<sup>2</sup>]"),
                  "R_bt": mark_safe(
                      "Расчётное сопротивление бетона растяжению, R<sub>bt</sub> [кН/см<sup>2</sup>]"),
                  "E_b": mark_safe(
                      "Начальный модуль упругости бетона, E<sub>b</sub> [кН/см<sup>2</sup>]")
                  }

    def __init__(self, *args, **kwargs):
        super(ConcreteStudentAnswersForm, self).__init__(*args, **kwargs)


class ReinforcementStudentAnswersForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Исходные данные по арматуре", disabled=True)

    class Meta:
        model = ReinforcementStudentAnswers
        exclude = ("student",)
        labels = {"reinforcement_class": "Класс продольной арматуры по заданию",
                  "R_s_ser": mark_safe(
                      "Нормативное сопротивление арматуры растяжению, R<sub>s,ser</sub> [кН/см<sup>2</sup>]"),
                  "R_s": mark_safe(
                      "Расчётное сопротивление арматуры растяжению, R<sub>s</sub> [кН/см<sup>2</sup>]"),
                  "R_sc_l": mark_safe(
                      "Расчётное сопротивление арматуры сжатию при действии длительных нагрузок,"
                      " R<sub>sc,l</sub> [кН/см<sup>2</sup>]"),
                  "R_sc_sh": mark_safe(
                      "Расчётное сопротивление арматуры сжатию при действии кратковременных нагрузок, "
                      "R<sub>sc,sh</sub> [кН/см<sup>2</sup>]"),
                  "R_sw": mark_safe(
                      "Расчётное сопротивление хомутов, R<sub>sw</sub> [кН/см<sup>2</sup>]"),
                  "alpha_R": mark_safe(
                      "Параметр &#945<sub>R</sub>"),
                  "xi_R": mark_safe(
                      "Параметр &#958<sub>R</sub>")}


class GirderGeometryForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Геометрия сечения ригеля", disabled=True)

    class Meta:
        model = GirderGeometry
        exclude = ("student", "slab", "girder_effective_flange_width")

        labels = {"girder_flange_bevel_height": mark_safe(
                       "Высота скоса полки, h<sub>fb</sub> [см]"
                  ),
                  "girder_flange_slab_height": mark_safe(
                      "Высота прямого участка полки, h<sub>fs</sub> [см]"
                  ),
                  "girder_wall_height": mark_safe(
                      "Высота стенки, h<sub>w</sub> [см]"
                  ),
                  "girder_wall_width": mark_safe(
                      "Ширина стенки, b<sub>w</sub> [см]"
                  ),
                  "girder_flange_bevel_width": mark_safe(
                      "Ширина скоса полки, b<sub>fb</sub> [см]"
                  ),
                  "girder_height": mark_safe(
                      "Высота сечения ригеля, h [см]"
                  ),
                  "girder_flange_full_width": mark_safe(
                      "Ширина полки ригеля, b<sub>f</sub> [см]"
                  ),
                  "girder_flange_console_widths": mark_safe(
                      "Вылет полки ригеля, b<sub>fc</sub> [см]"
                  ),
                  "girder_length": mark_safe(
                      "Конструктивная длина ригеля, l<sub>k</sub> [см]"
                  ),
                  }
        error_messages = {
            "girder_flange_bevel_height": {
                'min_value': mark_safe(
                    gettext_lazy(
                        'Высота скоса полки должна быть более или равна %(limit_value)s см'
                    )
                ),
                'max_value': mark_safe(
                    gettext_lazy(
                        'Высота скоса полки должна быть менее или равна %(limit_value)s см'
                    )
                )
            },
            "girder_flange_slab_height": {
                'min_value': mark_safe(
                    gettext_lazy(
                        'Высота прямого участка полки должна быть более или равна %(limit_value)s см'
                    )
                ),
                'max_value': mark_safe(
                    gettext_lazy(
                        'Высота прямого участка полки должна быть менее или равна %(limit_value)s см'
                    )
                )
            },
            "girder_wall_width": {
                'min_value': mark_safe(
                    gettext_lazy(
                        'Ширина стенки должна быть более или равна %(limit_value)s см'
                    )
                ),
                'max_value': mark_safe(
                    gettext_lazy(
                        'Ширина стенки должна быть менее или равна %(limit_value)s см'
                    )
                )
            },
            'girder_flange_bevel_width': {
                'min_value': mark_safe(
                    gettext_lazy(
                        'Ширина скоса полки должна быть более или равна %(limit_value)s см'
                    )
                ),
                'max_value': mark_safe(
                    gettext_lazy(
                        'Ширина скоса полки должна быть менее или равна %(limit_value)s см'
                    )
                )
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
            raise ValidationError(gettext_lazy('Уточните конструктивную длину ригеля (в рамках курсовой работы'
                                               ', она равна 536 см для крайнего ригеля и 556 см для среднего) '))
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
        exclude = ("student",)

        labels = {
            # SECTION 2 TOP
            "section_2_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_2_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_2_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_2_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_2_top_distance": mark_safe("a [см]"),
            "section_2_top_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_2_top_effective_depth": mark_safe("h<sub>0</sub> [см]"),
            # SECTION 2 BOT
            "section_2_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_2_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_2_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_2_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_2_bot_distance": mark_safe("a' [см]"),
            "section_2_bot_reinforcement_area": mark_safe("A'<sub>s</sub> [см<sup>2</sup>]"),
            "section_2_bot_effective_depth": mark_safe("h'<sub>0</sub> [см]"),

            # SECTION 1 TOP
            "section_1_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_1_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_1_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_1_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_1_top_distance": mark_safe("a' [см]"),
            "section_1_top_reinforcement_area": mark_safe("A'<sub>s</sub> [см<sup>2</sup>]"),
            "section_1_top_effective_depth": mark_safe("h'<sub>0</sub> [см]"),
            # SECTION 1 BOT
            "section_1_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_1_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_1_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_1_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_1_bot_distance": mark_safe("a [см]"),
            "section_1_bot_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_1_bot_effective_depth": mark_safe("h<sub>0</sub> [см]"),

            # SECTION 3 TOP
            "section_3_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_3_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_3_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_3_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_3_top_distance": mark_safe("a [см]"),
            "section_3_top_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_3_top_effective_depth": mark_safe("h<sub>0</sub> [см]"),
            # SECTION 3 BOT
            "section_3_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_3_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_3_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_3_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_3_bot_distance": mark_safe("a' [см]"),
            "section_3_bot_reinforcement_area": mark_safe("A'<sub>a</sub> [см<sup>2</sup>]"),
            "section_3_bot_effective_depth": mark_safe("h'<sub>0</sub> [см]"),
        }

        error_messages = {
            "section_2_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 2-2, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 2-2, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_2_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 2-2, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 2-2, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_1_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 1-1, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 1-1, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_1_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 1-1, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 1-1, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_3_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 3-3, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 3-3, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_3_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 3-3, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 3-3, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
        }

    def __init__(self, *args, **kwargs):
        self.girder_height = kwargs.pop('girder_height')
        super(InitialReinforcementForm, self).__init__(*args, **kwargs)
        self.fields["section_2_top_d_external"].disabled = True
        self.fields["section_2_top_n_external"].disabled = True
        self.fields["section_2_top_d_internal"].disabled = True
        self.fields["section_2_top_n_internal"].disabled = True

        self.fields["section_1_bot_d_external"].disabled = True
        self.fields["section_1_bot_n_external"].disabled = True
        self.fields["section_1_bot_d_internal"].disabled = True
        self.fields["section_1_bot_n_internal"].disabled = True

        self.fields["section_3_top_d_external"].disabled = True
        self.fields["section_3_top_n_external"].disabled = True
        self.fields["section_3_top_d_internal"].disabled = True
        self.fields["section_3_top_n_internal"].disabled = True

        self.fields["section_2_top_reinforcement_area"].disabled = True
        self.fields["section_2_top_effective_depth"].disabled = True
        self.fields["section_2_bot_reinforcement_area"].disabled = True
        self.fields["section_2_bot_effective_depth"].disabled = True

        self.fields["section_1_top_reinforcement_area"].disabled = True
        self.fields["section_1_top_effective_depth"].disabled = True
        self.fields["section_1_bot_reinforcement_area"].disabled = True
        self.fields["section_1_bot_effective_depth"].disabled = True

        self.fields["section_3_top_reinforcement_area"].disabled = True
        self.fields["section_3_top_effective_depth"].disabled = True
        self.fields["section_3_bot_reinforcement_area"].disabled = True
        self.fields["section_3_bot_effective_depth"].disabled = True

    def clean(self):
        self.cleaned_data["section_1_top_effective_depth"] = self.get_effective_depths(section=1, surface="top")
        self.cleaned_data["section_1_bot_effective_depth"] = self.get_effective_depths(section=1, surface="bot")
        self.cleaned_data["section_2_top_effective_depth"] = self.get_effective_depths(section=2, surface="top")
        self.cleaned_data["section_2_bot_effective_depth"] = self.get_effective_depths(section=2, surface="bot")
        self.cleaned_data["section_3_top_effective_depth"] = self.get_effective_depths(section=3, surface="top")
        self.cleaned_data["section_3_bot_effective_depth"] = self.get_effective_depths(section=3, surface="bot")

        return self.cleaned_data

    def get_effective_depths(self, section: int, surface: str):
        student_girder_height = self.girder_height
        distance_to_reinforcement = self.cleaned_data[f"section_{section}_{surface}_distance"]
        if student_girder_height is not None:
            return student_girder_height - distance_to_reinforcement
        else:
            return 0 - distance_to_reinforcement


class CalculatedReinforcementMiddleStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Требуемая арматура в сечении 1-1",
                                   disabled=True)

    class Meta:
        model = CalculatedReinforcementMiddleStudent
        exclude = ("student",)

        labels = {
            "alpha_m_middle": mark_safe("Параметр &alpha;<sub>m</sub>"),
            "is_compressed_zone_capacity_sufficient_middle": mark_safe("Прочность сжатой зоны обеспечена "
                                                                       "(&alpha;<sub>m</sub> < &alpha;<sub>R</sub>)?"),
            "reinforcement_area_middle": mark_safe("Требуемая площадь арматуры в сечении 1-1, "
                                                   "A<sub>s</sub><sup>1</sup>, [см<sup>2</sup>]")
        }


class CalculatedReinforcementLeftStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Требуемая арматура в сечении 2-2",
                                   disabled=True)

    class Meta:
        model = CalculatedReinforcementLeftStudent
        exclude = ("student",)

        labels = {
            "fully_compressed_flange_moment_left": mark_safe("Момент при полностью сжатой полке, M<sub>f</sub> [кНсм]"),
            "is_neutral_axis_in_flange_left": mark_safe("Неатральная ось в полке (M<sub>f</sub> > M<sub>2</sub>)?"),
            "section_widths_for_calculation_left": mark_safe(
                "Ширина сечения, используемая в расчёте, b<sub>f</sub> [см]"),
            "overhanging_flange_area_left": mark_safe("Площадь свесов полки (если нейтральная ось в полке, то 0),"
                                                      " A<sub>0v</sub> [см<sup>2</sup>]"),
            "alpha_m_left": mark_safe("Параметр &alpha;<sub>m</sub>"),
            "is_compressed_zone_capacity_sufficient_left": mark_safe("Прочность сжатой зоны обеспечена "
                                                                     "(&alpha;<sub>m</sub> < &alpha;<sub>R</sub>)?"),
            "reinforcement_area_left": mark_safe("Требуемая площадь арматуры в сечении 2-2, "
                                                 "A<sub>s</sub><sup>2</sup>, [см<sup>2</sup>]")
        }


class CalculatedReinforcementRightStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Требуемая арматура в сечении 3-3",
                                   disabled=True)

    class Meta:
        model = CalculatedReinforcementRightStudent
        exclude = ("student",)

        labels = {
            "fully_compressed_flange_moment_right": mark_safe(
                "Момент при полностью сжатой полке, M<sub>f</sub> [кНсм]"),
            "is_neutral_axis_in_flange_right": mark_safe("Неатральная ось в полке (M<sub>f</sub> > M<sub>3</sub>)?"),
            "section_widths_for_calculation_right": mark_safe(
                "Ширина сечения, используемая в расчёте, b<sub>f</sub> [см]"),
            "overhanging_flange_area_right": mark_safe("Площадь свесов полки (если нейтральная ось в полке, то 0),"
                                                       " A<sub>0v</sub> [см<sup>2</sup>]"),
            "alpha_m_right": mark_safe("Параметр &alpha;<sub>m</sub>"),
            "is_compressed_zone_capacity_sufficient_right": mark_safe("Прочность сжатой зоны обеспечена "
                                                                      "(&alpha;<sub>m</sub> < &alpha;<sub>R</sub>)?"),
            "reinforcement_area_right": mark_safe("Требуемая площадь арматуры в сечении 3-3, "
                                                  "A<sub>s</sub><sup>3</sup>, [см<sup>2</sup>]")
        }


class CalculatedReinforcementForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Итоговое армирование", disabled=True)

    class Meta:
        model = CalculatedReinforcement
        exclude = ("student",)

        labels = {
            # SECTION 2 TOP
            "section_2_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_2_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_2_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_2_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_2_top_distance": mark_safe("a [см]"),
            "section_2_top_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_2_top_effective_depth": mark_safe("h<sub>0</sub> [см]"),
            # SECTION 2 BOT
            "section_2_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_2_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_2_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_2_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_2_bot_distance": mark_safe("a' [см]"),
            "section_2_bot_reinforcement_area": mark_safe("A'<sub>s</sub> [см<sup>2</sup>]"),
            "section_2_bot_effective_depth": mark_safe("h'<sub>0</sub> [см]"),

            # SECTION 1 TOP
            "section_1_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_1_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_1_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_1_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_1_top_distance": mark_safe("a' [см]"),
            "section_1_top_reinforcement_area": mark_safe("A'<sub>s</sub> [см<sup>2</sup>]"),
            "section_1_top_effective_depth": mark_safe("h'<sub>0</sub> [см]"),
            # SECTION 1 BOT
            "section_1_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_1_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_1_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_1_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_1_bot_distance": mark_safe("a [см]"),
            "section_1_bot_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_1_bot_effective_depth": mark_safe("h<sub>0</sub> [см]"),

            # SECTION 3 TOP
            "section_3_top_d_external": mark_safe("d<sub>1</sub>"),
            "section_3_top_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_3_top_d_internal": mark_safe("d<sub>2</sub>"),
            "section_3_top_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_3_top_distance": mark_safe("a [см]"),
            "section_3_top_reinforcement_area": mark_safe("A<sub>s</sub> [см<sup>2</sup>]"),
            "section_3_top_effective_depth": mark_safe("h<sub>0</sub> [см]"),
            # SECTION 3 BOT
            "section_3_bot_d_external": mark_safe("d<sub>1</sub>"),
            "section_3_bot_n_external": mark_safe("n<sub>1</sub> [шт]"),
            "section_3_bot_d_internal": mark_safe("d<sub>2</sub>"),
            "section_3_bot_n_internal": mark_safe("n<sub>2</sub> [шт]"),
            "section_3_bot_distance": mark_safe("a' [см]"),
            "section_3_bot_reinforcement_area": mark_safe("A'<sub>a</sub> [см<sup>2</sup>]"),
            "section_3_bot_effective_depth": mark_safe("h'<sub>0</sub> [см]"),
        }

        error_messages = {
            "section_2_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 2-2, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 2-2, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_2_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 2-2, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 2-2, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_1_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 1-1, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 1-1, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_1_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 1-1, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 1-1, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_3_top_distance": {
                'min_value': gettext_lazy(
                    'Сечение 3-3, верх: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 3-3, верх: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
            "section_3_bot_distance": {
                'min_value': gettext_lazy(
                    'Сечение 3-3, низ: расстояние до ЦТ арматуры должно быть не менее %(limit_value)s см'),
                'max_value': gettext_lazy(
                    'Сечение 3-3, низ: расстояние до ЦТ арматуры должно быть не более %(limit_value)s см')
            },
        }

    def __init__(self, *args, **kwargs):
        self.girder_height = kwargs.pop('girder_height')
        self.initial_reinforcement = kwargs.pop('initial_reinforcement')
        super(CalculatedReinforcementForm, self).__init__(*args, **kwargs)

        self.fields["section_2_top_reinforcement_area"].disabled = True
        self.fields["section_2_top_effective_depth"].disabled = True
        self.fields["section_2_bot_reinforcement_area"].disabled = True
        self.fields["section_2_bot_effective_depth"].disabled = True

        self.fields["section_1_top_reinforcement_area"].disabled = True
        self.fields["section_1_top_effective_depth"].disabled = True
        self.fields["section_1_bot_reinforcement_area"].disabled = True
        self.fields["section_1_bot_effective_depth"].disabled = True

        self.fields["section_3_top_reinforcement_area"].disabled = True
        self.fields["section_3_top_effective_depth"].disabled = True
        self.fields["section_3_bot_reinforcement_area"].disabled = True
        self.fields["section_3_bot_effective_depth"].disabled = True

        # default values for distances to reinforcement's center of gravity
        self.fields["section_2_top_distance"].initial = self.get_initial_distance_value(section=2, surface="top")
        self.fields["section_2_bot_distance"].initial = self.get_initial_distance_value(section=2, surface="bot")
        self.fields["section_1_top_distance"].initial = self.get_initial_distance_value(section=1, surface="top")
        self.fields["section_1_bot_distance"].initial = self.get_initial_distance_value(section=1, surface="bot")
        self.fields["section_3_top_distance"].initial = self.get_initial_distance_value(section=3, surface="top")
        self.fields["section_3_bot_distance"].initial = self.get_initial_distance_value(section=3, surface="bot")

        # default diameters for non-calculated reinforcement (from InitialReinforcement model)
        for sec in range(1, 4):
            for surface in self.surface_localized.keys():
                for position in ["external", "internal"]:
                    if (surface == "top" and (sec == 2 or sec == 3)) or (surface == "bot" and sec == 1):
                        continue
                    self.fields[f"section_{sec}_{surface}_d_{position}"].initial = \
                        self.get_initial_diameter(section=sec, surface=surface, bar_position=position)
                    self.fields[f"section_{sec}_{surface}_d_{position}"].disabled = True

        # default nu,ber of bars for non-calculated reinforcement (from InitialReinforcement model)
        for sec in range(1, 4):
            for surface in self.surface_localized.keys():
                for position in ["external", "internal"]:
                    if (surface == "top" and (sec == 2 or sec == 3)) or (surface == "bot" and sec == 1):
                        continue
                    self.fields[f"section_{sec}_{surface}_n_{position}"].initial = \
                        self.get_initial_bars_number(section=sec, surface=surface, bar_position=position)
                    self.fields[f"section_{sec}_{surface}_n_{position}"].disabled = True

    def clean(self):
        # reinforcement overlapping
        self.check_inappropriate_overlapping(section=2, section_to=1, surface="top")
        self.check_inappropriate_overlapping(section=1, section_to=3, surface="top")
        self.check_inappropriate_overlapping(section=2, section_to=1, surface="bot")
        self.check_inappropriate_overlapping(section=1, section_to=3, surface="bot")

        # new effective depths
        self.cleaned_data["section_1_top_effective_depth"] = self.get_effective_depths(section=1, surface="top")
        self.cleaned_data["section_1_bot_effective_depth"] = self.get_effective_depths(section=1, surface="bot")
        self.cleaned_data["section_2_top_effective_depth"] = self.get_effective_depths(section=2, surface="top")
        self.cleaned_data["section_2_bot_effective_depth"] = self.get_effective_depths(section=2, surface="bot")
        self.cleaned_data["section_3_top_effective_depth"] = self.get_effective_depths(section=3, surface="top")
        self.cleaned_data["section_3_bot_effective_depth"] = self.get_effective_depths(section=3, surface="bot")

        return self.cleaned_data

    surface_localized = {"top": "верх", "bot": "низ"}

    # distance to reinforcement's center of gravity cannot be bigger, than it was before; recalculation needed otherwise
    def clean_section_2_top_distance(self):
        return self.compare_distances(section=2, surface="top")

    def clean_section_2_bot_distance(self):
        return self.compare_distances(section=2, surface="bot")

    def clean_section_1_top_distance(self):
        return self.compare_distances(section=1, surface="top")

    def clean_section_1_bot_distance(self):
        return self.compare_distances(section=1, surface="bot")

    def clean_section_3_top_distance(self):
        return self.compare_distances(section=3, surface="top")

    def clean_section_3_bot_distance(self):
        return self.compare_distances(section=3, surface="bot")

    def get_effective_depths(self, section: int, surface: str):
        student_girder_height = self.girder_height
        distance_to_reinforcement = self.cleaned_data.get(f"section_{section}_{surface}_distance")

        if student_girder_height is not None and distance_to_reinforcement is not None:
            return student_girder_height - distance_to_reinforcement
        else:
            return distance_to_reinforcement

    def get_initial_distance_value(self, section: int, surface: str):
        initial_data = self.initial_reinforcement
        if initial_data is not None:
            return getattr(initial_data, f"section_{section}_{surface}_distance", 0)
        else:
            return 0  # we should not end up here, but... just in case

    def get_initial_diameter(self, section: int, surface: str, bar_position: str):
        initial_data = self.initial_reinforcement
        if initial_data is not None:
            return getattr(initial_data, f"section_{section}_{surface}_d_{bar_position}", 0)
        else:
            return 1

    def get_initial_bars_number(self, section: int, surface: str, bar_position: str):
        initial_data = self.initial_reinforcement
        if initial_data is not None:
            return getattr(initial_data, f"section_{section}_{surface}_n_{bar_position}", 0)
        else:
            return 0

    def compare_distances(self, section: int, surface: str):
        current_distance_value = self.cleaned_data[f"section_{section}_{surface}_distance"]
        initial_distance_value = self.get_initial_distance_value(section=section, surface=surface)
        if current_distance_value > initial_distance_value:
            raise ValidationError(gettext_lazy(f"Сечение {section}, {self.surface_localized[surface]}: "
                                               f"расстояние до ЦТ арматуры не может быть более принятого при её подборе;"
                                               f" изменить можно в таблице 'Предварительное армирование' "
                                               f"с обязательным пересчётом требуемой площади арматуры"))
        else:
            return current_distance_value

    def check_inappropriate_overlapping(self, section: int, section_to: int, surface: str):
        max_distance = 3  # mm
        min_distance = -1  # mm
        section_diameter = self.cleaned_data[f"section_{section}_{surface}_d_external"].diameter
        section_to_diameter = self.cleaned_data[f"section_{section_to}_{surface}_d_external"].diameter

        section_distance = self.cleaned_data.get(f"section_{section}_{surface}_distance")
        section_to_distance = self.cleaned_data.get(f"section_{section_to}_{surface}_distance")

        if section_distance is not None and section_to_distance is not None:
            section_distance *= 10  # cm to mm
            section_to_distance *= 10

            if section_diameter != section_to_diameter:
                if section_distance > section_to_distance:
                    clearance = (section_distance - 0.5 * section_diameter) - \
                                (section_to_distance + 0.5 * section_to_diameter)
                else:
                    clearance = (section_to_distance - 0.5 * section_to_diameter) - \
                                (section_distance + 0.5 * section_diameter)
                if clearance < min_distance or clearance > max_distance:
                    self.add_error(None,
                                   ValidationError(
                                       gettext_lazy(f'Сечение {section}, {self.surface_localized[surface]}: '
                                                    f'расстояние в свету до стержней арматуры '
                                                    f'в сечении {section_to} составляет {clearance} мм; '
                                                    f'допустимо от {min_distance} до {max_distance} мм!'
                                                    )
                                   )
                                   )


class BearingCapacityMiddleBotStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 1-1, низ",
                                   disabled=True)

    class Meta:
        model = BearingCapacityMiddleBotStudent
        exclude = ("student",)

        labels = {
            "compressed_zone_height_a_middle_bot": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_middle_bot": mark_safe(
                "Относительная высота сжатой зоны, &xi;"
            ),
            "bearing_capacity_a_middle_bot": mark_safe(
                "Первый предельный момент сечения, M<sub>ult1(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_middle_bot": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_middle_bot": mark_safe(
                "Второй предельный момент сечения, M<sub>ult1(b)</sub> [кНсм] (если вычисление не требуется, то 0)"
            ),
            "bearing_capacity_middle_bot": mark_safe(
                "Итоговый предельный момент сечения, M<sub>ult1</sub> [кНсм]"
            )
        }


class BearingCapacityLeftBotStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 2-2, низ",
                                   disabled=True)

    class Meta:
        model = BearingCapacityLeftBotStudent
        exclude = ("student",)

        labels = {
            "compressed_zone_height_a_left_bot": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_left_bot": mark_safe(
                "Относительная высота сжатой зоны, &xi;"
            ),
            "bearing_capacity_a_left_bot": mark_safe(
                "Первый предельный момент сечения, M<sub>ult2(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_left_bot": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_left_bot": mark_safe(
                "Второй предельный момент сечения, M<sub>ult2(b)</sub> [кНсм] (если вычисление не требуется, то 0)"),
            "bearing_capacity_left_bot": mark_safe(
                "Итоговый предельный момент сечения, M<sub>ult2</sub> [кНсм]"
            )
        }


class BearingCapacityRightBotStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 3-3, низ",
                                   disabled=True)

    class Meta:
        model = BearingCapacityRightBotStudent
        exclude = ("student",)

        labels = {
            "compressed_zone_height_a_right_bot": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_right_bot": mark_safe(
                "Относительная высота сжатой зоны, &xi;"
            ),
            "bearing_capacity_a_right_bot": mark_safe(
                "Первый предельный момент сечения, M<sub>ult3(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_right_bot": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_right_bot": mark_safe(
                "Второй предельный момент сечения, M<sub>ult3(b)</sub> [кНсм] (если вычисление не требуется, то 0)"
            ),
            "bearing_capacity_right_bot": mark_safe(
                "Итоговый предельный момент сечения, M<sub>ult3</sub> [кНсм]"
            )
        }


class BearingCapacityMiddleTopStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 1-1, верх",
                                   disabled=True)

    class Meta:
        model = BearingCapacityMiddleTopStudent
        exclude = ("student",)

        labels = {
            "ultimate_tensile_force_middle_top": mark_safe(
                "Предельное усилие, воспринимаемое растянутой частью сечения, R<sub>s</sub>A<sub>s</sub> [кН]"
            ),
            "ultimate_compressive_force_middle_top": mark_safe(
                "Предельное усилие, воспринимаемое сжатой частью сечения,"
                " R<sub>b</sub>b'<sub>f</sub>h'<sub>f</sub>+R<sub>sc</sub>A'<sub>s</sub> [кН]"
            ),
            "compressed_zone_height_a_middle_top": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_middle_top": mark_safe(
                "Относительная высота сжатой зоны, &xi;"),
            "bearing_capacity_a_middle_top": mark_safe(
                "Первый предельный момент сечения, M'<sub>ult1(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_middle_top": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_middle_top": mark_safe(
                "Второй предельный момент сечения, M'<sub>ult1(b)</sub> [кНсм] (если вычисление не требуется, то 0)"
            ),
            "bearing_capacity_middle_top": mark_safe(
                "Итоговый предельный момент сечения, M'<sub>ult1</sub> [кНсм]"
            )
        }


class BearingCapacityLeftTopStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 2-2, верх",
                                   disabled=True)

    class Meta:
        model = BearingCapacityLeftTopStudent
        exclude = ("student",)

        labels = {
            "ultimate_tensile_force_left_top": mark_safe(
                "Предельное усилие, воспринимаемое растянутой частью сечения, R<sub>s</sub>A<sub>s</sub> [кН]"
            ),
            "ultimate_compressive_force_left_top": mark_safe(
                "Предельное усилие, воспринимаемое сжатой частью сечения,"
                " R<sub>b</sub>b'<sub>f</sub>h'<sub>f</sub>+R<sub>sc</sub>A'<sub>s</sub> [кН]"
            ),
            "compressed_zone_height_a_left_top": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_left_top": mark_safe(
                "Относительная высота сжатой зоны, &xi;"),
            "bearing_capacity_a_left_top": mark_safe(
                "Первый предельный момент сечения, M'<sub>ult2(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_left_top": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_left_top": mark_safe(
                "Второй предельный момент сечения, M'<sub>ult2(b)</sub> [кНсм] (если вычисление не требуется, то 0)"
            ),
            "bearing_capacity_left_top": mark_safe(
                "Итоговый предельный момент сечения, M'<sub>ult2</sub> [кНсм]"
            )
        }


class BearingCapacityRightTopStudentForm(ModelForm):
    verbose_name = forms.CharField(label="header", required=False, initial="Несущая способность в сечении 3-3, верх",
                                   disabled=True)

    class Meta:
        model = BearingCapacityRightTopStudent
        exclude = ("student",)

        labels = {
            "ultimate_tensile_force_right_top": mark_safe(
                "Предельное усилие, воспринимаемое растянутой частью сечения, R<sub>s</sub>A<sub>s</sub> [кН]"
            ),
            "ultimate_compressive_force_right_top": mark_safe(
                "Предельное усилие, воспринимаемое сжатой частью сечения,"
                " R<sub>b</sub>b'<sub>f</sub>h'<sub>f</sub>+R<sub>sc</sub>A'<sub>s</sub> [кН]"
            ),
            "compressed_zone_height_a_right_top": mark_safe(
                "Высота сжатой зоны с учётом сжатой арматуры, x<sub>a</sub> [см]"
            ),
            "relative_compressed_zone_height_a_right_top": mark_safe(
                "Относительная высота сжатой зоны, &xi;"),
            "bearing_capacity_a_right_top": mark_safe(
                "Первый предельный момент сечения, M'<sub>ult3(a)</sub> [кНсм]"
            ),
            "compressed_zone_height_b_right_top": mark_safe(
                "Высота сжатой зоны без учёта сжатой арматуры, x<sub>b</sub> [см]"
            ),
            "bearing_capacity_b_right_top": mark_safe(
                "Второй предельный момент сечения, M'<sub>ult3(b)</sub> [кНсм] (если вычисление не требуется, то 0)"
            ),
            "bearing_capacity_right_top": mark_safe(
                "Итоговый предельный момент сечения, M'<sub>ult3</sub> [кНсм]"
            )
        }
