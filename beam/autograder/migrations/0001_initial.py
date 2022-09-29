# Generated by Django 4.1.1 on 2022-09-29 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Concrete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concrete_class', models.CharField(max_length=5, unique=True)),
                ('R_b_n', models.FloatField()),
                ('R_bt_n', models.FloatField()),
                ('R_b', models.FloatField()),
                ('R_bt', models.FloatField()),
                ('E_b', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ConcreteCreepCoefficient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concrete_class', models.CharField(max_length=5, unique=True)),
                ('creep_for_humidity_high', models.FloatField()),
                ('creep_for_humidity_normal', models.FloatField()),
                ('creep_for_humidity_low', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_concrete_creep_coefficient',
            },
        ),
        migrations.CreateModel(
            name='CraneParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('building_width', models.SmallIntegerField()),
                ('crane_capacity', models.FloatField()),
                ('crane_full_length', models.FloatField()),
                ('crane_span', models.SmallIntegerField()),
                ('crane_cantilevers_length', models.FloatField()),
                ('crane_left_hook_indent', models.FloatField()),
                ('crane_right_hook_indent', models.FloatField()),
                ('crane_trolleys_base', models.FloatField()),
                ('crane_height_to_topmost_hook_position', models.FloatField()),
                ('crane_weight', models.FloatField()),
                ('crane_max_reaction', models.FloatField()),
                ('crane_min_reaction', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_crane_parameters',
            },
        ),
        migrations.CreateModel(
            name='CraneSupports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frames_spacing', models.SmallIntegerField()),
                ('crane_span', models.SmallIntegerField()),
                ('crane_capacity', models.FloatField()),
                ('crane_support_height', models.FloatField()),
                ('crane_support_meter_mass', models.FloatField()),
                ('beam_name', models.CharField(max_length=6)),
            ],
            options={
                'db_table': 'autograder_crane_supports',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_year', models.PositiveSmallIntegerField()),
                ('group_name', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='Reinforcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reinforcement_class', models.CharField(max_length=8)),
                ('possible_diameters', models.CharField(max_length=20)),
                ('R_s_ser', models.PositiveSmallIntegerField()),
                ('R_s', models.PositiveSmallIntegerField()),
                ('R_sc_l', models.PositiveSmallIntegerField()),
                ('R_sc_sh', models.PositiveSmallIntegerField()),
                ('R_sw', models.PositiveSmallIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReinforcementBarsDiameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.SmallIntegerField(unique=True)),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_bars_diameters',
            },
        ),
        migrations.CreateModel(
            name='ReinforcementStrands1500Diameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.FloatField()),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_strands_1500_diameters',
            },
        ),
        migrations.CreateModel(
            name='ReinforcementStrands16001700Diameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.FloatField()),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_strands_1600_1700_diameters',
            },
        ),
        migrations.CreateModel(
            name='ReinforcementStrandsCrimpedDiameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.FloatField()),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_strands_crimped_diameters',
            },
        ),
        migrations.CreateModel(
            name='ReinforcementStrandsGeneralDiameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.FloatField()),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_strands_general_diameters',
            },
        ),
        migrations.CreateModel(
            name='ReinforcementWiresDiameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diameter', models.SmallIntegerField()),
                ('cross_section_area', models.FloatField()),
                ('meter_mass', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_reinforcement_wires_diameters',
            },
        ),
        migrations.CreateModel(
            name='SnowLoads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snow_region', models.SmallIntegerField()),
                ('snow_load', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_snow_loads',
            },
        ),
        migrations.CreateModel(
            name='VariantInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'autograder_variant_info',
            },
        ),
        migrations.CreateModel(
            name='WindKCoefficient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effective_height_z_e', models.SmallIntegerField()),
                ('coeff_for_A_terrain', models.FloatField()),
                ('coeff_for_B_terrain', models.FloatField()),
                ('coeff_for_C_terrain', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_wind_k_coefficient',
            },
        ),
        migrations.CreateModel(
            name='WindLoads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wind_region', models.SmallIntegerField()),
                ('wind_load', models.FloatField()),
            ],
            options={
                'db_table': 'autograder_wind_loads',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text='Family name, given name, patronymic (if acceptable)', max_length=300)),
                ('subgroup_variant_number', models.PositiveSmallIntegerField()),
                ('personal_variant_number', models.PositiveSmallIntegerField()),
                ('preferred_freefall_acceleration', models.FloatField(default=10)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autograder.group')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
