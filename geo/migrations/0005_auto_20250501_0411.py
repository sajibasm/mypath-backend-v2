from django.db import migrations
from django.contrib.gis.geos import Point

def load_country(apps, schema_editor):
    Country = apps.get_model("geo", "Country")
    Region = apps.get_model("geo", "Region")
    SubRegion = apps.get_model("geo", "SubRegion")

    # Define country data directly
    country_data = {
        "id": "7c6488e25760423a9019406ce0707b58",
        "name": "United States",
        "iso3": "USA",
        "iso2": "US",
        "numeric_code": "840",
        "phone_code": "1",
        "capital": "Washington",
        "currency": "USD",
        "currency_name": "United States dollar",
        "currency_symbol": "$",
        "tld": ".us",
        "native": "United States",
        "nationality": "American",
        "latitude": 38.000000,
        "longitude": -97.000000,
        "emoji": "🇺🇸",
        "emojiU": "U+1F1FA U+1F1F8",
        "region_id": "3084d8293c4f492aaff2df05768d263a",
        "subregion_id": "476e1e6f71814264855c042c7d78f760",
    }

    # Get related foreign key objects
    region = Region.objects.filter(id=country_data["region_id"]).first()
    subregion = SubRegion.objects.filter(id=country_data["subregion_id"]).first()

    # Create a point using (longitude, latitude)
    location = Point(country_data["longitude"], country_data["latitude"])

    # Insert or update country
    Country.objects.update_or_create(
        id=country_data["id"],
        defaults={
            "name": country_data["name"],
            "iso3": country_data["iso3"],
            "iso2": country_data["iso2"],
            "numeric_code": country_data["numeric_code"],
            "phone_code": country_data["phone_code"],
            "capital": country_data["capital"],
            "currency": country_data["currency"],
            "currency_name": country_data["currency_name"],
            "currency_symbol": country_data["currency_symbol"],
            "tld": country_data["tld"],
            "native": country_data["native"],
            "nationality": country_data["nationality"],
            "emoji": country_data["emoji"],
            "emojiU": country_data["emojiU"],
            "region": region,
            "subregion": subregion,
            "location": location,
        }
    )
    print(f"✅ Inserted country: {country_data['name']}")

class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0004_auto_20250501_0409"),  # adjust if your migration name is different
    ]

    operations = [
        migrations.RunPython(load_country),
    ]
