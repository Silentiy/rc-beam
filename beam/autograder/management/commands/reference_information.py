import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Concrete, ConcreteCreepCoefficient, Reinforcement,
                               ReinforcementBarsDiameters, ReinforcementWiresDiameters,
                               ReinforcementStrandsGeneralDiameters, ReinforcementStrandsCrimpedDiameters,
                               ReinforcementStrands1500Diameters, ReinforcementStrands16001700Diameters)


def write_reinforcement_diameters(dataframe, model_name):
    for row in dataframe.itertuples(index=True):
        model_name.objects.update_or_create(diameter=row.d,
                                            defaults={"cross_section_area": row.As,
                                                      "meter_mass": row.m}
                                            )


def write_materials_properties(path_to_file):
    # read concrete strength properties from Excel file
    concrete_strength_data_frame = pd.read_excel(path_to_file,
                                                 sheet_name='Concrete_R',
                                                 usecols='B:P',
                                                 skiprows=2,
                                                 header=0,
                                                 index_col=0)
    concrete_strength_data_frame = concrete_strength_data_frame.transpose()
    # write concrete strength properties info DB
    for row in concrete_strength_data_frame.itertuples(index=True):
        Concrete.objects.update_or_create(concrete_class=row.Index,
                                          defaults={"R_b_n": row.Rbn,
                                                    "R_bt_n": row.Rbtn,
                                                    "R_b": row.Rb,
                                                    "R_bt": row.Rbt,
                                                    "E_b=": row.Eb}
                                          )

    # read concrete creep coefficients from Excel file
    concrete_creep_data_frame = pd.read_excel(path_to_file,
                                              sheet_name='Concrete_fi_b_cr',
                                              usecols='B:L',
                                              skiprows=2,
                                              header=0,
                                              index_col=0).dropna()
    concrete_creep_data_frame = concrete_creep_data_frame.transpose()
    # write concrete creep coefficients into DB
    for row in concrete_creep_data_frame.itertuples(index=True):
        ConcreteCreepCoefficient.objects.update_or_create(concrete_class=row.Index,
                                                          defaults={"creep_for_humidity_high": row.hum_high,
                                                                    "creep_for_humidity_normal": row.hum_normal,
                                                                    "creep_for_humidity_low": row.hum_low}
                                                          )

    # read reinforcement strength data from Excel file
    reinforcement_strength_data_frame = pd.read_excel(path_to_file,
                                                      sheet_name='Reinf_R',
                                                      usecols='B:H',
                                                      skiprows=2,
                                                      header=0,
                                                      index_col=0,
                                                      na_values='-')
    reinforcement_strength_data_frame['Rsw'].fillna(0, inplace=True)
    # write reinforcement strength data into DB
    for row in reinforcement_strength_data_frame.itertuples(index=True):
        Reinforcement.objects.update_or_create(reinforcement_class=row.Index,
                                               defaults={"possible_diameters": row.ds,
                                                         "R_s_ser": row.Rsser,
                                                         "R_s": row.Rs,
                                                         "R_sc_l": row.Rsc_l,
                                                         "R_sc_sh": row.Rsc_sh,
                                                         "R_sw": row.Rsw}
                                               )


class Command(BaseCommand):
    help = 'Inserting reference information about materials, constructions and loads' \
           'from files in "data" folder into DB'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        path_to_file = options['path']

        if "cities_data" in path_to_file:
            pass
        elif "constructions" in path_to_file:
            pass
        elif "cranes" in path_to_file:
            pass
        elif "env_loads" in path_to_file:
            pass

        elif "materials" in path_to_file:
            write_materials_properties(path_to_file)
        elif "reinf_diameters" in path_to_file:


            # bars (A class)
            bars_data_frame = pd.read_excel(path_to_file,
                                            sheet_name='Bars',
                                            usecols='B:D',
                                            skiprows=2,
                                            header=0).dropna()
            write_reinforcement_diameters(dataframe=bars_data_frame,
                                          model_name=ReinforcementBarsDiameters)

            # wires (B class)
            wires_data_frame = pd.read_excel(path_to_file,
                                             sheet_name='Wires',
                                             usecols='B:D',
                                             skiprows=2,
                                             header=0).dropna()

            # usual strands
            strands_usual_data_frame = pd.read_excel(path_to_file,
                                                     sheet_name='StrandsUsual',
                                                     usecols='B:D',
                                                     skiprows=2,
                                                     header=0).dropna()

            # crimped strands
            strands_crimped_data_frame = pd.read_excel(path_to_file,
                                                       sheet_name='StrandsCrimped',
                                                       usecols='B:D',
                                                       skiprows=2,
                                                       header=0).dropna()

            # K1500 strands
            strands_1500_data_frame = pd.read_excel(path_to_file,
                                                    sheet_name='Strands1500',
                                                    usecols='B:D',
                                                    skiprows=2,
                                                    header=0).dropna()

            # K1600 and K1700 strands
            strands_1600_1700_data_frame = pd.read_excel(path_to_file,
                                                         sheet_name='Strands16001700',
                                                         usecols='B:D',
                                                         skiprows=2,
                                                         header=0).dropna()
