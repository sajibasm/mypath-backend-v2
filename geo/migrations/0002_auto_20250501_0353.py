from django.db import migrations


def insert_regions(apps, schema_editor):
    Region = apps.get_model("geo", "Region")

    region_data = [
        {"id": "1baaa058a49641b18aafdd1642ecb73a", "name": "Polar", "wikiDataId": "Q51"},
        {"id": "3084d8293c4f492aaff2df05768d263a", "name": "Americas", "wikiDataId": "Q828"},
        {"id": "6e4977a9287e4fc69ee409e35d468809", "name": "Europe", "wikiDataId": "Q46"},
        {"id": "e4f24e31e0f64769b0b60449e34c479b", "name": "Asia", "wikiDataId": "Q48"},
        {"id": "f213b5ded0bd44c9b53128a9e93859fd", "name": "Africa", "wikiDataId": "Q15"},
        {"id": "fbf1f6c7b92a4706998ba030a7e38db5", "name": "Oceania", "wikiDataId": "Q55643"},
    ]

    for region in region_data:
        Region.objects.update_or_create(
            id=region["id"],
            defaults={
                "name": region["name"],
                "wikiDataId": region["wikiDataId"]
            }
        )
        print(f"✅ Inserted region: {region['name']}")


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(insert_regions),
    ]
