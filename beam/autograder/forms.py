from django.forms import ModelForm
from autograder.models import Student, ConcreteStudentAnswers, ReinforcementStudentAnswers
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
        exclude = ("student", )
        labels = {"stud_reinforcement_class": "Класс продольной арматуры по заданию",
                  "stud_R_s_ser": "Нормативное сопротивление арматуры растяжению",
                  "stud_R_s": "Расчётное сопротивление арматуры растяжению",
                  "stud_R_sc_l": "Расчётное сопротивление арматуры сжатию при действии длительных нагрзок",
                  "stud_R_sc_sh": "Расчётное сопротивление арматуры сжатию при действии кратковременных нагрузок",
                  "stud_R_sw": "Расчётное сопротивление хомутов",
                  "stud_alpha_R": "Параметр alpha_R",
                  "stud_xi_R": "Параметр xi_R"}
