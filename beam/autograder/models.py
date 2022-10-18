from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from autograder.services import *


class Group(models.Model):
    group_year = models.PositiveSmallIntegerField()
    group_name = models.CharField(max_length=12, unique=True)

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

    first_access_password = models.CharField(max_length=12)

    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ("group", "subgroup_variant_number", "personal_variant_number")

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
        return f"{self.concrete_class}"


class Reinforcement(models.Model):
    reinforcement_class = models.CharField(max_length=8)
    possible_diameters = models.CharField(max_length=20)
    R_s_ser = models.PositiveSmallIntegerField()
    R_s = models.PositiveSmallIntegerField()
    R_sc_l = models.PositiveSmallIntegerField()
    R_sc_sh = models.PositiveSmallIntegerField()
    R_sw = models.PositiveSmallIntegerField(null=True)
    alpha_R = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=3)
    xi_R = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=3)

    def __str__(self):
        return f"{self.reinforcement_class}"


class ReinforcementBarsDiameters(models.Model):
    diameter = models.SmallIntegerField(unique=True)
    cross_section_area = models.FloatField()
    meter_mass = models.FloatField()

    class Meta:
        db_table = "autograder_reinforcement_bars_diameters"

    def __str__(self):
        return f"d{self.diameter}"


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


class PersonalVariantsCivilEngineers(models.Model):
    personal_variant = models.SmallIntegerField(unique=True)
    slab = models.CharField(max_length=20)
    truss = models.CharField(max_length=20)
    girder = models.CharField(max_length=20)
    column = models.CharField(max_length=20)
    foundation = models.CharField(max_length=20)
    girder_detail = models.CharField(max_length=20)
    column_detail = models.CharField(max_length=20)

    class Meta:
        db_table = "autograder_personal_variants_civil_engineers"

    def __str__(self):
        return self.personal_variant


class PersonalVariantsArchitects(models.Model):
    personal_variant = models.SmallIntegerField(unique=True)
    slab = models.CharField(max_length=20)
    girder = models.CharField(max_length=20)
    column = models.CharField(max_length=20)
    foundation = models.CharField(max_length=20)
    girder_detail = models.CharField(max_length=20)
    column_detail = models.CharField(max_length=20)

    class Meta:
        db_table = "autograder_personal_variants_architects"

    def __str__(self):
        return self.personal_variant


