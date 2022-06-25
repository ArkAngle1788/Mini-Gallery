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
class ProfileSignupForm(SignupForm):

    city_options=[]
    for city in City.objects.all():
        city_options.append([city.pk,city.city_name])

#
    # username = forms.CharField(max_length=50,widget=forms.TextInput(basicattrs))
    first_name = forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'First Name Here'})) # Required {'class':'form-control apply_select2'}
    last_name = forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'Last Name Here'})) # Required
    home_city = forms.ChoiceField(choices=city_options,widget=Select2Widget)


    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(ProfileSignupForm, self).save(request)

        # after user is saved we can manipulate it's object in the DB to create a UserProfile for it
        #  self.cleaned_data['home_city'][0] is supery hacky but i don't have a better idea right now
        user.profile.location=City.objects.get(pk=self.cleaned_data['home_city'][0])
        user.profile.save()
        # new_userprofile=UserProfile(user=user,location=City.objects.get(pk=self.cleaned_data['home_city'][0]))
        # new_userprofile.save()


        # You must return the original result.
        return user

class ProfileEditForm(forms.ModelForm):

    first_name = forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'First Name Here','class':'bg-white'})) # Required {'class':'form-control apply_select2'}
    last_name = forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'Last Name Here','class':'bg-white'})) # Required

    class Meta:
        model=UserProfile
        fields=['location']
        widgets = {
            'location' : Select2Widget,
        }

    def save(self):

        # Ensure you call the parent class's save.
        # .save() returns a UserProfile object.

        userprofile = super().save()

        # after user is saved we can manipulate it's object in the DB to create a UserProfile for it
        #  self.cleaned_data['name'][0] is supery hacky but i don't have a better idea right now
        userprofile.user.first_name=self.cleaned_data['first_name']
        userprofile.user.last_name=self.cleaned_data['last_name']
        userprofile.user.save()

        # You must return the original result.
        return userprofile




#
# Providing initial values¶
# As with regular forms, it’s possible to specify initial data for forms by specifying an initial parameter when instantiating the form. Initial values provided this way will override both initial values from the form field and values from an attached model instance. For example:
#
# >>> article = Article.objects.get(pk=1)
# >>> article.headline
# 'My headline'
# >>> form = ArticleForm(initial={'headline': 'Initial headline'}, instance=article)
# >>> form['headline'].value()
# 'Initial headline'
