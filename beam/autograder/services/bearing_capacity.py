from autograder.models import (Student, CalculatedReinforcement,
                               BearingCapacityMiddleBotProgram, BearingCapacityMiddleTopProgram,
                               BearingCapacityLeftBotProgram, BearingCapacityLeftTopProgram,
                               BearingCapacityRightBotProgram, BearingCapacityRightTopProgram,
                               )
from django.core.exceptions import ObjectDoesNotExist
from . import reiforcement_calculation as rc

VALID_SECTIONS = {1, 2, 3}
VALID_SURFACES = {"top", "bot"}


def get_calculated_reinforcement(student_id: int):
    calculated_reinforcement = CalculatedReinforcement.objects.filter(student_id=student_id).first()
    section_geometry = rc.get_section_geometry(student_id)
    if section_geometry is not None:
        h = section_geometry["h"]
    else:
        raise ObjectDoesNotExist("You should fill InitialGeometry form first!")

    reinforcement = dict()

    if calculated_reinforcement is not None:
        for section in VALID_SECTIONS:
            for surface in VALID_SURFACES:
                reinforcement[f"A_{section}_{surface}"] = \
                    float(getattr(calculated_reinforcement, f"section_{section}_{surface}_reinforcement_area"))
                reinforcement[f"a_s_{section}_{surface}"] = float(getattr(calculated_reinforcement,
                                                                          f"section_{section}_{surface}_distance"))
                reinforcement[f"h_0_{section}_{surface}"] = h - reinforcement[f"a_s_{section}_{surface}"]
    else:
        reinforcement["reinforcement"] = None

    return reinforcement


def is_data_for_calculations(data_to_check: dict):
    return None not in data_to_check.values()


def get_section_name(section: int):
    if section == 1:
        section_name = "middle"
    elif section == 2:
        section_name = "left"
    else:
        section_name = "right"
    return section_name


def get_program_answers_model(section: int, surface: str):
    if surface == "top":
        if section == 1:
            model = BearingCapacityMiddleTopProgram
        elif section == 2:
            model = BearingCapacityLeftTopProgram
        else:
            model = BearingCapacityRightTopProgram
    else:
        if section == 1:
            model = BearingCapacityMiddleBotProgram
        elif section == 2:
            model = BearingCapacityLeftBotProgram
        else:
            model = BearingCapacityRightBotProgram

    return model


def calculate_bearing_capacity(student: Student, surface: str):
    student_id = student.pk
    d = dict()
    d.update(rc.get_materials_properties(student_id))
    d.update(rc.get_section_geometry(student_id))
    d.update(get_calculated_reinforcement(student_id))

    if surface == "top":
        opp_surface = "bot"
        d["b"] = d["b_f"]
    else:
        opp_surface = "top"
        d["b"] = d["b_w"]

    defaults = dict()

    if is_data_for_calculations(d):
        for section in VALID_SECTIONS:
            section_name = get_section_name(section)
            model = get_program_answers_model(section=section, surface=surface)
            if surface == "top":
                ultimate_tensile_force = d["R_s"] * d[f"A_{section}_{surface}"]
                ultimate_compressive_force = d["R_b"] * d["b_f"] * d["h_f"] + \
                                             d["R_sc"] * d[f"A_{section}_{opp_surface}"]
                defaults[f"ultimate_tensile_force_{section_name}_{surface}"] = ultimate_tensile_force
                defaults[f"ultimate_compressive_force_{section_name}_{surface}"] = ultimate_compressive_force

                if ultimate_tensile_force > ultimate_compressive_force:
                    raise ValueError(f"Case Rs*As > Rsc*Asc + Rb*bf*hf is not implemented")

            compressed_zone_height = (d["R_s"] * d[f"A_{section}_{surface}"] -
                                      d["R_sc"] * d[f"A_{section}_{opp_surface}"]) / (d["R_b"] * d["b"])

            relative_compressed_zone_height = compressed_zone_height / d[f"h_0_{section}_{surface}"]

            if compressed_zone_height < d[f"a_s_{section}_{opp_surface}"] * 1.01:
                bearing_capacity_a = d["R_s"] * d[f"A_{section}_{surface}"] * (d[f"h_0_{section}_{surface}"] -
                                                                               d[f"a_s_{section}_{opp_surface}"])
            else:
                bearing_capacity_a = d["R_b"] * d["b"] * compressed_zone_height * (d[f"h_0_{section}_{surface}"] -
                                                                                   compressed_zone_height / 2) + \
                    d["R_sc"] * d[f"A_{section}_{opp_surface}"] * (d[f"h_0_{section}_{surface}"] -
                                                                               d[f"a_s_{section}_{opp_surface}"])

            compressed_zone_height_b = (d["R_s"] * d[f"A_{section}_{surface}"]) / (d["R_b"] * d["b"])

            if compressed_zone_height_b < 2 * d[f"a_s_{section}_{opp_surface}"]:
                bearing_capacity_b = d["R_s"] * d[f"A_{section}_{surface}"] * (d[f"h_0_{section}_{surface}"] -
                                                                               compressed_zone_height_b / 2)
            else:
                bearing_capacity_b = 0

            if bearing_capacity_b != 0:
                ultimate_bearing_capacity = min(bearing_capacity_a, bearing_capacity_b)
            else:
                ultimate_bearing_capacity = bearing_capacity_a

            defaults[f"compressed_zone_height_a_{section_name}_{surface}"] = compressed_zone_height
            defaults[f"relative_compressed_zone_height_a_{section_name}_{surface}"] = relative_compressed_zone_height
            defaults[f"bearing_capacity_a_{section_name}_{surface}"] = bearing_capacity_a
            defaults[f"compressed_zone_height_b_{section_name}_{surface}"] = compressed_zone_height_b
            defaults[f"bearing_capacity_b_{section_name}_{surface}"] = bearing_capacity_b
            defaults[f"bearing_capacity_{section_name}_{surface}"] = ultimate_bearing_capacity

            model.objects.update_or_create(student=student,
                                           defaults={**defaults})
            defaults.clear()

    else:
        for section in VALID_SECTIONS:
            section_name = get_section_name(section)
            model = get_program_answers_model(section=section, surface=surface)

            if surface == "top":
                defaults[f"ultimate_tensile_force_{section_name}_{surface}"] = None
                defaults[f"ultimate_compressive_force_{section_name}_{surface}"] = None

            defaults[f"compressed_zone_height_a_{section_name}_{surface}"] = None
            defaults[f"relative_compressed_zone_height_a_{section_name}_{surface}"] = None
            defaults[f"bearing_capacity_a_{section_name}_{surface}"] = None
            defaults[f"compressed_zone_height_b_{section_name}_{surface}"] = None
            defaults[f"bearing_capacity_b_{section_name}_{surface}"] = None
            defaults[f"bearing_capacity_{section_name}_{surface}"] = None

            model.objects.update_or_create(student=student,
                                           defaults={**defaults})
            defaults.clear()


