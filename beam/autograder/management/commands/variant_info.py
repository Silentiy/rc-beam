import os
import fitz
import string
import secrets
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Group, Student, VariantInfo,
                               Concrete, Reinforcement,
                               Cities, RoofLayers, FloorLayers)
from django.contrib.auth.models import User


class Layer:
    def __init__(self, str_data):
        self.str_data = str_data
        self.layer_name = self._parse_layers_data(self.str_data)[0]
        self.layer_density = self._parse_layers_data(self.str_data)[1]
        self.layer_weight = self._parse_layers_data(self.str_data)[2]

    def _parse_layers_data(self, str_data):
        """ Parses given string and returns layer_name, layer_density, layer_weight
         if string is correct """
        if 'q' in str_data:  # 'q' is in line, we will catch weight of a layer
            symbol_position = str_data.find('q')
            layer_density = None
            layer_weight = float(str_data[symbol_position + 2:].split()[0].replace(',', '.'))
            layer_name = str_data[2:symbol_position - 2]
            return layer_name, layer_density, layer_weight
        elif 'γ' in str_data:  # there is 'γ' in line, we will catch density of a layer
            symbol_position = str_data.find('γ')
            layer_weight = None
            layer_density = float(str_data[symbol_position + 2:].split()[0].replace(',', '.'))
            if layer_density <= 10:  # mistakes in pdf, 'q' and 'γ' mixed up...
                layer_weight = layer_density
                layer_density = None
            layer_name = str_data[2:symbol_position - 2]
            return layer_name, layer_density, layer_weight
        else:
            print("Incorrect input for parsing layers data!")


def parse_layer_thickness(line_data: str):
    if "-" in line_data:
        thickness = None
    else:
        thickness = int(line_data[:-2].translate(str.maketrans('', '', string.punctuation)))
    return thickness


def get_concrete(str_data: str):
    concrete_class = str_data.replace('В', 'B')  # 'CYRILLIC CAPITAL LETTER VE' to ASCII 'B'
    concrete = Concrete.objects.get(concrete_class=concrete_class)
    return concrete


def get_reinforcement(str_data: str):
    reinforcement_class = str_data.strip()
    reinforcement = Reinforcement.objects.get(reinforcement_class=reinforcement_class)
    return reinforcement


