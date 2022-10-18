from autograder.models import (Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics,
                               Reinforcement, ReinforcementStudentAnswers, ReinforcementAnswersStatistics,
                               VariantInfo, PersonalVariantsArchitects, PersonalVariantsCivilEngineers,
                               Student)
from django.forms.models import model_to_dict



def validate_answers(student, button_name):
    models_dict = {"Concrete": [Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics],
                   "Reinforcement": [Reinforcement, ReinforcementStudentAnswers, ReinforcementAnswersStatistics]}

    student_id = student.pk
    student_subgroup_variant = student.subgroup_variant_number
    student_personal_variant = student.personal_variant_number
    student_variant_data = VariantInfo.objects.get(variant_number=student_subgroup_variant)

    program_answers_model = models_dict[button_name][0]
    student_answers_model = models_dict[button_name][1]
    statistics_model = models_dict[button_name][2]

    student_answers = student_answers_model.objects.get(student_id=student_id)

    student_exclude = ["id", "student"]
    if button_name == "Concrete":
        program_exclude = ["id"]
        student_material_id = student_variant_data.girder_concrete_id
    elif button_name == "Reinforcement":
        program_exclude = ["id", "possible_diameters"]
        student_material_id = student_variant_data.girder_reinforcement_id

    program_answers = program_answers_model.objects.get(pk=student_material_id)

    student_answers_dict = model_to_dict(student_answers, exclude=student_exclude)
    program_answers_dict = model_to_dict(program_answers, exclude=program_exclude)

    statistics = dict()
    for key, value in program_answers_dict.items():
        stud_dict_key = "stud_" + key
        if key not in ["alpha_R", "xi_R", "reinforcement_class", "concrete_class"]:
            if student_answers_dict[stud_dict_key] == value / 10:
                statistics[key] = True
            else:
                statistics[key] = False
        elif "reinforcement_class" in key or "concrete_class" in key:

            if student_answers_dict[stud_dict_key] == program_answers.id:
                statistics[key] = True
            else:
                statistics[key] = False
        else:
            if student_answers_dict[stud_dict_key] is not None:
                if float(value) * 0.995 <= student_answers_dict[stud_dict_key] <= float(value) * 1.005:
                    statistics[key] = True
                else:
                    statistics[key] = False

    statistics_model.objects.update_or_create(student_id=student_id,
                                              defaults={**statistics})