class VariantInfo(models.Model):
    # general info
    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=False)
    variant_number = models.SmallIntegerField()
    city = models.ForeignKey("Cities", on_delete=models.DO_NOTHING, null=False)

    # building parameters
    num_of_floors = models.SmallIntegerField(null=False)
    floor_height = models.FloatField(null=False)
    building_length = models.SmallIntegerField(null=False)
    building_width = models.SmallIntegerField(null=False)

    crane_height = models.FloatField(null=True)
    crane_capacity = models.FloatField(null=True)

    girder_length = models.SmallIntegerField(null=False)
    girder_type = models.CharField(max_length=18)

    frames_spacing = models.SmallIntegerField(null=False)

    roof_slab_width = models.FloatField(null=False)
    top_slab_width = models.FloatField(null=False)
    usual_slab_width = models.FloatField(null=False)

    # loads
    roof_load_full = models.SmallIntegerField(null=False)
    roof_load_long = models.SmallIntegerField(null=False)

    top_floor_load_full = models.SmallIntegerField(null=False)
    top_floor_load_long = models.SmallIntegerField(null=False)

    usual_floor_load_full = models.SmallIntegerField(null=False)
    usual_floor_load_long = models.SmallIntegerField(null=False)

    # roof and floor layers
    roof_layer_1 = models.ForeignKey("RoofLayers", related_name="roof_layer_1", on_delete=models.DO_NOTHING)
    roof_layer_1_thickness = models.SmallIntegerField(null=True)
    roof_layer_2 = models.ForeignKey("RoofLayers", related_name="roof_layer_2", on_delete=models.DO_NOTHING)
    roof_layer_2_thickness = models.SmallIntegerField(null=True)
    roof_layer_3 = models.ForeignKey("RoofLayers", related_name="roof_layer_3", on_delete=models.DO_NOTHING)
    roof_layer_3_thickness = models.SmallIntegerField(null=True)
    roof_layer_4 = models.ForeignKey("RoofLayers", related_name="roof_layer_4", on_delete=models.DO_NOTHING)
    roof_layer_4_thickness = models.SmallIntegerField(null=True)
    roof_layer_5 = models.ForeignKey("RoofLayers", related_name="roof_layer_5", on_delete=models.DO_NOTHING)
    roof_layer_5_thickness = models.SmallIntegerField(null=True)

    floor_layer_1 = models.ForeignKey("FloorLayers", related_name="floor_layer_1", on_delete=models.DO_NOTHING)
    floor_layer_1_thickness = models.SmallIntegerField(null=True)
    floor_layer_2 = models.ForeignKey("FloorLayers", related_name="floor_layer_2", on_delete=models.DO_NOTHING)
    floor_layer_2_thickness = models.SmallIntegerField(null=True)
    floor_layer_3 = models.ForeignKey("FloorLayers", related_name="floor_layer_3", on_delete=models.DO_NOTHING)
    floor_layer_3_thickness = models.SmallIntegerField(null=True)
    floor_layer_4 = models.ForeignKey("FloorLayers", related_name="floor_layer_4", on_delete=models.DO_NOTHING)
    floor_layer_4_thickness = models.SmallIntegerField(null=True)
    floor_layer_5 = models.ForeignKey("FloorLayers", related_name="floor_layer_5", on_delete=models.DO_NOTHING)
    floor_layer_5_thickness = models.SmallIntegerField(null=True)

    # materials
    roof_slab_concrete = models.ForeignKey("Concrete",
                                           related_name="roof_slab_concrete",
                                           on_delete=models.DO_NOTHING
                                           )
    roof_slab_reinforcement = models.ForeignKey("Reinforcement",
                                                related_name="roof_slab_reinforcement",
                                                on_delete=models.DO_NOTHING
                                                )
    roof_slab_pt_reinforcement = models.ForeignKey("Reinforcement",
                                                   related_name="roof_slab_pt_reinforcement",
                                                   on_delete=models.DO_NOTHING
                                                   )

    top_slab_concrete = models.ForeignKey("Concrete",
                                          related_name="top_slab_concrete",
                                          on_delete=models.DO_NOTHING
                                          )
    top_slab_reinforcement = models.ForeignKey("Reinforcement",
                                               related_name="top_slab_reinforcement",
                                               on_delete=models.DO_NOTHING
                                               )
    top_slab_pt_reinforcement = models.ForeignKey("Reinforcement",
                                                  related_name="top_slab_pt_reinforcement",
                                                  on_delete=models.DO_NOTHING
                                                  )

    usual_slab_concrete = models.ForeignKey("Concrete",
                                            related_name="usual_slab_concrete",
                                            on_delete=models.DO_NOTHING
                                            )
    usual_slab_reinforcement = models.ForeignKey("Reinforcement",
                                                 related_name="usual_slab_reinforcement",
                                                 on_delete=models.DO_NOTHING
                                                 )
    usual_slab_pt_reinforcement = models.ForeignKey("Reinforcement",
                                                    related_name="usual_slab_pt_reinforcement",
                                                    on_delete=models.DO_NOTHING
                                                    )

    truss_concrete = models.ForeignKey("Concrete",
                                       related_name="truss_concrete",
                                       on_delete=models.DO_NOTHING
                                       )
    truss_reinforcement = models.ForeignKey("Reinforcement",
                                            related_name="truss_reinforcement",
                                            on_delete=models.DO_NOTHING
                                            )
    truss_pt_reinforcement = models.ForeignKey("Reinforcement",
                                               related_name="truss_pt_reinforcement",
                                               on_delete=models.DO_NOTHING
                                               )

    girder_concrete = models.ForeignKey("Concrete",
                                        related_name="girder_concrete",
                                        on_delete=models.DO_NOTHING
                                        )
    girder_reinforcement = models.ForeignKey("Reinforcement",
                                             related_name="girder_reinforcement",
                                             on_delete=models.DO_NOTHING
                                             )

    column_concrete = models.ForeignKey("Concrete",
                                        related_name="column_concrete",
                                        on_delete=models.DO_NOTHING
                                        )
    column_reinforcement = models.ForeignKey("Reinforcement",
                                             related_name="column_reinforcement",
                                             on_delete=models.DO_NOTHING
                                             )

    foundation_concrete = models.ForeignKey("Concrete",
                                            related_name="foundation_concrete",
                                            on_delete=models.DO_NOTHING
                                            )
    foundation_reinforcement = models.ForeignKey("Reinforcement",
                                                 related_name="foundation_reinforcement",
                                                 on_delete=models.DO_NOTHING
                                                 )

    # ground
    ground_natural = models.FloatField(null=False)
    ground_unnatural = models.FloatField(null=False)

    class Meta:
        db_table = "autograder_variant_info"
        unique_together = ("group", "variant_number")

    def __str__(self):
        return f"group = {self.group}, variant_number = {self.variant_number}"