class Command(BaseCommand):
    help = "Retrieves data from blanks in *.pdf with students' variant data" \
           "and transfers it into VariantInfo table in DB"

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        path_to_files = options['path']

        # list of files for further processing
        pdf_files_list = list()
        pdf_names = os.listdir(path_to_files)
        for pdf in pdf_names:
            pdf_files_list.append(path_to_files + '\\' + pdf)

        page_number = 0
        defaults = dict()
        for doc_name in pdf_files_list:
            # check if file is accessible
            try:
                with open(doc_name):
                    print(f"Connected to {doc_name}")
            except FileNotFoundError as e:
                print(e)
                print(f"Add files to folder {path_to_files}!")
                quit()

            # open pdf
            doc = fitz.open(doc_name)

            # parse information
            for page in doc:
                text = page.get_text()
                lines = text.splitlines()
                page_number += 1

                if not page_number % 2 == 0:  # we have odd page
                    # variant number, group_name and group_year
                    variant = lines[4].split()
                    variant_number = variant[3]
                    group_name = variant[1]
                    group_year = int("20" + group_name[-5:-3])
                    print(group_year)
                    group, created = Group.objects.get_or_create(group_name=group_name,
                                                                 defaults={"group_year": group_year})
                    # city
                    city_name = lines[6]
                    defaults["city"] = Cities.objects.get(city_name=city_name)

                    # girder
                    defaults["girder_type"] = lines[26]

                    # general info about building
                    defaults["num_of_floors"] = int(lines[8])
                    defaults["floor_height"] = float(lines[10].replace(',', '.'))
                    defaults["building_length"] = int(lines[12])
                    defaults["building_width"] = int(lines[20])
                    try:
                        crane_height = float(lines[14].replace(',', '.'))
                        crane_capacity = float(lines[16].replace(',', '.'))
                    except ValueError as e:
                        crane_height = None
                        crane_capacity = None
                    defaults["crane_height"] = crane_height
                    defaults["crane_capacity"] = crane_capacity

                    defaults["girder_length"] = int(lines[24])
                    defaults["frames_spacing"] = int(lines[28])
                    defaults["roof_slab_width"] = float(lines[30].replace(',', '.'))
                    defaults["top_slab_width"] = float(lines[34].replace(',', '.'))
                    defaults["usual_slab_width"] = float(lines[32].replace(',', '.'))

                    # roof layers
                    roof_layers_lines = [37, 39, 41, 43, 45]
                    layer_number = 1
                    for lin in roof_layers_lines:
                        layer = Layer(lines[lin])
                        roof_layer, created = \
                            RoofLayers.objects.get_or_create(layer_name=layer.layer_name,
                                                             defaults={"layer_density": layer.layer_density,
                                                                       "layer_distributed_weight": layer.layer_weight})
                        defaults["roof_layer_" + str(layer_number)] = roof_layer
                        defaults["roof_layer_" + str(layer_number) + "_thickness"] = parse_layer_thickness(
                            lines[lin + 1])
                        layer_number += 1

                    # floor layers
                    floor_layers_lines = [47, 49, 51, 53, 55]
                    layer_number = 1
                    for lin in floor_layers_lines:
                        layer = Layer(lines[lin])
                        floor_layer, created = \
                            FloorLayers.objects.get_or_create(layer_name=layer.layer_name,
                                                              defaults={"layer_density": layer.layer_density,
                                                                        "layer_distributed_weight": layer.layer_weight})
                        defaults["floor_layer_" + str(layer_number)] = floor_layer
                        defaults["floor_layer_" + str(layer_number) + "_thickness"] = parse_layer_thickness(
                            lines[lin + 1])
                        layer_number += 1

                    # loads
                    defaults["roof_load_full"] = int(lines[58])
                    defaults["roof_load_long"] = int(lines[60])
                    defaults["top_floor_load_full"] = int(lines[66])
                    defaults["top_floor_load_long"] = int(lines[68])
                    defaults["usual_floor_load_full"] = int(lines[62])
                    defaults["usual_floor_load_long"] = int(lines[64])

                    # students and users
                    student_name_lines = [71, 73, 75]
                    for num in student_name_lines:
                        # if there is no word 'группа' in line, so student data is not supposed to be in this line
                        if 'группа' in lines[num]:
                            personal_variant_number = int(lines[num + 1])
                            student_data = lines[num].split()
                            student_full_name = student_data[:-2]
                            student_last_name = student_full_name[0].translate(
                                str.maketrans('', '', string.punctuation))

                            # if there are actually 2 students, but we have place for 3rd and its empty
                            if len(student_last_name) == 0:
                                student_last_name = "LastName" + str(group.pk) + \
                                                    str(variant_number) + str(personal_variant_number)
                            # there could be not full names of students
                            try:
                                student_first_name = student_full_name[1].translate(str.maketrans('', '', ','))
                            except IndexError:
                                student_first_name = None
                            try:
                                student_middle_name = student_full_name[2].translate(
                                    str.maketrans('', '', string.punctuation))
                            except IndexError:
                                student_middle_name = None
                            username = str(group.group_name) + "-" + \
                                       str(variant_number) + "-" + str(personal_variant_number)
                            first_access_password = secrets.token_urlsafe(6)

                            try:
                                User.objects.get_by_natural_key(username=username)
                            except ObjectDoesNotExist:
                                user = User.objects.create_user(username=username,
                                                                first_name=student_first_name if student_first_name is not None else "?",
                                                                last_name=student_last_name,
                                                                password=first_access_password)
                                student = Student.objects.update_or_create(group=group,
                                                                           subgroup_variant_number=variant_number,
                                                                           personal_variant_number=personal_variant_number,
                                                                           defaults={"full_name": student_full_name,
                                                                                     "user": user,
                                                                                     "first_access_password":
                                                                                         first_access_password}
                                                                           )
                else:  # even page
                    # roof slab materials
                    defaults["roof_slab_concrete"] = get_concrete(lines[6])
                    defaults["roof_slab_reinforcement"] = get_reinforcement(lines[8])
                    defaults["roof_slab_pt_reinforcement"] = get_reinforcement(lines[10])
                    # top floor slab materials
                    defaults["top_slab_concrete"] = get_concrete(lines[18])
                    defaults["top_slab_reinforcement"] = get_reinforcement(lines[20])
                    defaults["top_slab_pt_reinforcement"] = get_reinforcement(lines[22])
                    # usual floor slab materials
                    defaults["usual_slab_concrete"] = get_concrete(lines[12])
                    defaults["usual_slab_reinforcement"] = get_reinforcement(lines[14])
                    defaults["usual_slab_pt_reinforcement"] = get_reinforcement(lines[16])
                    # truss materials
                    defaults["truss_concrete"] = get_concrete(lines[24])
                    defaults["truss_reinforcement"] = get_reinforcement(lines[26])
                    defaults["truss_pt_reinforcement"] = get_reinforcement(lines[28])
                    # girder materials
                    defaults["girder_concrete"] = get_concrete(lines[30])
                    defaults["girder_reinforcement"] = get_reinforcement(lines[32])
                    # column materials
                    defaults["column_concrete"] = get_concrete(lines[34])
                    defaults["column_reinforcement"] = get_reinforcement(lines[36])
                    # foundation materials
                    defaults["foundation_concrete"] = get_concrete(lines[38])
                    defaults["foundation_reinforcement"] = get_reinforcement(lines[40])

                    # ground
                    defaults["ground_natural"] = float(lines[42].replace(',', '.'))
                    defaults["ground_unnatural"] = float(lines[44].replace(',', '.'))

                    # variant_info object creation or update
                    print(defaults)
                    VariantInfo.objects.update_or_create(group=group,
                                                         variant_number=variant_number,
                                                         defaults={**defaults})
