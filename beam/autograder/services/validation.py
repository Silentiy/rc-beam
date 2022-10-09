from autograder.models import (Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics,
                               VariantInfo, PersonalVariantsArchitects, PersonalVariantsCivilEngineers,
                               Student)
from django.forms.models import model_to_dict


def validate_answers(student):
    student_id = student.pk
    student_subgroup_variant = student.subgroup_variant_number
    student_personal_variant = student.personal_variant_number
    concrete_student_answers = ConcreteStudentAnswers.objects.get(student_id=student_id)
    student_variant_data = VariantInfo.objects.get(variant_number=student_subgroup_variant)
    student_concrete_id = student_variant_data.girder_concrete_id
    concrete_program_answers = Concrete.objects.get(pk=student_concrete_id)

    concrete_student_answers_dict = model_to_dict(concrete_student_answers)
    concrete_program_answers_dict = model_to_dict(concrete_program_answers)
    concrete_student_answers_dict.pop("id")
    concrete_student_answers_dict.pop("student")
    concrete_program_answers_dict.pop("id")

    # print(concrete_student_answers_dict)
    #  print(concrete_program_answers_dict)

    statistics = dict()
    for key, value in concrete_program_answers_dict.items():
        # print(key, value)
        stud_dict_key = "stud_" + key
        if concrete_student_answers_dict[stud_dict_key] == value:
            statistics[key] = True
        else:
            statistics[key] = False

    ConcreteAnswersStatistics.objects.update_or_create(student_id=student_id,
                                                       defaults={**statistics})

