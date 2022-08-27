from allauth.account.forms import SignupForm
from django import forms
from django_select2.forms import Select2Widget

from CommunityInfrastructure.models import City
from UserAccounts.models import UserProfile


class ProfileSignupForm(SignupForm):
    """adds city field to signup info"""
    city_options = []
    for city in City.objects.all():
        city_options.append([city.pk, city.city_name])
    first_name = forms.CharField(max_length=50, widget=forms.TextInput({
                                 'placeholder': 'First Name Here'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput({
                                'placeholder': 'Last Name Here'}))
    home_city = forms.ChoiceField(choices=city_options, widget=Select2Widget)

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(ProfileSignupForm, self).save(request)

        # after user is saved we can manipulate it's object in the DB to create a UserProfile for it
        #  self.cleaned_data['home_city'][0]
        #  is supery hacky but i don't have a better idea right now
        user.profile.location = City.objects.get(
            pk=self.cleaned_data['home_city'][0])
        user.profile.save()

        # You must return the original result.
        return user


class ProfileEditForm(forms.ModelForm):
    """allows a user to update their profile info"""
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(
        {'placeholder': 'First Name Here', 'class': 'bg-white'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(
        {'placeholder': 'Last Name Here', 'class': 'bg-white'}))

    class Meta:
        model = UserProfile
        fields = ['location']
        widgets = {
            'location': Select2Widget,
        }

    def save(self):
        # Ensure you call the parent class's save.
        # .save() returns a UserProfile object.
        userprofile = super().save()

        # after user is saved we can manipulate it's object in the DB to create a UserProfile for it
        #  self.cleaned_data['name'][0] is supery hacky but i don't have a better idea right now
        userprofile.user.first_name = self.cleaned_data['first_name']
        userprofile.user.last_name = self.cleaned_data['last_name']
        userprofile.user.save()

        # You must return the original result.
        return userprofile
