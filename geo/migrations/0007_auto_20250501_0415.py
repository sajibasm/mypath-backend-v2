import csv
import os
from django.db import migrations
from django.contrib.gis.geos import Point

def load_cities_from_csv(apps, schema_editor):
    City = apps.get_model("geo", "City")

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "csv/geo_city.csv")

    batch_size = 1000
    cities_batch = []
    inserted = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                location = Point(longitude, latitude)  # (lng, lat)
            except (ValueError, TypeError):
                location = None

            city = City(
                id=row['id'],
                name=row['name'],
                country_code=row['country_code'],
                state_code=row['state_code'],
                wikiDataId=row['wikiDataId'],
                location=location
            )
            cities_batch.append(city)

            if len(cities_batch) == batch_size:
                City.objects.bulk_create(cities_batch, ignore_conflicts=True)
                print(f"✅ Inserted batch of {batch_size}")
                inserted += len(cities_batch)
                cities_batch.clear()

        # Insert remaining cities
        if cities_batch:
            City.objects.bulk_create(cities_batch, ignore_conflicts=True)
            print(f"✅ Inserted final batch of {len(cities_batch)}")
            inserted += len(cities_batch)

    print(f"✅ Total cities inserted: {inserted}")

class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0006_auto_20250501_0413"),  # Update to your actual latest migration
    ]

    operations = [
        migrations.RunPython(load_cities_from_csv),
    ]
