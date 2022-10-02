import os
import fitz
import string
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Group, Student, VariantInfo,
                               Concrete, ConcreteCreepCoefficient, Reinforcement,
                               ReinforcementBarsDiameters, ReinforcementWiresDiameters,
                               ReinforcementStrandsGeneralDiameters, ReinforcementStrandsCrimpedDiameters,
                               ReinforcementStrands1500Diameters, ReinforcementStrands16001700Diameters,
                               SnowLoads, WindLoads, WindKCoefficient,
                               CraneParameters, CraneSupports,
                               SlabReferenceGeometry, TrussName, TrussParameters,
                               Cities, RoofLayers, FloorLayers)


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


# def concr_ID(str_data):
#     concrete = str_data.replace('В', 'B')  # 'CYRILLIC CAPITAL LETTER VE' to ASCII 'B'
#     cur.execute('SELECT id FROM Concrete WHERE c_class = ? ', (concrete,))
#     concreteID = cur.fetchone()[0]
#     return concreteID
#
#
# def reinf_ID(str_data):
#     reinf = str_data.strip()
#     # print(reinf)
#     cur.execute('SELECT id FROM Reinforcement WHERE r_class = ? ', (reinf,))
#     reinfID = cur.fetchone()[0]
#     return reinfID


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
                    group_year = int("20" + group_name[-4:-3])
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
                    roof_layers_list = list()
                    roof_layers_thickness_list = list()
                    layer_number = 1
                    for lin in roof_layers_lines:
                        # parsing to get layer name, density and distributed weight
                        layer = Layer(lines[lin])
                        # retrieving or creation of RoofLayers object
                        roof_layer, created = \
                            RoofLayers.objects.get_or_create(layer_name=layer.layer_name,
                                                             defaults={"layer_density": layer.layer_density,
                                                                       "layer_distributed_weight": layer.layer_weight})
                        roof_layers_list.append()
                        # thicknesses of layers in current variant
                        roof_layers_thickness_list.append(parse_layer_thickness(lines[lin + 1]))
                        defaults["roof_layer_" + str(layer_number)] = roof_layer


                        layer_number += 1
                    # floor layers
                    floor_layers_lines = [47, 49, 51, 53, 55]
                    floor_layers_list = list()
                    floor_layers_thickness_list = list()
                    layer_number = 1
                    for lin in floor_layers_lines:
                        layer = Layer(lines(lin))
                        floor_layer, created = \
                            FloorLayers.objects.get_or_create(layer_name=layer.layer_name,
                                                              defaults={"layer_density": layer.layer_density,
                                                                        "layer_distributed_weight": layer.layer_weight})
                        floor_layers_list.append(floor_layer)
                        floor_layers_thickness_list.append(parse_layer_thickness(lines[lin + 1]))

                    # loads
                    defaults["roof_load_full"] = int(lines[58])
                    defaults["roof_load_long"] = int(lines[60])
                    defaults["top_floor_load_full"] = int(lines[66])
                    defaults["top_floor_load_long"] = int(lines[68])
                    defaults["usual_floor_load_full"] = int(lines[62])
                    defaults["usual_floor_load_long"] = int(lines[64])

                    # students
                    student_name_lines = [71, 73, 75]
                    for num in student_name_lines:
                        if 'группа' in lines[num]:  # check if there are only 2 student for 1 variant

                            calcVar = int(lines[num + 1])

                            stNameList = lines[num].split()
                            studName = stNameList[:-2]
                            # print(studName)
                            studNameL = studName[0].translate(str.maketrans('', '', string.punctuation))

                            if len(studNameL) == 0:  # if there actually 2 students, but we have place for third and its empty
                                studNameL = "LastName" + str(groupID) + str(variant_number) + str(calcVar)
                                # (we want to calculate everything in our building)

                            try:  # if there not full names of sudents
                                studNameF = studName[1].translate(str.maketrans('', '', ','))
                            except:
                                studNameF = None
                            try:
                                studNameM = studName[2].translate(str.maketrans('', '', string.punctuation))
                            except:
                                studNameM = None

                            cur.execute('''INSERT OR IGNORE INTO Students
                            (f_name, m_name, l_name,
                            group_id, variant_number, calc_var)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                                        (studNameF, studNameM, studNameL, groupID, variant_number, calcVar))
                    conn.commit()
                else:  # even page
                    # roof slab materials
                    roofSlabConcreteID = concr_ID(lines[6])
                    roofSlabReinfID = reinf_ID(lines[8])
                    roofSlabPTReinfID = reinf_ID(lines[10])
                    # top floor slab materials
                    topSlabConcreteID = concr_ID(lines[18])
                    topSlabReinfID = reinf_ID(lines[20])
                    topSlabPTReinfID = reinf_ID(lines[22])
                    # usual floor slab materials
                    usualSlabConcreteID = concr_ID(lines[12])
                    usualSlabReinfID = reinf_ID(lines[14])
                    usualSlabPTReinfID = reinf_ID(lines[16])
                    # truss materials
                    trussConcreteID = concr_ID(lines[24])
                    trussReinfID = reinf_ID(lines[26])
                    trussPTReinfID = reinf_ID(lines[28])
                    # girder materials
                    girderConcreteID = concr_ID(lines[30])
                    girderReinfID = reinf_ID(lines[32])
                    # column materials
                    columnConcreteID = concr_ID(lines[34])
                    columnReinfID = reinf_ID(lines[36])
                    # foundation materials
                    foundationConcreteID = concr_ID(lines[38])
                    foundationReinfID = reinf_ID(lines[40])

                    # ground
                    ground_natural = float(lines[42].replace(',', '.'))
                    ground_unnatural = float(lines[44].replace(',', '.'))

                # variant_info object creation or update
                VariantInfo.objects.update_or_create(group=group,
                                                     variant_number=variant_number,
                                                     defaults=defaults)
