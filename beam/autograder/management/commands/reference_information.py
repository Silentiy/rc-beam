import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from autograder.models import Concrete, Reinforcement


class Command(BaseCommand):
    help = 'Inserting reference information about materials, constructions and loads' \
           'from files in "data" folder into DB'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handler(self, *args, **options):
        with open(options['path'], 'r') as file:
            # Retrieve concrete info
            concrete_data_frame = pd.read_excel(file, sheet_name='Concrete_R',
                                        usecols='B:P', skiprows=2, header=0, index_col=0)

            concrete_data_frame = concrete_data_frame.transpose()

            # Write concrete info to DB
            for row in concrete_data_frame.itertuples(index=True):
                concrete_data_row = Concrete.objects.create()
                concrData = (row.Index, row.Rbn, row.Rbtn, row.Rb, row.Rbt, row.Eb)
