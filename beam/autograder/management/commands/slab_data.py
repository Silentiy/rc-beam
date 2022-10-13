import os
import fitz
import pandas as pd
import string
import secrets
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Group, Student, SlabHeight)
from django.contrib.auth.models import User
from pathlib import Path


class Command(BaseCommand):
    help = "Retrieves data from temporary file with slabs' heights and writes them into DB"

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        path_to_file = options['path']

        with open(path_to_file, "r") as data:
            lines = data.readlines()
            for line in lines:
                values = line.split()
                group_name = values[0]
                subgroup_variant_number = int(values[1])
                personal_variant_number = int(values[2])
                slab_height = float(values[3])
                group_id = Group.objects.get(group_name=group_name).pk
                student = Student.objects.get(group_id=group_id,
                                              subgroup_variant_number=subgroup_variant_number,
                                              personal_variant_number=personal_variant_number)
                SlabHeight.objects.create(student=student,
                                          slab_height=slab_height)


