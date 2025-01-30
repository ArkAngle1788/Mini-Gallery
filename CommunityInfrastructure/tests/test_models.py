from django.core.exceptions import ValidationError
from django.test import TestCase

from CommunityInfrastructure.models import Country,Region,City,Group, validate_int_list


class CommunityInfrastructureTests(TestCase):
    """testing the entire model in here because it's structure is simple"""

    @classmethod
    def setUpTestData(cls):

        cls.country_1=Country(country_name="countryname")
        cls.country_1.save()
        cls.region_1=Region(region_name="regionname",country=cls.country_1)
        cls.region_1.save()
        cls.city_1=City(city_name="cityname",region=cls.region_1)
        cls.city_1.save()


        cls.city_group_1=Group(group_name="citygroup1",
                                group_tag="group tags ABC",
                                group_description="description1",
                                group_image_str="1,2,3",
                                location_city=cls.city_1)
        cls.city_group_1.save()
        cls.region_group_1=Group(group_name="regiongroup1",
                                  group_tag="group tags DEF",
                                  group_description="description2",
                                  group_image_str="13,25,388",
                                  location_region=cls.region_1)
        cls.region_group_1.save()
        cls.country_group_1=Group(group_name="countrygroup1",
                                   group_tag="group tags GHI",
                                   group_description="description3",
                                   group_image_str="341,222,113",
                                   location_country=cls.country_1)
        cls.country_group_1.save()
        cls.null_group_1=Group(group_name="nullgroup1",
                                   group_tag="group tags 342",
                                   group_description="description4")
        cls.null_group_1.save()



    def test_validate_int_list(self):
        """database validator functionality check"""

        self.assertIsNone(validate_int_list("2,3,4,5,64"))
        with self.assertRaises(ValidationError):
            validate_int_list("2,3,hello,5,64")
        with self.assertRaises(ValidationError):
            validate_int_list("2,3,,5,64")



    def test_group(self):
        """tests that get_absolute_url works"""

        self.assertEqual(self.city_group_1.get_absolute_url(),
                         "/organizations/cityname/citygroup1/1")
        self.assertEqual(self.region_group_1.get_absolute_url(),
                         "/organizations/regionname/regiongroup1/2")
        self.assertEqual(self.country_group_1.get_absolute_url(),
                         "/organizations/countryname/countrygroup1/3")
        self.assertEqual(self.null_group_1.get_absolute_url(),"/")

