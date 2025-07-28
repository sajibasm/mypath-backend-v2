from django import forms
from geo.models import Country, SubRegion

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country  # Use Country model here
        fields = ['name', 'iso3', 'iso2', 'numeric_code', 'phone_code', 'capital', 'currency', 'currency_name', 'currency_symbol', 'tld', 'native', 'nationality', 'latitude', 'longitude', 'emoji', 'emojiU']  # Correct 'national' to 'nationality'

    def __init__(self, *args, **kwargs):
        super(CountryForm, self).__init__(*args, **kwargs)

        # Initially set subregion queryset to none (empty list)
        self.fields['subregion'].queryset = SubRegion.objects.none()

        # If there's data for region, load the relevant subregions
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['subregion'].queryset = SubRegion.objects.filter(region_id=region_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, keep subregion queryset empty
        elif self.instance.pk:
            # If this is an edit form, prepopulate the subregion dropdown based on the current region
            self.fields['subregion'].queryset = self.instance.region.subregions.order_by('name')
