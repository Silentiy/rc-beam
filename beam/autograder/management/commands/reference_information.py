import os
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from autograder.models import (Concrete, ConcreteCreepCoefficient, Reinforcement,
                               ReinforcementBarsDiameters, ReinforcementWiresDiameters,
                               ReinforcementStrandsGeneralDiameters, ReinforcementStrandsCrimpedDiameters,
                               ReinforcementStrands1500Diameters, ReinforcementStrands16001700Diameters,
                               SnowLoads, WindLoads, WindKCoefficient,
                               CraneParameters, CraneSupports,
                               SlabReferenceGeometry, TrussName, TrussParameters,
                               Cities)


def write_reinforcement_diameters(path_to_file):
    models_list = [ReinforcementBarsDiameters, ReinforcementWiresDiameters,
                   ReinforcementStrandsGeneralDiameters, ReinforcementStrandsCrimpedDiameters,
                   ReinforcementStrands1500Diameters, ReinforcementStrands16001700Diameters]
    bars_data_frames = pd.read_excel(path_to_file,
                                     sheet_name=None,
                                     usecols="B:D",
                                     skiprows=2,
                                     header=0)
    current_model = 0
    for sheet_name, dataframe in bars_data_frames.items():
        for row in dataframe.itertuples(index=True):
            models_list[current_model].objects.update_or_create(diameter=row.d,
                                                                defaults={"cross_section_area": row.As,
                                                                          "meter_mass": row.m}
                                                                )
        current_model += 1


def write_materials_properties(path_to_file):
    # read concrete strength properties from Excel file
    concrete_strength_data_frame = pd.read_excel(path_to_file,
                                                 sheet_name='Concrete_R',
                                                 usecols='B:P',
                                                 skiprows=2,
                                                 header=0,
                                                 index_col=0)
    concrete_strength_data_frame = concrete_strength_data_frame.transpose()
    # write concrete strength properties into DB
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


def write_environment_loads(path_to_file):
    snow_data_frame = pd.read_excel(path_to_file,
                                    sheet_name='Snow',
                                    usecols='B:J',
                                    skiprows=2,
                                    header=0,
                                    index_col=0).dropna()
    snow_data_frame = snow_data_frame.transpose()
    print(snow_data_frame)
    for row in snow_data_frame.itertuples(index=True):
        SnowLoads.objects.update_or_create(snow_region=row.Index,
                                           defaults={"snow_load": row.Sg})

    wind_data_frame = pd.read_excel(path_to_file,
                                    sheet_name='Wind',
                                    usecols='B:J',
                                    skiprows=2,
                                    header=0,
                                    index_col=0).dropna()
    wind_data_frame = wind_data_frame.transpose()
    print(wind_data_frame)
    for row in wind_data_frame.itertuples(index=True):
        WindLoads.objects.update_or_create(wind_region=row.Index,
                                           defaults={"wind_load": row.w0})


def write_wind_coefficients(path_to_file):
    wind_k_coefficient_data_frame = pd.read_excel(path_to_file,
                                                  sheet_name='Wind_k_coeff',
                                                  usecols='B:E',
                                                  skiprows=2,
                                                  header=0).dropna()
    for row in wind_k_coefficient_data_frame.itertuples(index=True):
        WindKCoefficient.objects.update_or_create(effective_height_z_e=row.z_e,
                                                  defaults={"coeff_for_A_terrain": row.A,
                                                            "coeff_for_B_terrain": row.B,
                                                            "coeff_for_C_terrain": row.C}
                                                  )


def write_crane_data(path_to_file):
    crane_parameters_data_frame = pd.read_excel(path_to_file,
                                                sheet_name='Crane_parameters',
                                                usecols='B:M',
                                                skiprows=2,
                                                header=0).dropna()
    for row in crane_parameters_data_frame.itertuples(index=True):
        CraneParameters.objects.update_or_create(building_width=row.build_width,
                                                 crane_capacity=row.cr_capacity,
                                                 defaults={"crane_full_length": row.cr_len,
                                                           "crane_span": row.cr_l0,
                                                           "crane_cantilevers_length": row.cr_nom_cantil_len,
                                                           "crane_left_hook_indent": row.cr_left_indent / 1000,
                                                           "crane_right_hook_indent": row.cr_right_indent / 1000,
                                                           "crane_trolleys_base": row.cr_trolley_base / 1000,
                                                           "crane_height_to_topmost_hook_position": row.cr_hook_h / 1000,
                                                           "crane_weight": row.cr_wgt,
                                                           "crane_max_reaction": row.cr_R_max,
                                                           "crane_min_reaction": row.cr_R_min}
                                                 )

    cranes_supports_data_frame = pd.read_excel(path_to_file,
                                               sheet_name='Crane_supports',
                                               usecols='B:G',
                                               skiprows=2,
                                               header=0).dropna()
    for row in cranes_supports_data_frame.itertuples(index=True):
        CraneSupports.objects.update_or_create(frames_spacing=row.frames_step,
                                               crane_span=row.cr_l0,
                                               crane_capacity=row.crn_capacity,
                                               defaults={"crane_support_height": row.cr_sup_h / 1000,
                                                         "crane_support_meter_mass": row.cr_sup_m,
                                                         "beam_name": row.beam_name})


