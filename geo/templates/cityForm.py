from django import forms
from geo.models import City

class CityAdminForm(forms.ModelForm):
    country_code = forms.CharField(label='Country Code', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    state_code = forms.CharField(label='State code', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = City
        fields = "__all__"
        # fields = ['name', 'country', 'country_code', 'state', 'state_code', 'latitude', 'longitude', 'wikiDataId']

    # def __init__(self, *args, **kwargs):
    #     super(CityAdminForm, self).__init__(*args, **kwargs)
    #     # Prepopulate country_code and state_code based on selected country and state
    #     if self.instance and self.instance.pk:
    #         if self.instance.country:
    #             self.fields['country_code'].initial = self.instance.country.iso2  # Assuming iso2 is the country code
    #         if self.instance.state:
    #             self.fields['state_code'].initial = self.instance.state.state_code  # Assuming state_code is a field in the State model
    #
