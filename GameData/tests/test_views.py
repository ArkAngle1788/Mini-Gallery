from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from UserAccounts.models import UserProfile



class TestAuthentication(TestCase):
    def test_add_unit_accessible_for_authenticated_users(self):
        get_user_model().objects.create_user(username='testuser',password='password123')

        response=self.client.get(reverse('add unit type'))
        self.assertRedirects(response, expected_url=f"{reverse('account_login')}?next={reverse('add unit type')}")


        # log user in
        self.client.login(username='testuser',password='password123')
        response=self.client.get(reverse('add unit type'))
        self.assertEqual(response.status_code,403)



class TestPage(TestCase):
    
    def test_page_status_code(self):
        response=self.client.get(reverse('add unit type'))
        self.assertEqual(response.status_code,302)

    def test_page_uses_correct_template(self):
        response=self.client.get(reverse('add unit type'))
        # print(response)
        # self.assertTemplateUsed(response,'game_data_form.html')