from django.db import migrations

def insert_wheelchair_metadata(apps, schema_editor):
    WheelchairType = apps.get_model('wheelchair', 'WheelchairType')
    WheelchairDriveType = apps.get_model('wheelchair', 'WheelchairDriveType')
    WheelchairTireMaterial = apps.get_model('wheelchair', 'WheelchairTireMaterial')

    # --- WheelchairType Data ---
    wheelchair_types = [
        'Manual Wheelchair',
        'Powered Wheelchair',
        'Power Assist Wheelchair',
        'Other Wheelchair',
    ]
    for name in wheelchair_types:
        WheelchairType.objects.update_or_create(
            name=name,
            defaults={'status': 'active'}
        )

    # --- WheelchairDriveType Data ---
    drive_types = [
        'Front Wheel Drive',
        'Mid Wheel Drive',
        'Rear Wheel Drive',
    ]
    for name in drive_types:
        WheelchairDriveType.objects.update_or_create(
            name=name,
            defaults={'status': 'active'}
        )

    # --- WheelchairTireMaterial Data ---
    tire_materials = [
        'Pneumatic',
        'Solid',
        'Flat Free',
        'Other'
    ]
    for name in tire_materials:
        WheelchairTireMaterial.objects.update_or_create(
            name=name,
            defaults={'status': 'active'}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('wheelchair', '0001_initial'),  # Adjust if needed
    ]

    operations = [
        migrations.RunPython(insert_wheelchair_metadata),
    ]
