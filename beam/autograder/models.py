from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    group_year = models.PositiveSmallIntegerField()
    group_name = models.CharField(
        max_length=12)

    def __str__(self):
        return self.group_name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    full_name = models.CharField(
        max_length=300,
        help_text="Family name, given name, patronymic (if acceptable)"
    )
    subgroup_variant_number = models.PositiveSmallIntegerField()
    personal_variant_number = models.PositiveSmallIntegerField()
    preferred_freefall_acceleration = models.FloatField(default=10)

    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.full_name) + " " + str(self.group)


class Concrete(models.Model):
    concrete_class = models.CharField(max_length=5, unique=True)
    R_b_n = models.FloatField()
    R_bt_n = models.FloatField()
    R_b = models.FloatField()
    R_bt = models.FloatField()
    E_b = models.PositiveIntegerField()

    def __str__(self):
        return self.concrete_class


class ConcreteCreepCoefficient(models.Model):
    concrete_class = models.CharField(max_length=5, unique=True)
    creep_for_humidity_high = models.FloatField()
    creep_for_humidity_normal = models.FloatField()
    creep_for_humidity_low = models.FloatField()

    class Meta:
        db_table = "autograder_concrete_creep_coefficient"

    def __str__(self):
        return self.concrete_class


class Reinforcement(models.Model):
    reinforcement_class = models.CharField(max_length=8)
    possible_diameters = models.CharField(max_length=20)
    R_s_ser = models.PositiveSmallIntegerField()
    R_s = models.PositiveSmallIntegerField()
    R_sc_l = models.PositiveSmallIntegerField()
    R_sc_sh = models.PositiveSmallIntegerField()
    R_sw = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.reinforcement_class


class ReinforcementBarsDiameters(models.Model):
    diameter = models.SmallIntegerField(unique=True)
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_bars_diameters"

    def __str__(self):
        return f"bar d{self.diameter}"


class ReinforcementWiresDiameters(models.Model):
    diameter = models.SmallIntegerField()
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_wires_diameters"

    def __str__(self):
        return f"wire d{self.diameter}"


class ReinforcementStrandsGeneralDiameters(models.Model):
    diameter = models.FloatField()
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_strands_general_diameters"

    def __str__(self):
        return f"strand d{self.diameter} (usual)"


class ReinforcementStrandsCrimpedDiameters(models.Model):
    diameter = models.FloatField()
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_strands_crimped_diameters"

    def __str__(self):
        return f"strand d{self.diameter} (crimped)"


class ReinforcementStrands1500Diameters(models.Model):
    diameter = models.FloatField()
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_strands_1500_diameters"

    def __str__(self):
        return f"strand d{self.diameter} (R=1500)"


class ReinforcementStrands16001700Diameters(models.Model):
    diameter = models.FloatField()
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_strands_1600_1700_diameters"

    def __str__(self):
        return f"strand d{self.diameter} (R=1600/1700)"


class SnowLoads(models.Model):
    snow_region = models.SmallIntegerField()
    snow_load = models.FloatField()

    class Meta:
        db_table = "autograder_snow_loads"

    def __str__(self):
        return f"Snow region: {self.snow_region}, snow load: {self.snow_load}"


class WindLoads(models.Model):
    wind_region = models.SmallIntegerField()
    wind_load = models.FloatField()

    class Meta:
        db_table = "autograder_wind_loads"

    def __str__(self):
        return f"Wind region: {self.wind_region}, wind load: {self.wind_load}"


class WindKCoefficient(models.Model):
    effective_height_z_e = models.SmallIntegerField()
    coeff_for_A_terrain = models.FloatField()
    coeff_for_B_terrain = models.FloatField()
    coeff_for_C_terrain = models.FloatField()

    class Meta:
        db_table = "autograder_wind_k_coefficient"

    def __str__(self):
        return f"Z_e: {self.effective_height_z_e}, A: {self.coeff_for_A_terrain}," \
               f" B: {self.coeff_for_B_terrain}, C: {self.coeff_for_C_terrain}"


class CraneParameters(models.Model):
    building_width = models.SmallIntegerField()
    crane_capacity = models.FloatField()
    crane_full_length = models.FloatField()
    crane_span = models.SmallIntegerField()
    crane_cantilevers_length = models.FloatField()
    crane_left_hook_indent = models.FloatField()
    crane_right_hook_indent = models.FloatField()
    crane_trolleys_base = models.FloatField()
    crane_height_to_topmost_hook_position = models.FloatField()
    crane_weight = models.FloatField()
    crane_max_reaction = models.FloatField()
    crane_min_reaction = models.FloatField()

    class Meta:
        db_table = "autograder_crane_parameters"

    def __str__(self):
        return self.crane_capacity


class CraneSupports(models.Model):
    frames_spacing = models.SmallIntegerField()
    crane_span = models.SmallIntegerField()
    crane_capacity = models.FloatField()
    crane_support_height = models.FloatField()
    crane_support_meter_mass = models.FloatField()
    beam_name = models.CharField(max_length=6)

    class Meta:
        db_table = "autograder_crane_supports"

    def __str__(self):
        return self.crane_support_height


