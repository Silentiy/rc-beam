import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from autograder.models import Concrete, Reinforcement


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
            # Read Excel file
            concrete_data_frame = pd.read_excel(path_to_file, sheet_name='Concrete_R', usecols='B:P',
                                                skiprows=2, header=0, index_col=0)
            concrete_data_frame = concrete_data_frame.transpose()
            # Write concrete info to DB
            for row in concrete_data_frame.itertuples(index=True):
                Concrete.objects.update_or_create(concrete_class=row.Index, R_b_n=row.Rbn, R_bt_n=row.Rbtn, R_b=row.Rb,
                                                  R_bt=row.Rbt, E_b=row.Eb)
        elif "reinf_diameters" in path_to_file:
            pass




