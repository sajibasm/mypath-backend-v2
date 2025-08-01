# Generated by Django 4.2.9 on 2025-05-20
from django.db import migrations
import csv
from pathlib import Path

def load_sensor_data(apps, schema_editor):
    SensorData = apps.get_model('device', 'SensorData')

    csv_path = Path(__file__).resolve().parent / 'csv' / 'device_sensor_data.csv'
    batch_size = 5000
    batch = []
    inserted = 0

    # Calculate total rows (excluding header)
    with open(csv_path, newline='', encoding='utf-8') as f:
        total_rows = sum(1 for _ in f) - 1

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            batch.append(SensorData(
                id=row['id'],
                timestamp=row['time_stamp'],
                event=row['e'],
                accel_x=row['ax'],
                accel_y=row['ay'],
                accel_z=row['az'],
                gyro_x=row['gx'],
                gyro_y=row['gy'],
                gyro_z=row['gz'],
                mag_x=row['mx'],
                mag_y=row['my'],
                mag_z=row['mz'],
                latitude=row['lat'],
                longitude=row['lng'],
                pressure=row['p'],
                speed=row['s']
            ))

            if len(batch) == batch_size:
                SensorData.objects.bulk_create(batch, ignore_conflicts=True)
                inserted += len(batch)
                batch.clear()
                percent = (inserted / total_rows) * 100
                print(f"📊 Loading: {percent:.2f}% (inserted {inserted} of {total_rows} rows)")

        # Insert remaining items
        if batch:
            SensorData.objects.bulk_create(batch, ignore_conflicts=True)
            inserted += len(batch)
            percent = (inserted / total_rows) * 100
            print(f"📊 Finalizing: {percent:.2f}% (inserted {inserted} of {total_rows} rows)")

    print(f"✅ Total sensor records inserted: {inserted}")

class Migration(migrations.Migration):

    dependencies = [
        ('device', '0002_init_migration'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(load_sensor_data),
    ]