class SlabReferenceGeometry(models.Model):
    nominal_length = models.SmallIntegerField()
    nominal_width = models.SmallIntegerField()
    nominal_height = models.SmallIntegerField()
    load_greater_than = models.SmallIntegerField()
    load_less_than = models.SmallIntegerField()
    slab_fact_width_bottom = models.SmallIntegerField()
    slab_fact_width_top = models.SmallIntegerField()
    longitudinal_rib_width_bottom = models.SmallIntegerField()
    longitudinal_rib_width_top = models.SmallIntegerField()
    flange_height = models.SmallIntegerField()
    transverse_rib_outer_width_bottom = models.SmallIntegerField()
    transverse_rib_usual_height = models.SmallIntegerField()
    transverse_rib_outer_width_top = models.SmallIntegerField()
    transverse_rib_usual_width_bottom = models.SmallIntegerField()
    transverse_rib_usual_width_top = models.SmallIntegerField()
    transverse_ribs_spacing = models.SmallIntegerField()

    class Meta:
        db_table = "autograder_slab_reference_geometry"

    def __str__(self):
        return f"LxBxH = {self.nominal_length}x{self.nominal_width}x{self.nominal_height}"


class TrussName(models.Model):
    truss_type = models.CharField(max_length=3)
    frames_spacing = models.SmallIntegerField()
    load_greater_than = models.SmallIntegerField()
    load_less_than = models.SmallIntegerField()
    truss_span = models.SmallIntegerField()
    truss_name = models.CharField(max_length=6)

    class Meta:
        db_table = "autograder_truss_name"

    def __str__(self):
        return self.truss_name


class TrussParameters(models.Model):
    truss_name = models.CharField(max_length=6)
    truss_length = models.SmallIntegerField()
    truss_height = models.SmallIntegerField()
    truss_mass = models.FloatField()
    truss_width = models.SmallIntegerField()
    top_chord_cross_section_height = models.SmallIntegerField()
    bottom_chord_cross_section_height = models.SmallIntegerField()
    bracing_elements_cross_section_height = models.SmallIntegerField()
    bracing_elements_cross_section_height_extra = models.SmallIntegerField()
    bearing_knot_height = models.SmallIntegerField()

    class Meta:
        db_table = "autograder_truss_parameters"

    def __str__(self):
        return f"{self.truss_name},m = {self.truss_mass} т"


class Cities(models.Model):
    city_name = models.CharField(max_length=32, unique=True)
    snow_region = models.SmallIntegerField(null=True)
    snow_region_2011 = models.SmallIntegerField(null=True)
    wind_region = models.SmallIntegerField(null=True)
    average_january_temp = models.SmallIntegerField(null=True)

    def __str__(self):
        return self.city_name


class RoofLayers(models.Model):
    layer_name = models.CharField(max_length=42, unique=True)
    layer_density = models.SmallIntegerField(null=True)
    layer_distributed_weight = models.FloatField(null=True)
    
    class Meta:
    db_table = "autograder_roof_layers"

    def __str__(self):
        return self.layer_name
    
        
class FloorLayers(models.Model):
    layer_name = models.CharField(max_length=42, unique=True)
    layer_density = models.SmallIntegerField(null=True)
    layer_distributed_weight = models.FloatField(null=True)

    class Meta:
    db_table = "autograder_floor_layers"

    def __str__(self):
        return self.layer_name


class VariantInfo(models.Model):
    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=False)
    variant_number = models.SmallIntegerField()
    city = models.ForeignKey("Cities", on_delete=models.DO_NOTHING, null=False)
    girder_type = models.CharField(max_length=18)
    roof_layer_1 = 


    class Meta:
        db_table = "autograder_variant_info"
        unique_together = ('group_id', 'variant_number')

    def __str__(self):
        return f"group_id = {self.group_id}, variant_number = {variant_number }"

#     roof_layer_1_id INTEGER, roof_layer_1_th INTEGER,
#     roof_layer_2_id INTEGER, roof_layer_2_th INTEGER,
#     roof_layer_3_id INTEGER, roof_layer_3_th INTEGER,
#     roof_layer_4_id INTEGER, roof_layer_4_th INTEGER,
#     roof_layer_5_id INTEGER, roof_layer_5_th INTEGER,
#     floor_layer_1_id INTEGER, floor_layer_1_th INTEGER,
#     floor_layer_2_id INTEGER, floor_layer_2_th INTEGER,
#     floor_layer_3_id INTEGER, floor_layer_3_th INTEGER,
#     floor_layer_4_id INTEGER, floor_layer_4_th INTEGER,
#     floor_layer_5_id INTEGER, floor_layer_5_th INTEGER,
#     roof_slab_concrete_id INTEGER, roof_slab_reinf_id INTEGER, roof_slab_pt_reinf_id INTEGER,
#     top_slab_concrete_id INTEGER, top_slab_reinf_id INTEGER, top_slab_pt_reinf_id INTEGER,
#     usual_slab_concrete_id INTEGER, usual_slab_reinf_id INTEGER, usual_slab_pt_reinf_id INTEGER,
#     truss_concrete_id INTEGER, truss_reinf_id INTEGER, truss_pt_reinf_id INTEGER,
#     girder_concrete_id INTEGER, girder_reinf_id INTEGER,
#     column_concrete_id INTEGER, column_reinf_id INTEGER,
#     foundation_concrete_id INTEGER, foundation_reinf_id INTEGER,
#     num_of_floors INTEGER, floor_height FLOAT, building_length INTEGER, building_width INTEGER,
#     crane_height FLOAT, crane_capacity FLOAT,
#     girder_length INTEGER, frames_spacing INTEGER,
#     roof_slab_width FLOAT, top_slab_width FLOAT, usual_slab_width FLOAT,
#     roof_load INTEGER, roof_load_l INTEGER,
#     top_floor_load INTEGER, top_floor_load_l INTEGER,
#     usual_floor_load INTEGER, usual_floor_load_l INTEGER,
#     ground_natural FLOAT, ground_unnatural FLOAT,
#     UNIQUE (group_id, var_number)
#     ); ''')

