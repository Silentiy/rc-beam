from django.forms import ModelForm
from autograder.models import Student, ConcreteStudentAnswers
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


