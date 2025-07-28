from django.db import migrations
import csv
from pathlib import Path

def load_session_data(apps, schema_editor):
    SessionData = apps.get_model('device', 'SessionData')

    csv_path = Path(__file__).resolve().parent / 'csv' / 'device_session_data.csv'
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                start_ts = int(row['st'])
                end_ts = int(row['et'])
                duration = end_ts - start_ts
            except (ValueError, KeyError):
                start_ts = end_ts = duration = 0  # fallback if bad/missing data

            SessionData.objects.update_or_create(
                id=row['id'],
                defaults={
                    'user_id': row['uid'],
                    'start_timestamp': start_ts,
                    'end_timestamp': end_ts,
                    'steps_taken': row['sbt'],
                    'wheelchair_id': row['wcId'],
                    'start_quality_1': row['sq1'],
                    'start_quality_2': row['sq2'],
                    'start_quality_3': row['sq3'],
                    'end_quality_1': row['eq1'],
                    'end_quality_2': row['eq2'],
                    'version': row['v'] or 'old',
                    'duration_ms': duration,
                }
            )
            print(f"✅ Inserted session ID: {row['id']} with duration {duration}ms for user {row['uid']}")

class Migration(migrations.Migration):

    dependencies = [
        ('device', '0001_initial'),  # Update to your correct dependency
    ]

    operations = [
        migrations.RunPython(load_session_data),
    ]
