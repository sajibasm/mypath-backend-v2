from django.db import models
# Create your models here.

class WheelchairType(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "wheelchair_type"
        verbose_name = "WheelchairType"
        verbose_name_plural = "WheelchairsType"


class WheelchairDriveType(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "wheelchair_drive_type"
        verbose_name = "WheelchairDriveType"
        verbose_name_plural = "WheelchairDriveType"


class WheelchairTireMaterial(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    name = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "wheelchair_tire_material"
        verbose_name = "WheelchairTireMaterial"
        verbose_name_plural = "WheelchairTireMaterial"