class ConcreteStudentAnswers(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    stud_concrete_class = models.ForeignKey("Concrete",
                                            on_delete=models.DO_NOTHING, null=False, default=1)
    stud_R_b_n = models.FloatField()
    stud_R_bt_n = models.FloatField()
    stud_R_b = models.FloatField()
    stud_R_bt = models.FloatField()
    stud_E_b = models.PositiveIntegerField()

    class Meta:
        db_table = "autograder_concrete_student_answers"

    def __str__(self):
        return f"{self.student} {self.stud_concrete_class}"


class ConcreteAnswersStatistics(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    concrete_class = models.BooleanField()
    R_b_n = models.BooleanField()
    R_bt_n = models.BooleanField()
    R_b = models.BooleanField()
    R_bt = models.BooleanField()
    E_b = models.BooleanField()

    class Meta:
        db_table = "autograder_concrete_answers_statistics"

    def __str__(self):
        return self.student


class ReinforcementStudentAnswers(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    stud_reinforcement_class = models.ForeignKey("Reinforcement",
                                                 on_delete=models.DO_NOTHING, null=False, default=1)
    stud_R_s_ser = models.FloatField()
    stud_R_s = models.FloatField()
    stud_R_sc_l = models.FloatField()
    stud_R_sc_sh = models.FloatField()
    stud_R_sw = models.FloatField(null=True)
    stud_alpha_R = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=3)
    stud_xi_R = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=3)

    class Meta:
        db_table = "autograder_reinforcement_student_answers"

    def __str__(self):
        return f"{self.student} {self.stud_reinforcement_class}"


class ReinforcementAnswersStatistics(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    reinforcement_class = models.BooleanField()
    R_s_ser = models.BooleanField()
    R_s = models.BooleanField()
    R_sc_l = models.BooleanField()
    R_sc_sh = models.BooleanField()
    R_sw = models.BooleanField()
    alpha_R = models.BooleanField(blank=True)
    xi_R = models.BooleanField(blank=True)

    class Meta:
        db_table = "autograder_reinforcement_answers_statistics"

    def __str__(self):
        return self.student


class SlabHeight(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    slab_height = models.SmallIntegerField(null=False)

    class Meta:
        db_table = "autograder_slab_height"

    def __str__(self):
        return self.slab_height


class GirderGeometry(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)
    slab = models.ForeignKey(SlabHeight, on_delete=models.DO_NOTHING, null=True)  # is necessary?

    girder_flange_bevel_height = models.FloatField(validators=[MinValueValidator(10), MaxValueValidator(30)])
    girder_flange_slab_height = models.FloatField(validators=[MinValueValidator(5), MaxValueValidator(15)])
    girder_wall_height = models.SmallIntegerField()
    girder_wall_width = models.SmallIntegerField(validators=[MinValueValidator(30), MaxValueValidator(40)])
    girder_flange_bevel_width = models.FloatField(validators=[MinValueValidator(14.5), MaxValueValidator(20.5)])

    girder_height = models.SmallIntegerField(blank=True, null=True)
    girder_flange_full_width = models.SmallIntegerField(blank=True, null=True)
    girder_flange_console_widths = models.FloatField(blank=True, null=True)

    girder_length = models.SmallIntegerField()
    girder_effective_flange_width = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "autograder_girder_geometry"

    def determine_flange_width(self):
        """ Determines effective width of flange for T-section girder """

        girder_height = self.girder_height
        girder_length = self.girder_length
        girder_wall_width = self.girder_wall_width
        girder_flange_height = self.girder_flange_bevel_height + self.girder_flange_slab_height
        girder_flange_average_width = (self.girder_flange_full_width + girder_wall_width) / 2

        flange_widths_options = list()
        flange_widths_options.append(girder_flange_average_width)
        flange_widths_options.append(girder_length / 3 + girder_wall_width)

        if girder_flange_height < 0.05 * girder_height:
            flange_widths_options.append(girder_wall_width)

        if 0.05 * girder_height <= girder_flange_height < 0.1 * girder_height:
            flange_widths_options.append(girder_wall_width + 6 * girder_flange_height)

        if girder_flange_height >= 0.1 * girder_height:
            flange_widths_options.append(girder_wall_width + 12 * girder_flange_height)

        return min(flange_widths_options)

    def clean(self):
        if self.girder_wall_height is not None:
            self.girder_height = self.girder_wall_height + self.girder_flange_bevel_height + self.girder_flange_slab_height
            self.girder_flange_full_width = 2 * self.girder_flange_bevel_width + self.girder_wall_width
            self.girder_flange_console_widths = self.girder_flange_bevel_width - 2
            if self.girder_height > 80:
                raise ValidationError(gettext_lazy('Высота сечения ригеля должна быть не более 80 см!'))
        if self.girder_length is not None and self.girder_height is not None:
            self.girder_effective_flange_width = self.determine_flange_width()

    def __str__(self):
        return f"girder_h = {self.girder_height}"


class MomentsForces(models.Model):
    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)

    middle_section_moment_top = models.FloatField()
    middle_section_moment_bot = models.FloatField()
    middle_section_status = models.BooleanField(null=True, blank=True)

    left_support_moment_top = models.FloatField()
    left_support_moment_bot = models.FloatField()
    left_support_shear_force = models.FloatField()
    left_support_status = models.BooleanField(null=True, blank=True)

    right_support_moment_top = models.FloatField()
    right_support_moment_bot = models.FloatField()
    right_support_shear_force = models.FloatField()
    right_support_status = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "autograder_moments_forces"

    def __str__(self):
        return f"M & Q for {self.student}"


class InitialReinforcement(models.Model):
    NUMBER_EXTERNAL_BARS = [(0, 0), (2, 2)]
    NUMBER_INTERNAL_BARS = [(0, 0), (1, 1), (2, 2)]

    student = models.OneToOneField("Student", on_delete=models.CASCADE, null=False)

    # SECTION 1
    # top reinforcement external
    section_1_top_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_1_top_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_1_top_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=2)
    # top reinforcement internal
    section_1_top_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_1_top_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_1_top_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=1)
    # top reinforcement area
    section_1_top_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to top
    section_1_top_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_1_top_effective_depth = models.FloatField(null=True, blank=True)

    # bot reinforcement external
    section_1_bot_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_1_bot_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_1_bot_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=0)
    # bot reinforcement external
    section_1_bot_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_1_bot_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_1_bot_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=0)
    # bot reinforcement area
    section_1_bot_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to bot
    section_1_bot_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_1_bot_effective_depth = models.FloatField(null=True, blank=True)

    # SECTION 2
    # top reinforcement external
    section_2_top_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_2_top_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_2_top_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=0)
    # top reinforcement internal
    section_2_top_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_2_top_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_2_top_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=0)
    # top reinforcement area
    section_2_top_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to top
    section_2_top_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_2_top_effective_depth = models.FloatField(null=True, blank=True)

    # bot reinforcement external
    section_2_bot_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_2_bot_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_2_bot_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=2)
    # bot reinforcement external
    section_2_bot_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_2_bot_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_2_bot_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=1)
    # bot reinforcement area
    section_2_bot_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to bot
    section_2_bot_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_2_bot_effective_depth = models.FloatField(null=True, blank=True)

    # SECTION 3
    # top reinforcement external
    section_3_top_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_3_top_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_3_top_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=0)
    # top reinforcement internal
    section_3_top_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_3_top_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_3_top_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=0)
    # top reinforcement area
    section_3_top_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to top
    section_3_top_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_3_top_effective_depth = models.FloatField(null=True, blank=True)

    # bot reinforcement external
    section_3_bot_d_external = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_3_bot_external",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_3_bot_n_external = models.PositiveSmallIntegerField(choices=NUMBER_EXTERNAL_BARS, default=2)
    # bot reinforcement external
    section_3_bot_d_internal = models.ForeignKey("ReinforcementBarsDiameters",
                                                 related_name="section_3_bot_internal",
                                                 on_delete=models.DO_NOTHING, null=True, default=1)
    section_3_bot_n_internal = models.PositiveSmallIntegerField(choices=NUMBER_INTERNAL_BARS, default=1)
    # bot reinforcement area
    section_3_bot_reinforcement_area = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=3)
    # effective depths to bot
    section_3_bot_distance = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(6.5)])
    section_3_bot_effective_depth = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "autograder_initial_reinforcement"

    def get_reinforcement_area(self, section: int, surface: str):
        external_bar = getattr(self, f"section_{section}_{surface}_d_external")
        internal_bar = getattr(self, f"section_{section}_{surface}_d_internal")
        if external_bar is not None:
            external_bar_area = external_bar.cross_section_area
        else:
            external_bar_area = 0
        if internal_bar is not None:
            internal_bar_area = internal_bar.cross_section_area
        else:
            internal_bar_area = 0

        number_external_bars = getattr(self, f"section_{section}_{surface}_n_external")
        number_internal_bars = getattr(self, f"section_{section}_{surface}_n_internal")

        reinforcement_area = external_bar_area * number_external_bars + \
                             internal_bar_area * number_internal_bars  # square mm
        return reinforcement_area / 100  # square cm

    def clean(self):
        print("Clean in model started")
        self.section_1_top_reinforcement_area = self.get_reinforcement_area(section=1, surface="top")
        self.section_1_bot_reinforcement_area = self.get_reinforcement_area(section=1, surface="bot")

        self.section_2_top_reinforcement_area = self.get_reinforcement_area(section=2, surface="top")
        self.section_2_bot_reinforcement_area = self.get_reinforcement_area(section=2, surface="bot")

        self.section_3_top_reinforcement_area = self.get_reinforcement_area(section=3, surface="top")
        self.section_3_bot_reinforcement_area = self.get_reinforcement_area(section=3, surface="bot")

    def __str__(self):
        stud = self.student if hasattr(self, 'student') else "no student yet"
        return f"Initial reinforcement {stud}"
