from django.db import models


class Group(models.Model):
    group_year = models.PositiveSmallIntegerField()
    group_name = models.CharField(
        max_length=12)

    def __str__(self):
        return self.group_name


class Student(models.Model):
    full_name = models.CharField(
        max_length=300,
        help_text="Family name, given name, patronymic (if acceptable)"
    )
    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=False)
    subgroup_variant_number = models.PositiveSmallIntegerField()
    personal_variant_number = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.full_name) + " " + str(self.group)
