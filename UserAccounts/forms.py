from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from CommunityInfrastructure.models import City
from UserAccounts.models import UserProfile
from django_select2.forms import Select2Widget

# Inherit Django's default UserCreationForm
# class UserRegisterForm(UserCreationForm):
#     first_name = forms.CharField(max_length=50,help_text="help text test") # Required
#     last_name = forms.CharField(max_length=50) # Required
#     # All fields you re-define here will become required fields in the form
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']



from allauth.account.forms import SignupForm
class MyCustomSignupForm(SignupForm):

    city_options=[]
    for city in City.objects.all():
        city_options.append([city.pk,city.city_name])


    first_name = forms.CharField(max_length=50,help_text="help text test",widget=forms.TextInput({'placeholder':'Name Here'})) # Required {'class':'form-control apply_select2'}
    last_name = forms.CharField(max_length=50) # Required
    home_city = forms.ChoiceField(choices=city_options,widget=Select2Widget)

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # after user is saved we can manipulate it's object in the DB to create a UserProfile for it
        #  self.cleaned_data['home_city'][0] is supery hacky but i don't have a better idea right now
        user.profile.location=City.objects.get(pk=self.cleaned_data['home_city'][0])
        user.profile.save()
        # new_userprofile=UserProfile(user=user,location=City.objects.get(pk=self.cleaned_data['home_city'][0]))
        # new_userprofile.save()


        # You must return the original result.
        return user
