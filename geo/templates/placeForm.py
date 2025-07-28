from django import forms

from geo.models import Place, State, City

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'address', 'zip_code', 'lat', 'lng']  # Specify the field order

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)

        # Initially set both state and city fields' querysets to none (empty list)
        self.fields['state'].queryset = State.objects.none()
        self.fields['city'].queryset = City.objects.none()

        # If there's data for country, load the relevant states
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, ignore and keep state queryset empty
        elif self.instance.pk:
            # If this is an edit form, prepopulate the state dropdown based on the current country
            self.fields['state'].queryset = self.instance.country.states.order_by('name')

        # If there's data for state, load the relevant cities
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, ignore and keep city queryset empty
        elif self.instance.pk:
            # If this is an edit form, prepopulate the city dropdown based on the current state
            self.fields['city'].queryset = self.instance.state.cities.order_by('name')
