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


class Command(BaseCommand):
    help = 'Inserting reference information about materials, constructions and loads' \
           'from files in "data" folder into DB'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):