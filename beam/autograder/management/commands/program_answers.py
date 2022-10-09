import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Group, Student, VariantInfo,
                               Concrete, Reinforcement,
                               Cities, RoofLayers, FloorLayers,
                               ConcreteStudentAnswers, ConcreteProgramAnswers, ConcreteAnswersStatistics)
from django.contrib.auth.models import User


def get_concrete_parameters(students: list):
    for student in students:
        student_id = student.pk
        student_variant = student.subgroup_variant_number
        student_calc_variant = student.personal_variant_number
        
        


class Command(BaseCommand):
    help = 'Defines answers which possible to get without user inputted data' \
           'and inserts them to according "..._program_answers" tables in DB'

    def add_arguments(self, parser):
        parser.add_argument('--group', type=str)

    def handle(self, *args, **options):
        group_name = options["group"]

        try:
            group_id = Group.objects.get(group_name=group_name)
        except Group.ObjectDoesNotExist as e:
            print(e)
            quit()
        
        student_list = Student.objects.filter(group_id=group_id)
        
        get_concrete_parameters(student_list)