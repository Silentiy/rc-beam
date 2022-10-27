from autograder.models import PersonalVariantsCivilEngineers, PersonalVariantsArchitects, VariantInfo, Student, Group


def determine_girder_length(student: Student):
    group = Group.objects.get(pk=student.group_id)
    group_id = group.pk
    group_name = group.group_name
    student_variant = student.subgroup_variant_number
    student_personal_variant = student.personal_variant_number
    variant_data = VariantInfo.objects.get(group_id=group_id, variant_number=student_variant)
    girder_nominal_length = variant_data.girder_length * 100

    if "ПГС" in group_name:
        personal_data = PersonalVariantsCivilEngineers.objects.get(personal_variant=student_personal_variant)
    else:
        personal_data = PersonalVariantsArchitects.objects.get(personal_variant=student_personal_variant)
    girder_position = personal_data.girder

    if "крайний" in girder_position:
        girder_length = girder_nominal_length - 40 - 20 - 4
    else:
        girder_length = girder_nominal_length - 20 - 20 - 4

    return girder_length
