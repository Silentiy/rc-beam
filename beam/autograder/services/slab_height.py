from autograder.models import (PersonalVariantsCivilEngineers, PersonalVariantsArchitects,
                               Student, Group, SlabHeight,)


def get_slab(student: Student, group_name: str):
    student_group_name = group_name
    student_group_id = student.group.pk
    student_subgroup_variant_number = student.subgroup_variant_number
    student_personal_variant_number = student.personal_variant_number

    if "ПГС" in student_group_name:
        student_personal_variant = PersonalVariantsCivilEngineers.objects.filter(personal_variant=
                                                                             student_personal_variant_number).first()
    else:
        student_personal_variant = PersonalVariantsArchitects.objects.filter(personal_variant=
                                                                             student_personal_variant_number).first()

    girder_name = student_personal_variant.girder

    if "ВЭ" in girder_name:
        slab_floor = "ВЭ"
    else:
        slab_floor = "РЭ"

    slab_personal_variant = PersonalVariantsCivilEngineers.objects.filter(slab__contains=slab_floor).first()
    slab_personal_variant_number = slab_personal_variant.personal_variant

    slab_student_id = Student.objects.filter(group__id=student_group_id,
                                             subgroup_variant_number=student_subgroup_variant_number,
                                             personal_variant_number=slab_personal_variant_number).first().pk

    return SlabHeight.objects.get(student_id=slab_student_id)
