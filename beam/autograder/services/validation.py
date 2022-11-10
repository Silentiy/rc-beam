from autograder.models import VariantInfo, Student
from django.forms.models import model_to_dict
from . import reiforcement_calculation, bearing_capacity


def validate_answers(student: Student, opened_models_dict: dict, button_name: str):
    models_dict = dict()
    button_names = list()

    button_names.append(button_name)

    for model_name, models_list in opened_models_dict.items():
        if len(models_list) > 2:  # there are models for statistics
            models_dict[model_name] = models_list

    student_id = student.pk
    group_id = student.group
    revalidate_reinforcement_list = ["CalculatedReinforcementMiddle", "CalculatedReinforcementLeft",
                                     "CalculatedReinforcementRight"]
    revalidate_capacity_list = ["BearingCapacityMiddleBot", "BearingCapacityLeftBot", "BearingCapacityRightBot",
                                "BearingCapacityMiddleTop", "BearingCapacityLeftTop", "BearingCapacityRightTop"]

    if "InitialReinforcement" in button_name or "GirderGeometry" in button_name:
        for name in revalidate_reinforcement_list:
            if name in models_dict.keys():  # do we have CalculatedReinforcement... models opened for student
                if models_dict[name][0].objects.filter(student_id=student_id).first() is not None:  # answer is there
                    button_names.append(name)  # revalidate reinforcement calculations

    if "InitialReinforcement" in button_name or "GirderGeometry" in button_name or\
            "CalculatedReinforcement" in button_name:
        for name in revalidate_capacity_list:
            if name in models_dict.keys():  # do we have BearingCapacity... models opened for student
                if models_dict[name][0].objects.filter(student_id=student_id).first() is not None:  # answer is there
                    button_names.append(name)  # revalidate bearing capacity calculations

    for button_name in button_names:
        if button_name in models_dict.keys():  # work with models that allow validation
            student_subgroup_variant = student.subgroup_variant_number
            student_personal_variant = student.personal_variant_number
            student_variant_data = VariantInfo.objects.get(variant_number=student_subgroup_variant, group_id=group_id)

            program_answers_model = models_dict[button_name][2]
            student_answers_model = models_dict[button_name][0]
            statistics_model = models_dict[button_name][3]

            if "CalculatedReinforcementMiddle" in button_name:
                reiforcement_calculation.calculate_reinforcement(student=student, section=1)
            elif "CalculatedReinforcementLeft" in button_name:
                reiforcement_calculation.calculate_reinforcement(student=student, section=2)
            elif "CalculatedReinforcementRight" in button_name:
                reiforcement_calculation.calculate_reinforcement(student=student, section=3)

            if "BearingCapacity" in button_name:
                if "Bot" in button_name:  # bot surface in tension
                    bearing_capacity.calculate_bearing_capacity(student, surface="bot")
                else:
                    bearing_capacity.calculate_bearing_capacity(student, surface="top")

            student_answer = student_answers_model.objects.get(student_id=student_id)

            student_exclude = ["id", "student"]
            if button_name == "Concrete":
                program_exclude = ["id"]
                student_material_id = student_variant_data.girder_concrete_id
                program_answer = program_answers_model.objects.get(pk=student_material_id)
            elif button_name == "Reinforcement":
                program_exclude = ["id", "possible_diameters"]
                student_material_id = student_variant_data.girder_reinforcement_id
                program_answer = program_answers_model.objects.get(pk=student_material_id)
            else:
                program_exclude = ["id", "student"]
                program_answer = program_answers_model.objects.get(student_id=student_id)

            student_answers_dict = model_to_dict(student_answer, exclude=student_exclude)
            program_answers_dict = model_to_dict(program_answer, exclude=program_exclude)

            statistics = dict()

            if button_name == "Concrete" or button_name == "Reinforcement":
                statistics = validate_concrete_and_reinforcement(program_answers=program_answers_dict,
                                                                 student_answers=student_answers_dict,
                                                                 program_answer_id=program_answer.id)
            else:
                special_keys = list()
                for key in student_answers_dict.keys():  # for fields, that contain True / False
                    if str(key).startswith("is_"):
                        special_keys.append(key)

                if special_keys:
                    statistics = strict_match_validation(program_answers=
                                                         get_dict_for_special_validation(program_answers_dict,
                                                                                         special_keys),
                                                         student_answers=
                                                         get_dict_for_special_validation(student_answers_dict,
                                                                                         special_keys))

                statistics.update(tolerant_match_validation(program_answers=program_answers_dict,
                                                            student_answers=student_answers_dict,
                                                            tolerance=0.01)
                                  )
            statistics_model.objects.update_or_create(student_id=student_id,
                                                      defaults={**statistics}
                                                      )


def get_dict_for_special_validation(answers: dict, special_keys: list):
    special_answers = dict()

    for key in special_keys:
        if answers.get(key) is not None:
            special_answers[key] = answers.pop(key)

    return special_answers


def strict_match_validation(program_answers: dict, student_answers: dict):
    statistics = dict()

    for key, value in program_answers.items():
        if student_answers[key] is not None and student_answers[key] == value:
            statistics[key] = True
        else:
            statistics[key] = False

    return statistics


def tolerant_match_validation(program_answers: dict, student_answers: dict, tolerance: float):
    statistics = dict()
    min_bound = 1 - tolerance
    max_bound = 1 + tolerance

    for key, value in program_answers.items():
        if student_answers[key] is not None:
            if value >= 0:
                if float(value) * min_bound <= student_answers[key] <= float(value) * max_bound:
                    statistics[key] = True
                else:
                    statistics[key] = False
            else:
                if float(value) * min_bound >= student_answers[key] >= float(value) * max_bound:
                    statistics[key] = True
                else:
                    statistics[key] = False
        else:
            statistics[key] = False

    return statistics


def validate_concrete_and_reinforcement(program_answers: dict, student_answers: dict, program_answer_id: int):
    statistics = dict()
    student_special_values = dict()
    program_special_values = dict()
    special_keys = ["alpha_R", "xi_R"]

    if special_keys[0] in program_answers.keys() and special_keys[1] in program_answers.keys():
        for key in special_keys:
            student_special_values[key] = student_answers.pop(key)
            program_special_values[key] = program_answers.pop(key)

    if program_special_values:
        statistics.update(tolerant_match_validation(program_answers=program_special_values,
                                                    student_answers=student_special_values,
                                                    tolerance=0.005))

    for key, value in program_answers.items():
        if key in ["reinforcement_class", "concrete_class"]:
            if student_answers[key] == program_answer_id:
                statistics[key] = True
            else:
                statistics[key] = False
        else:
            if (value / 10) * 0.999 <= student_answers[key] <= (value / 10) * 1.001:
                statistics[key] = True
            else:
                statistics[key] = False

    return statistics
