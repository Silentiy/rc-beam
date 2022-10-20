from autograder.models import (Student, VariantInfo,
                               Concrete, Reinforcement,
                               GirderGeometry, MomentsForces, InitialReinforcement,
                               CalculatedReinforcementMiddleProgram,
                               CalculatedReinforcementLeftProgram,
                               CalculatedReinforcementRightProgram
                               )

VALID_SECTIONS = {1, 2, 3}


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

    return geometry


def get_moments(student_id: int):
    moments_forces = MomentsForces.objects.filter(student_id=student_id).first()
    moments = dict()
    if moments_forces is not None:
        moments["M_1_bot"] = float(moments_forces.middle_section_moment_bot)
        moments["M_1_top"] = float(moments_forces.middle_section_moment_top)

        moments["M_2_bot"] = float(moments_forces.left_support_moment_bot)
        moments["M_2_top"] = float(moments_forces.left_support_moment_top)

        moments["M_3_bot"] = float(moments_forces.right_support_moment_bot)
        moments["M_3_top"] = float(moments_forces.right_support_moment_top)
    else:
        moments["moments"] = None

    return moments


def get_initial_reinforcement(student_id: int):
    initial_reinforcement = InitialReinforcement.objects.filter(student_id=student_id).first()
    reinforcement = dict()

    if initial_reinforcement is not None:
        reinforcement["A_sc_1"] = float(initial_reinforcement.section_1_top_reinforcement_area)
        reinforcement["h_0_1"] = float(initial_reinforcement.section_1_bot_effective_depth)
        reinforcement["a_sc_1"] = float(initial_reinforcement.section_1_top_distance)

        reinforcement["A_sc_2"] = float(initial_reinforcement.section_2_bot_reinforcement_area)
        reinforcement["h_0_2"] = float(initial_reinforcement.section_2_top_effective_depth)
        reinforcement["a_sc_2"] = float(initial_reinforcement.section_2_bot_distance)

        reinforcement["A_sc_3"] = float(initial_reinforcement.section_3_bot_reinforcement_area)
        reinforcement["h_0_3"] = float(initial_reinforcement.section_3_top_effective_depth)
        reinforcement["a_sc_3"] = float(initial_reinforcement.section_3_bot_distance)
    else:
        reinforcement["reinforcement"] = None

    return reinforcement


def get_materials_properties(student_id: int):
    materials = dict()

    student = Student.objects.filter(pk=student_id).first()

    if student is not None:
        student_subgroup_variant = student.subgroup_variant_number
        student_variant_data = VariantInfo.objects.get(variant_number=student_subgroup_variant)
        concrete_id = student_variant_data.girder_concrete_id
        reinforcement_id = student_variant_data.girder_reinforcement_id
        concrete = Concrete.objects.filter(pk=concrete_id).first()
        reinforcement = Reinforcement.objects.filter(pk=reinforcement_id).first()

        if reinforcement is not None and concrete is not None:
            materials["R_s"] = float(reinforcement.R_s / 10)
            materials["R_sc"] = float(reinforcement.R_sc_sh / 10)
            materials["R_b"] = float(concrete.R_b / 10)
        else:
            materials["materials"] = None
    else:
        materials["materials"] = None

    return materials


def is_data_for_calculations(data_to_check: dict):
    return None not in data_to_check.values()


def get_data_for_reinforcement_calculation(student_id: int):
    data_for_reinforcement_calculation = dict()

    data_for_reinforcement_calculation.update(get_section_geometry(student_id))
    data_for_reinforcement_calculation.update(get_materials_properties(student_id))
    data_for_reinforcement_calculation.update(get_moments(student_id))
    data_for_reinforcement_calculation.update(get_initial_reinforcement(student_id))

    return data_for_reinforcement_calculation


def is_section_valid(section: int):
    if section not in VALID_SECTIONS:
        raise ValueError(f"Only {VALID_SECTIONS} could be used!")


def filter_data_for_section(data: dict, section: int):
    is_section_valid(section)

    filtered_data = dict()
    filtered_data["R_s"] = data["R_s"]
    filtered_data["R_sc"] = data["R_sc"]
    filtered_data["R_b"] = data["R_b"]
    filtered_data["h_0"] = data[f"h_0_{section}"]
    filtered_data["a_sc"] = data[f"a_sc_{section}"]
    filtered_data["A_sc"] = data[f"A_sc_{section}"]

    if section == 1:
        filtered_data["M"] = data["M_1_bot"]
        filtered_data["b"] = data["b_w"]
    else:
        filtered_data["M"] = data[f"M_{section}_top"]
        filtered_data["b"] = data["b_f"]

    return filtered_data


def calculate_alpha_m(filtered_data: dict):
    d = filtered_data
    return (d["M"] - d["R_sc"] * d["A_sc"] * (d["h_0"] - d["a_sc"])) / (d["R_b"] * d["b"] * d["h_0"] ** 2)


def calculate_reinforcement_area(filtered_data: dict, alpha_m: float):
    d = filtered_data

    if alpha_m > 0:
        return d["R_b"] * d["b"] * d["h_0"] * (1 - (1 - 2 * alpha_m) ** 0.5) / d["R_s"] + \
               d["A_sc"] * d["R_sc"] / d["R_s"]
    else:
        return d["M"] / (d["R_s"] * (d["h_0"] - d["a_sc"]))


def calculate_reinforcement(student: Student, section: int):
    is_section_valid(section)

    if section == 1:
        model = CalculatedReinforcementMiddleProgram
    elif section == 2:
        pass
    else:
        pass

    defaults = dict()

    student_id = student.pk
    data = get_data_for_reinforcement_calculation(student_id)

    if is_data_for_calculations(data):
        filtered_data = filter_data_for_section(data, section)
        defaults["alpha_m"] = calculate_alpha_m(filtered_data)
        defaults["reinforcement_area"] = calculate_reinforcement_area(filtered_data, defaults["alpha_m"])

        model.objects.update_or_create(student=student,
                                       defaults={**defaults}
                                       )
    else:
        model.objects.update_or_create(student=student,
                                       defaults={"alpha_m": -1,
                                                 "reinforcement_area": -1}
                                       )


def calculate_support_reinforcement(student: Student):
    pass
