from autograder.models import (Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics,
                               Reinforcement, ReinforcementStudentAnswers, ReinforcementAnswersStatistics,
                               VariantInfo, PersonalVariantsArchitects, PersonalVariantsCivilEngineers,
                               Student, GirderGeometry, MomentsForces, InitialReinforcement,
                               CalculatedReinforcementMiddleProgram,
                               CalculatedReinforcementMiddleStudent,
                               CalculatedReinforcementMiddleStatistics
                               )
from django.forms.models import model_to_dict



def validate_answers(student, button_name):
    models_dict = {"Concrete": [Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics],
                   "Reinforcement": [Reinforcement, ReinforcementStudentAnswers, ReinforcementAnswersStatistics],
                   "CalculatedReinforcementMiddle": [CalculatedReinforcementMiddleProgram,
                                                      CalculatedReinforcementMiddleStudent,
                                                      CalculatedReinforcementMiddleStatistics],
                   }

    if "CalculatedReinforcementMiddle" in button_name:
        calculate_reinforcement(student=student)

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
        program_answers = program_answers_model.objects.get(pk=student_material_id)
    elif button_name == "Reinforcement":
        program_exclude = ["id", "possible_diameters"]
        student_material_id = student_variant_data.girder_reinforcement_id
        program_answers = program_answers_model.objects.get(pk=student_material_id)
    elif button_name == "CalculatedReinforcementMiddle":
        program_exclude = ["id", "student"]
        program_answers = program_answers_model.objects.get(student_id=student_id)

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


def calculate_reinforcement(student: Student):
    student_id = student.pk
    girder_geometry = GirderGeometry.objects.get(student_id=student_id)
    concrete = ConcreteStudentAnswers.objects.get(student_id=student_id)
    reinforcement = ReinforcementStudentAnswers.objects.get(student_id=student_id)
    moments_forces = MomentsForces.objects.get(student_id=student_id)
    initial_reinforcement = InitialReinforcement.objects.get(student_id=student_id)

    M_1 = float(moments_forces.middle_section_moment_bot)
    R_sc = float(reinforcement.stud_R_sc_sh)
    A_sc_1 = float(initial_reinforcement.section_1_top_reinforcement_area)
    h_0_1 = float(initial_reinforcement.section_1_bot_effective_depth)
    a_sc_1 = float(initial_reinforcement.section_1_top_distance)
    wall_b = float(girder_geometry.girder_wall_width)
    R_b = float(concrete.stud_R_b)
    R_s = float(reinforcement.stud_R_s)

    alpha_m = (M_1 - R_sc * A_sc_1 * (h_0_1 - a_sc_1)) / (R_b * wall_b * h_0_1 ** 2)
    if alpha_m < 0:
        pass
    else:
        A_s_1 = R_b * wall_b * h_0_1 * (1 - (1 - 2 * alpha_m) ** 0.5) / R_s + A_sc_1 * R_sc / R_s

    CalculatedReinforcementMiddleProgram.objects.update_or_create(student=student,
                                                                  defaults={"alpha_m": alpha_m,
                                                                            "reinforcement_area":  A_s_1}
                                                                  )