def write_constructions_data(path_to_file):
    slabs_data_frame = pd.read_excel(path_to_file,
                                     sheet_name='Slabs',
                                     usecols='B:Q',
                                     skiprows=2,
                                     header=0).dropna()
    for row in slabs_data_frame.itertuples(index=True):
        SlabReferenceGeometry.objects.update_or_create(nominal_length=row.l_nom,
                                                       nominal_width=row.b_nom,
                                                       nominal_height=row.h_tot,
                                                       defaults={"load_greater_than": row.load_gr,
                                                                 "load_less_than": row.load_less,
                                                                 "slab_fact_width_bottom": row.slab_w_bot,
                                                                 "slab_fact_width_top": row.slab_w_top,
                                                                 "longitudinal_rib_width_bottom": row.b_long_bot,
                                                                 "longitudinal_rib_width_top": row.b_long_up,
                                                                 "flange_height": row.h_flange,
                                                                 "transverse_rib_outer_width_bottom": row.b_tr_out_bot,
                                                                 "transverse_rib_usual_height": row.h_tr_usual,
                                                                 "transverse_rib_outer_width_top": row.b_tr_out_up,
                                                                 "transverse_rib_usual_width_bottom": row.b_tr_us_bot,
                                                                 "transverse_rib_usual_width_top": row.b_tr_us_up,
                                                                 "transverse_ribs_spacing": row.tr_sp}
                                                       )

    truss_name_data_frame = pd.read_excel(path_to_file,
                                          sheet_name='Trusses_names',
                                          usecols='B:G',
                                          skiprows=2,
                                          header=0).dropna()
    for row in truss_name_data_frame.itertuples(index=True):
        TrussName.objects.update_or_create(truss_type=row.type,
                                           frames_spacing=row.frames_sp,
                                           load_greater_than=row.t_load_gr,
                                           load_less_than=row.t_load_less,
                                           truss_span=row.t_span,
                                           defaults={"truss_name": row.t_name})

    truss_parameters_data_frame = pd.read_excel(path_to_file,
                                                sheet_name='Trusses_parameters',
                                                usecols='B:K',
                                                skiprows=2,
                                                header=0).dropna()
    for row in truss_parameters_data_frame.itertuples(index=True):
        TrussParameters.objects.update_or_create(truss_name=row.tr_name,
                                                 defaults={"truss_length": row.t_length,
                                                           "truss_height": row.t_height,
                                                           "truss_mass": row.t_mass,
                                                           "truss_width": row.t_b,
                                                           "top_chord_cross_section_height": row.t_h1,
                                                           "bottom_chord_cross_section_height": row.t_h2,
                                                           "bracing_elements_cross_section_height": row.t_h3,
                                                           "bracing_elements_cross_section_height_extra": row.t_h4,
                                                           "bearing_knot_height": row.t_h_on_sup}
                                                 )


def write_cities_data(path_to_file):
    cities_data_frame = pd.read_excel(path_to_file,
                                                sheet_name='cities',
                                                usecols='C:G',
                                                skiprows=2,
                                                header=0)
    cities_data_frame = cities_data_frame.replace({np.nan:None})
    cities_list = cities_data_frame.to_dict(orient='records')
    for dictionary in cities_list:
        city_name = dictionary.pop('city_name')
        Cities.objects.update_or_create(city_name=city_name,
                                        defaults={**dictionary})


class Command(BaseCommand):
    help = 'Inserting reference information about materials, constructions and loads' \
           'from files in "data" folder into DB'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        path_to_file = options['path']

        try:
            with open(path_to_file):
                print(f"Connected to {path_to_file}")
        except FileNotFoundError as e:
            print(e)
            print(f"Add file {path_to_file}!")
            quit()

        if "cities_data" in path_to_file:
            write_cities_data(path_to_file)
        elif "constructions" in path_to_file:
            write_constructions_data(path_to_file)
        elif "cranes" in path_to_file:
            write_crane_data(path_to_file)
        elif "env_loads" in path_to_file:
            write_environment_loads(path_to_file)
        elif "wind_coeffs" in path_to_file:
            write_wind_coefficients(path_to_file)
        elif "materials" in path_to_file:
            write_materials_properties(path_to_file)
        elif "reinf_diameters" in path_to_file:
            write_reinforcement_diameters(path_to_file)

        print("Data inserted into DB!")
