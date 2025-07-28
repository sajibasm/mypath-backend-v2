from django.db import migrations
from django.contrib.gis.geos import Point

def load_states(apps, schema_editor):
    State = apps.get_model("geo", "State")

    STATES = [
        {"id": "04071b25cb574993b1b217d60311262d", "name": "Maine", "country_code": "US", "state_code": "ME", "type": "", "latitude": 45.253783, "longitude": -69.445469},
        {"id": "0676b86fbb2b4d34b80e0a463c3b1a9b", "name": "Ohio", "country_code": "US", "state_code": "OH", "type": "", "latitude": 40.417287, "longitude": -82.907123},
        {"id": "111a5ae5b0a4412983926a5cbbd03e0e", "name": "Oregon", "country_code": "US", "state_code": "OR", "type": "", "latitude": 43.804133, "longitude": -120.554201},
        {"id": "11bc104e879145a1ab85ab4755fd82b4", "name": "Connecticut", "country_code": "US", "state_code": "CT", "type": "", "latitude": 41.603221, "longitude": -73.087749},
        {"id": "136cff9514024cd98a45182e11095c6a", "name": "New Jersey", "country_code": "US", "state_code": "NJ", "type": "", "latitude": 40.058324, "longitude": -74.405661},
        {"id": "157cf9e141bc4b9c94ff3d7736eaad13", "name": "South Dakota", "country_code": "US", "state_code": "SD", "type": "", "latitude": 43.969515, "longitude": -99.901813},
        {"id": "1a116211175e48ff809388c7243a1f42", "name": "North Dakota", "country_code": "US", "state_code": "ND", "type": "", "latitude": 47.551493, "longitude": -101.002012},
        {"id": "1c0238fe5e8f44e5a8130a11a35c0b46", "name": "Nevada", "country_code": "US", "state_code": "NV", "type": "", "latitude": 38.802610, "longitude": -116.419389},
        {"id": "1d9d5fc9b66143f787dd1d8d899bfbed", "name": "South Carolina", "country_code": "US", "state_code": "SC", "type": "", "latitude": 33.836081, "longitude": -81.163725},
        {"id": "207d988445ae415bb067c12ef063e4c3", "name": "Missouri", "country_code": "US", "state_code": "MO", "type": "", "latitude": 37.964253, "longitude": -91.831833},
        {"id": "220ccfe6221f483aa3f8247c35fba444", "name": "Hawaii", "country_code": "US", "state_code": "HI", "type": "Territory", "latitude": 19.896766, "longitude": -155.582782},
        {"id": "233f1c00af564094b05b7271c01e1b7e", "name": "Alaska", "country_code": "US", "state_code": "AK", "type": "", "latitude": 64.200841, "longitude": -149.493673},
        {"id": "24c80bb2825540628f481e48e8ee7a83", "name": "Rhode Island", "country_code": "US", "state_code": "RI", "type": "", "latitude": 41.580095, "longitude": -71.477429},
        {"id": "2fc2d7c0a54340eba72512d75b75fd8f", "name": "Indiana", "country_code": "US", "state_code": "IN", "type": "", "latitude": 40.267194, "longitude": -86.134902},
        {"id": "31c0e61b53c545a8ad83a9b6e5c5db4b", "name": "Mississippi", "country_code": "US", "state_code": "MS", "type": "", "latitude": 32.354668, "longitude": -89.398528},
        {"id": "40af6169970a43289c8fce2065d4c929", "name": "Tennessee", "country_code": "US", "state_code": "TN", "type": "", "latitude": 35.517491, "longitude": -86.580447},
        {"id": "453456e7e2034aa6b8dc35dba919f3cf", "name": "Michigan", "country_code": "US", "state_code": "MI", "type": "", "latitude": 44.314844, "longitude": -85.602364},
        {"id": "550dc6660f814a638dcdab52a1f21285", "name": "Texas", "country_code": "US", "state_code": "TX", "type": "", "latitude": 31.968599, "longitude": -99.901813},
        {"id": "5831660814224a149b8204f1c7b9b17e", "name": "Pennsylvania", "country_code": "US", "state_code": "PA", "type": "", "latitude": 41.203322, "longitude": -77.194525},
        {"id": "653356156dc14d2a99e809de1ec6e2c4", "name": "North Carolina", "country_code": "US", "state_code": "NC", "type": "", "latitude": 35.759573, "longitude": -79.019300},
        {"id": "7748a620272c46e699fe2c3e6b94e2fa", "name": "New York", "country_code": "US", "state_code": "NY", "type": "", "latitude": 40.712775, "longitude": -74.005973},
        {"id": "7cb3be99361e4d61af8b68f36aad0b24", "name": "Maryland", "country_code": "US", "state_code": "MD", "type": "", "latitude": 39.045755, "longitude": -76.641271},
        {"id": "7eec7a161d33402fab775761135463a1", "name": "Colorado", "country_code": "US", "state_code": "CO", "type": "", "latitude": 39.550051, "longitude": -105.782067},
        {"id": "8e13dab6f4114521a93518f52cf80e17", "name": "Vermont", "country_code": "US", "state_code": "VT", "type": "", "latitude": 44.558803, "longitude": -72.577842},
        {"id": "9050a65e527644fd8a2a1ae0225200e1", "name": "Virginia", "country_code": "US", "state_code": "VA", "type": "", "latitude": 37.431573, "longitude": -78.656894},
        {"id": "9448b18d13eb4ae1b9d2c8777ee4726b", "name": "Arizona", "country_code": "US", "state_code": "AZ", "type": "", "latitude": 34.048928, "longitude": -111.093731},
        {"id": "9a4ec641bd444e93a6d007a11eade84a", "name": "New Hampshire", "country_code": "US", "state_code": "NH", "type": "", "latitude": 43.193852, "longitude": -71.572395},
        {"id": "9a8428c39f4c4891bef4fb6708e13c4f", "name": "Nebraska", "country_code": "US", "state_code": "NE", "type": "", "latitude": 41.492537, "longitude": -99.901813},
        {"id": "9de79fac54454f17a983a93fd2a7fd99", "name": "West Virginia", "country_code": "US", "state_code": "WV", "type": "", "latitude": 38.597626, "longitude": -80.454903},
        {"id": "9e81f4ac89e745c1923cbb40fa058bb2", "name": "Wisconsin", "country_code": "US", "state_code": "WI", "type": "", "latitude": 43.784440, "longitude": -88.787868},
        {"id": "a0d9a8ee198740cab66d5245a1377e12", "name": "Guam", "country_code": "US", "state_code": "GU", "type": "Territory", "latitude": 13.444304, "longitude": 144.793731},
        {"id": "a19df3a2e8d9412890dc926c341cfd82", "name": "New Mexico", "country_code": "US", "state_code": "NM", "type": "", "latitude": 34.519940, "longitude": -105.870090},
        {"id": "a5f520e945764033817fa028c419ed1b", "name": "Louisiana", "country_code": "US", "state_code": "LA", "type": "", "latitude": 30.984298, "longitude": -91.962333},
        {"id": "a6a840543c8a4ffb9058cf416c253c1e", "name": "Florida", "country_code": "US", "state_code": "FL", "type": "", "latitude": 27.664827, "longitude": -81.515754},
        {"id": "b0b0ea040a034b25887cb0ab7146c5ab", "name": "Minnesota", "country_code": "US", "state_code": "MN", "type": "", "latitude": 46.729553, "longitude": -94.685900},
        {"id": "b4e408aaf7ff4176a5ad531007ac5ea1", "name": "Oklahoma", "country_code": "US", "state_code": "OK", "type": "", "latitude": 35.467560, "longitude": -97.516428},
        {"id": "bf48ab5d0dac4924ac5409613f4b3ef3", "name": "Kansas", "country_code": "US", "state_code": "KS", "type": "", "latitude": 39.011902, "longitude": -98.484247},
        {"id": "c15a811214424011a701825e9bb67eca", "name": "Idaho", "country_code": "US", "state_code": "ID", "type": "", "latitude": 44.068202, "longitude": -114.742041},
        {"id": "c69988b474194e6cbe70fadbdef80063", "name": "Wyoming", "country_code": "US", "state_code": "WY", "type": "", "latitude": 43.075968, "longitude": -107.290284},
        {"id": "ca0ccba4b9f3408a83b741f2689267f5", "name": "Georgia", "country_code": "US", "state_code": "GA", "type": "", "latitude": 32.165622, "longitude": -82.900075},
        {"id": "cc52c9f588ee466a9b3e27d095eda680", "name": "Kentucky", "country_code": "US", "state_code": "KY", "type": "", "latitude": 37.839333, "longitude": -84.270018},
        {"id": "cfb2a237c5364f669048c2a7a4b1149d", "name": "Utah", "country_code": "US", "state_code": "UT", "type": "", "latitude": 39.320980, "longitude": -111.093731},
        {"id": "d069abcde8b843fa881782bdcac1c92e", "name": "Arkansas", "country_code": "US", "state_code": "AR", "type": "", "latitude": 35.201050, "longitude": -91.831833},
        {"id": "d1e5ffde6a454e198049030c57a547b1", "name": "Illinois", "country_code": "US", "state_code": "IL", "type": "", "latitude": 40.633125, "longitude": -89.398528},
        {"id": "da602830ab7f40be818b55090fa37382", "name": "Delaware", "country_code": "US", "state_code": "DE", "type": "", "latitude": 38.910833, "longitude": -75.527670},
        {"id": "daec5889afdf4ac5b0a4dec38d6ae1b1", "name": "Iowa", "country_code": "US", "state_code": "IA", "type": "", "latitude": 41.878003, "longitude": -93.097702},
        {"id": "db74ffbe725945248fff64767265c13e", "name": "Alabama", "country_code": "US", "state_code": "AL", "type": "", "latitude": 32.318231, "longitude": -86.902298},
        {"id": "ec69102cda1c4289bc5ee271017afd18", "name": "Washington", "country_code": "US", "state_code": "WA", "type": "", "latitude": 47.751074, "longitude": -120.740139},
        {"id": "ed38812bb901404a93319ec1cac6fa4b", "name": "Puerto Rico", "country_code": "US", "state_code": "PR", "type": "Territory", "latitude": 18.220833, "longitude": -66.590149},
        {"id": "f19f08d6f9dc4063b431c04b3073f877", "name": "Massachusetts", "country_code": "US", "state_code": "MA", "type": "", "latitude": 42.407211, "longitude": -71.382437},
        {"id": "fb5b62530f004184b20bc70a2d62bb4f", "name": "Montana", "country_code": "US", "state_code": "MT", "type": "", "latitude": 46.879682, "longitude": -110.362566},
        {"id": "fdac6067557845e7b872cfe9f5b14d46", "name": "California", "country_code": "US", "state_code": "CA", "type": "", "latitude": 36.778261, "longitude": -119.417932},
    ]

    inserted = 0
    for state in STATES:
        location = None
        try:
            location = Point(state['longitude'], state['latitude'])
        except (ValueError, TypeError):
            pass

        State.objects.update_or_create(
            id=state['id'],
            defaults={
                'name': state['name'],
                'country_code': state['country_code'],
                'state_code': state['state_code'],
                'type': state['type'],
                'location': location
            }
        )
        print(f"✅ Inserted state: {state['name']}")
        inserted += 1

    print(f"✅ Total states inserted: {inserted}")

class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0005_auto_20250501_0411"),
    ]

    operations = [
        migrations.RunPython(load_states),
    ]