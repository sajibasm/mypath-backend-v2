from django.db import migrations

# Timezone data defined directly in the script
TIMEZONES = [
    {"id": "01a21bf4514c47d2a25eb8cb95bb6c15", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Petersburg", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "0920de0ee39e48dca9e295481b94f659", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/North_Dakota/New_Salem", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "0bb6a9c7407348aab0b3a1a41b52d8e2", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Winamac", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "1320c00739a44202a0cec157341b4a03", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/North_Dakota/Beulah", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "1f070e8a7c4f4de7ba4c377a585ad2f5", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Detroit", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "36ae286c94f748dbb1c7d01dacad6cff", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Metlakatla", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "3fd0c6d7ddc34cfabd769dac66485bf5", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/Indiana/Tell_City", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "54d02b54f66949d7beabd99df921bfb4", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Anchorage", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "5989ad9d64d44d1b99a4b8c91d049687", "country_code": "US", "tz_name": "Mountain Standard Time (North America)", "zone_name": "America/Boise", "gmt_offset": -25200, "abbreviation": "MST", "gmt_offset_name": "UTC-07:00"},
    {"id": "609aef1d89634246a02922eac7ecae3b", "country_code": "US", "tz_name": "Hawaii–Aleutian Standard Time", "zone_name": "Pacific/Honolulu", "gmt_offset": -36000, "abbreviation": "HST", "gmt_offset_name": "UTC-10:00"},
    {"id": "6a0319c1a38b47808876407dcb0d493e", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Kentucky/Monticello", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "6adfe1ff99c94c6caccb9827024e7c0c", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Vincennes", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "6c2a7ff7e9db4b84af1a4595cbf52264", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Sitka", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "7f885127dcbc4c4db0ae309b4a9e3982", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Juneau", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "8d546216029d4079aacb61db037e00a5", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/New_York", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "906342c679cf45b2a8dda2d0b46f1868", "country_code": "US", "tz_name": "Mountain Standard Time (North America)", "zone_name": "America/Denver", "gmt_offset": -25200, "abbreviation": "MST", "gmt_offset_name": "UTC-07:00"},
    {"id": "98b8cf31bf394730ba1cbc96ddc58892", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Nome", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "afa0a841ec16465794bcb21718462c21", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Marengo", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "bf55733731fd40d4b0b691b7e7a04f17", "country_code": "US", "tz_name": "Pacific Standard Time (North America)", "zone_name": "America/Los_Angeles", "gmt_offset": -28800, "abbreviation": "PST", "gmt_offset_name": "UTC-08:00"},
    {"id": "d8f412becc0e4e9b9264800e23937060", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/Chicago", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "e2efbf58ab0548539d1005b62589d060", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Indianapolis", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "e772556139264e7893ce192a58421819", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Indiana/Vevay", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "f192ed8f5a294d03bbe0c0fdb20ae6d5", "country_code": "US", "tz_name": "Mountain Standard Time (North America)", "zone_name": "America/Phoenix", "gmt_offset": -25200, "abbreviation": "MST", "gmt_offset_name": "UTC-07:00"},
    {"id": "f1df73ba8f4b44f7874c2cf9fccaf966", "country_code": "US", "tz_name": "Eastern Standard Time (North America)", "zone_name": "America/Kentucky/Louisville", "gmt_offset": -18000, "abbreviation": "EST", "gmt_offset_name": "UTC-05:00"},
    {"id": "f40045167fb6425d9ffbfb8bf5f1ef75", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/Indiana/Knox", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "f40c48cefcb34cd6b3d04b04050584d8", "country_code": "US", "tz_name": "Hawaii–Aleutian Standard Time", "zone_name": "America/Adak", "gmt_offset": -36000, "abbreviation": "HST", "gmt_offset_name": "UTC-10:00"},
    {"id": "f6b77ef3699a4253b76163fbd68918be", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/North_Dakota/Center", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
    {"id": "f7e5b176a9e042c89c5c3a7f9d44fd9d", "country_code": "US", "tz_name": "Alaska Standard Time", "zone_name": "America/Yakutat", "gmt_offset": -32400, "abbreviation": "AKST", "gmt_offset_name": "UTC-09:00"},
    {"id": "fcf951ef05ad4c5ca7f5cf50465e9ca2", "country_code": "US", "tz_name": "Central Standard Time (North America)", "zone_name": "America/Menominee", "gmt_offset": -21600, "abbreviation": "CST", "gmt_offset_name": "UTC-06:00"},
]

def load_timezones(apps, schema_editor):
    Timezone = apps.get_model("geo", "Timezone")
    inserted = 0
    for row in TIMEZONES:
        Timezone.objects.update_or_create(
            id=row["id"],
            defaults={
                "country_code": row["country_code"],
                "tz_name": row["tz_name"],
                "zone_name": row["zone_name"],
                "gmt_offset": row["gmt_offset"],
                "abbreviation": row["abbreviation"],
                "gmt_offset_name": row["gmt_offset_name"]
            }
        )
        print(f"✅ Inserted timezone: {row['zone_name']}")
        inserted += 1

    print(f"✅ Total timezones inserted: {inserted}")

class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0003_auto_20250501_0354"),
    ]

    operations = [
        migrations.RunPython(load_timezones),
    ]
