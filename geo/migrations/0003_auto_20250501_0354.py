from django.db import migrations

# Subregion data defined directly in the script
SUBREGIONS = [
    {"id": "1056a216587845a39e6607a6c9360bda", "name": "Middle Africa", "wikiDataId": "Q27433", "region_id": "f213b5ded0bd44c9b53128a9e93859fd"},
    {"id": "28ae0ef6408c483695f2c5f4377370cc", "name": "Western Africa", "wikiDataId": "Q4412", "region_id": "f213b5ded0bd44c9b53128a9e93859fd"},
    {"id": "2f1003861e274cfca339ae1372701640", "name": "South-Eastern Asia", "wikiDataId": "Q11708", "region_id": "e4f24e31e0f64769b0b60449e34c479b"},
    {"id": "2f29da1699b24b08ad6ac2c3f1a5f6c5", "name": "Polynesia", "wikiDataId": "Q35942", "region_id": "fbf1f6c7b92a4706998ba030a7e38db5"},
    {"id": "42b64e331e0749bcb7c0bfc957609f95", "name": "Eastern Africa", "wikiDataId": "Q27407", "region_id": "f213b5ded0bd44c9b53128a9e93859fd"},
    {"id": "476e1e6f71814264855c042c7d78f760", "name": "Northern America", "wikiDataId": "Q2017699", "region_id": "3084d8293c4f492aaff2df05768d263a"},
    {"id": "4912d56630c14c96a2d1e16d50b9833d", "name": "Central Asia", "wikiDataId": "Q27275", "region_id": "e4f24e31e0f64769b0b60449e34c479b"},
    {"id": "512b0a672179409683f16d8dc82115cc", "name": "Southern Europe", "wikiDataId": "Q27449", "region_id": "6e4977a9287e4fc69ee409e35d468809"},
    {"id": "585767af492648ea8d540017b5ad6fa3", "name": "South America", "wikiDataId": "Q18", "region_id": "3084d8293c4f492aaff2df05768d263a"},
    {"id": "63abdd491c26483984487e0aafe85fa4", "name": "Melanesia", "wikiDataId": "Q37394", "region_id": "fbf1f6c7b92a4706998ba030a7e38db5"},
    {"id": "64ba3a946e794aa6ac72b4fb444ede61", "name": "Southern Asia", "wikiDataId": "Q771405", "region_id": "e4f24e31e0f64769b0b60449e34c479b"},
    {"id": "6984ff545fc6498e82522e28ce8f24d9", "name": "Micronesia", "wikiDataId": "Q3359409", "region_id": "fbf1f6c7b92a4706998ba030a7e38db5"},
    {"id": "7f71ae82a921458abf5e48a765c08175", "name": "Southern Africa", "wikiDataId": "Q27394", "region_id": "f213b5ded0bd44c9b53128a9e93859fd"},
    {"id": "94d585fc38c64ce79e4b40d0ff7ee36b", "name": "Eastern Asia", "wikiDataId": "Q27231", "region_id": "e4f24e31e0f64769b0b60449e34c479b"},
    {"id": "a95da5e10828449e8055a14d8ee3f68f", "name": "Western Europe", "wikiDataId": "Q27496", "region_id": "6e4977a9287e4fc69ee409e35d468809"},
    {"id": "adbc23c3e33b4783bc20970e5fabc66f", "name": "Central America", "wikiDataId": "Q27611", "region_id": "3084d8293c4f492aaff2df05768d263a"},
    {"id": "c13cc3b2145a4918a520f165393595c7", "name": "Australia and New Zealand", "wikiDataId": "Q45256", "region_id": "fbf1f6c7b92a4706998ba030a7e38db5"},
    {"id": "cf70e8f95b00484cac65c784c905681e", "name": "Caribbean", "wikiDataId": "Q664609", "region_id": "3084d8293c4f492aaff2df05768d263a"},
    {"id": "d2dc8d24e490455dbbfb2f85b8c63819", "name": "Northern Africa", "wikiDataId": "Q27381", "region_id": "f213b5ded0bd44c9b53128a9e93859fd"},
    {"id": "e491d17338994adcaacc331e702af3d4", "name": "Eastern Europe", "wikiDataId": "Q27468", "region_id": "6e4977a9287e4fc69ee409e35d468809"},
    {"id": "ee0f59722d894a8fac2b95cf0bd0721d", "name": "Western Asia", "wikiDataId": "Q27293", "region_id": "e4f24e31e0f64769b0b60449e34c479b"},
    {"id": "ef4ab1dad81a455b83b18231309e41c4", "name": "Northern Europe", "wikiDataId": "Q27479", "region_id": "6e4977a9287e4fc69ee409e35d468809"},
]

def load_subregions(apps, schema_editor):
    SubRegion = apps.get_model("geo", "SubRegion")
    Region = apps.get_model("geo", "Region")

    inserted = 0
    for subregion in SUBREGIONS:
        try:
            region = Region.objects.get(id=subregion['region_id'])
        except Region.DoesNotExist:
            print(f"❌ Region not found for subregion: {subregion['name']} (region_id: {subregion['region_id']})")
            continue

        SubRegion.objects.update_or_create(
            id=subregion['id'],
            defaults={
                'name': subregion['name'],
                'wikiDataId': subregion['wikiDataId'],
                'region': region
            }
        )
        print(f"✅ Inserted/Updated subregion: {subregion['name']}")
        inserted += 1

    print(f"✅ Total subregions inserted or updated: {inserted}")

class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0002_auto_20250501_0353"),  # Adjust to match your actual previous migration
    ]

    operations = [
        migrations.RunPython(load_subregions),
    ]
