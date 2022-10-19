from autograder.models import (Concrete, ConcreteStudentAnswers, ConcreteAnswersStatistics,
                               Reinforcement, ReinforcementStudentAnswers, ReinforcementAnswersStatistics,
                               VariantInfo, PersonalVariantsArchitects, PersonalVariantsCivilEngineers,
                               Student, GirderGeometry, MomentsForces, InitialReinforcement,
                               CalculatedReinforcementMiddleProgram,
                               CalculatedReinforcementMiddleStudent,
                               CalculatedReinforcementMiddleStatistics
                               )


def get_section_geometry(student_id: int):
    girder_geometry = GirderGeometry.objects.filter(student_id=student_id).first()
    geometry = dict()
    if girder_geometry is not None:
        geometry["b_w"] = float(girder_geometry.girder_wall_width)
        geometry["b_f"] = float(girder_geometry.girder_effective_flange_width)
        geometry["h_f"] = float(girder_geometry.girder_flange_bevel_height +
                                girder_geometry.girder_flange_slab_height)
    else:
        geometry["geometry"] = None


def get_moments(student_id: int):

    moments_forces = MomentsForces.objects.filter(student_id=student_id).first()


def get_initial_reinforcement(student_id: int, section: int):

    if section < 1 or section > 3:
        raise ValueError(f"There are can not be section number {section}")

    initial_reinforcement = InitialReinforcement.objects.filter(student_id=student_id).first()
    reinforcement = dict()

    parameters_names = ["A_sc", "h_0", "a_sc"]

    if initial_reinforcement is not None:
        if section == 1:
            reinforcement["A_sc_1"] = float(initial_reinforcement.section_1_top_reinforcement_area)
            reinforcement["h_0_1"] = float(initial_reinforcement.section_1_bot_effective_depth)
            reinforcement["a_sc_1"] = float(initial_reinforcement.section_1_top_distance)
        elif section == 2:
            reinforcement["A_sc_2"] = float(initial_reinforcement.section_2_bot_reinforcement_area)
            reinforcement["h_0_2"] = float(initial_reinforcement.section_2_top_effective_depth)
            reinforcement["a_sc_2"] = float(initial_reinforcement.section_2_bot_distance)
        elif section == 3:
            reinforcement["A_sc_3"] = float(initial_reinforcement.section_3_bot_reinforcement_area)
            reinforcement["h_0_3"] = float(initial_reinforcement.section_3_top_effective_depth)
            reinforcement["a_sc_3"] = float(initial_reinforcement.section_3_bot_distance)
    else:
        reinforcement["reinforcement"] = None

    return reinforcement


def get_materials_properties(student_id: int):
    concrete = ConcreteStudentAnswers.objects.filter(student_id=student_id).first()
    reinforcement = ReinforcementStudentAnswers.objects.filter(student_id=student_id).first()
    materials = dict()

    if reinforcement is not None and concrete is not None:
        materials["R_s"] = float(reinforcement.stud_R_s)
        materials["R_sc"] = float(reinforcement.stud_R_sc_sh)
        materials["R_b"] = float(concrete.stud_R_b)
    else:
        materials["materials"] = None

    return materials


def is_data_for_calculations(data_to_check: dict):
    return None not in data_to_check.values()


def calculate_middle_reinforcement(student: Student):

    student_id = student.pk

    girder_geometry = GirderGeometry.objects.filter(student_id=student_id).first()
    concrete = ConcreteStudentAnswers.objects.filter(student_id=student_id).first()
    reinforcement = ReinforcementStudentAnswers.objects.filter(student_id=student_id).first()
    moments_forces = MomentsForces.objects.filter(student_id=student_id).first()
    initial_reinforcement = InitialReinforcement.objects.filter(student_id=student_id).first()

    if None not in [girder_geometry, concrete, reinforcement, moments_forces, initial_reinforcement]:
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
            A_s_1 = M_1 / (R_s * (h_0_1 - a_sc_1))
        else:
            A_s_1 = R_b * wall_b * h_0_1 * (1 - (1 - 2 * alpha_m) ** 0.5) / R_s + A_sc_1 * R_sc / R_s

        CalculatedReinforcementMiddleProgram.objects.update_or_create(student=student,
                                                                      defaults={"alpha_m": alpha_m,
                                                                                "reinforcement_area": A_s_1}
                                                                      )
    else:
        CalculatedReinforcementMiddleProgram.objects.update_or_create(student=student,
                                                                      defaults={"alpha_m": -1,
                                                                                "reinforcement_area": -1}
                                                                      )


def calculate_support_reinforcement(student: Student):
    pass
