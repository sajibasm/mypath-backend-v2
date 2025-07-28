# device/models.py
from django.db import models

class SessionData(models.Model):
    user_id = models.IntegerField()
    start_timestamp = models.BigIntegerField()
    end_timestamp = models.BigIntegerField()
    steps_taken = models.IntegerField(default=0)
    wheelchair_id = models.IntegerField()
    start_quality_1 = models.CharField(max_length=10, default="0")
    start_quality_2 = models.CharField(max_length=10, default="0")
    start_quality_3 = models.CharField(max_length=10, default="0")
    end_quality_1 = models.CharField(max_length=10, default="0")
    end_quality_2 = models.CharField(max_length=10, default="0")
    version = models.CharField(max_length=20, default="old")
    duration_ms = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.start_timestamp and self.end_timestamp:
            self.duration_ms = self.end_timestamp - self.start_timestamp
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SessionData ({self.user_id}, {self.start_timestamp} - {self.end_timestamp})"

    class Meta:
        db_table = "device_session_data"
        verbose_name = "Device Session Data"
        verbose_name_plural = "Device Session Data"


class SensorData(models.Model):
    timestamp = models.CharField(max_length=20)
    event = models.CharField(max_length=25)
    session = models.ForeignKey(SessionData, null=True, blank=True, on_delete=models.SET_NULL, related_name="sensors")

    accel_x = models.CharField(max_length=20)
    accel_y = models.CharField(max_length=20)
    accel_z = models.CharField(max_length=20)
    gyro_x = models.CharField(max_length=20)
    gyro_y = models.CharField(max_length=20)
    gyro_z = models.CharField(max_length=20)
    mag_x = models.CharField(max_length=20)
    mag_y = models.CharField(max_length=20)
    mag_z = models.CharField(max_length=20)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    pressure = models.CharField(max_length=20)
    speed = models.CharField(max_length=20)

    def __str__(self):
        return f"Sensor Data ({self.timestamp})"

    class Meta:
        db_table = "device_sensor_data"
        verbose_name = "Sensor Insight"
        verbose_name_plural = "Sensor Insights"
