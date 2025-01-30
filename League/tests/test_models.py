from django.test import TestCase
from django.contrib.auth import get_user_model

from League.models import League, Match, PlayerSeasonFaction, Round, Season
from UserAccounts.models import AdminProfile, UserProfile
from CommunityInfrastructure.models import Group
from GameData.models import Game,Faction,FactionType,SubFaction
from django.urls import reverse
from django.test import Client
from CommunityInfrastructure.models import City,Region,Country
from django.contrib.auth.models import Group as PermGroup

class ScoreUpdateInfinityTests(TestCase):
    """test the signal that handles updating"""
    @classmethod
    def setUpTestData(cls):

        cls.country_1=Country(country_name="Canada")
        cls.country_1.save()
        cls.region_1=Region(region_name="Alberta",country=cls.country_1)
        cls.region_1.save()
        cls.city_1=City(city_name="Edmonton",region=cls.region_1)
        cls.city_1.save()

        cls.game_infinity=Game(game_system_name="Infinity")
        cls.game_infinity.save()

        cls.faction_type_1=FactionType(system=cls.game_infinity,faction_name="Human Sphere")
        cls.faction_type_1.save()
        cls.faction_1=Faction(faction_type=cls.faction_type_1,faction_name="Aleph")
        cls.faction_1.save()
        cls.faction_2=Faction(faction_type=cls.faction_type_1,faction_name="Haqqislam")
        cls.faction_2.save()
        cls.subfaction_1=SubFaction(faction=cls.faction_1,faction_name="Steel Phalanx")
        cls.subfaction_1.save()
        cls.subfaction_2=SubFaction(faction=cls.faction_1,faction_name="O.S.S.")
        cls.subfaction_2.save()


        adminuser=get_user_model().objects.create_user(username='adminuser',password='password123')
        adminuser.is_superuser=True
        adminuser.is_staff=True
        adminuser.save()

        setup_client=Client()
        setup_client.login(username='adminuser',password='password123')

        group_form_data = {
            'group_name':'Infinity Canada',
            'group_tag':'group tag',
            'group_description':'description',
            'location_country':cls.country_1.pk
        }

 
        res=setup_client.post(reverse('create group'),data=group_form_data)
        # print(res.content)

        PermGroup(name='Primary Group Admin').save()
        
        # print(PermGroup.objects.all())
        # print(Group.objects.all())

        group_add_admin_form_data = {
            'select admins primary':adminuser.pk
        }

        url=reverse('group add admin',args=['region', Group.objects.get(group_name='Infinity Canada').slug(), Group.objects.get(group_name='Infinity Canada').id])
        # print(url)
        res=setup_client.post(url,data=group_add_admin_form_data)
        # print(res)
        # print(adminuser.profile.linked_admin_profile.groups_managed_primary.all())
        league_form_data = {
            'league_name':'Colder than Carbonite',
            'admin_options':[adminuser.profile.linked_admin_profile.pk],
            'league_description':'description',
            'location_city':cls.city_1.pk,
            'system':cls.game_infinity.pk
        }
        url=reverse('create league',args=[Group.objects.get(group_name='Infinity Canada').id])
        res=setup_client.post(url,data=league_form_data)
        # print(res.content)
        # print(League.objects.all())

        season_form_data = {
            'season_name':'2025',
            'registration_active':True,
            'allow_repeat_matches':False,
            'registration_key':'passkey'
        }
        url=reverse('create season',args=[League.objects.get(league_name='Colder than Carbonite').pk])
        res=setup_client.post(url,data=season_form_data)
        # print(res)
        

        get_user_model().objects.create_user(username='Tie',password='password123')

        player1=get_user_model().objects.create_user(username='player1',password='password123')
        player2=get_user_model().objects.create_user(username='player2',password='password123')
        player3=get_user_model().objects.create_user(username='player3',password='password123')
        player4=get_user_model().objects.create_user(username='player4',password='password123')
        player5=get_user_model().objects.create_user(username='player5',password='password123')
        player6=get_user_model().objects.create_user(username='player6',password='password123')

# create a PSF for everyone
# profile,faction,sub_faction,season,army_list,previous_opponents,score,wlrecord,matched
        season=Season.objects.get(season_name='2025')
        cls.psf1=PlayerSeasonFaction(profile=player1.profile,faction=cls.faction_1,season=season)
        cls.psf2=PlayerSeasonFaction(profile=player2.profile,faction=cls.faction_2,season=season)
        cls.psf3=PlayerSeasonFaction(profile=player3.profile,faction=cls.faction_1,sub_faction=cls.subfaction_1,season=season)
        cls.psf4=PlayerSeasonFaction(profile=player4.profile,faction=cls.faction_1,sub_faction=cls.subfaction_2,season=season)
        cls.psf5=PlayerSeasonFaction(profile=player5.profile,faction=cls.faction_2,season=season)
        cls.psf6=PlayerSeasonFaction(profile=player6.profile,faction=cls.faction_2,season=season)
        cls.psf1.save()
        cls.psf2.save()
        cls.psf3.save()
        cls.psf4.save()
        cls.psf5.save()
        cls.psf6.save()
     
        # print(PlayerSeasonFaction.objects.all())

        season.registration_active=False
        season.save()


        round_form_data = {
            'round_details':'mission for the round',
            'automate_matchmaking':True,
        }

        url=reverse('create round',args=[season.pk])
        res=setup_client.post(url,data=round_form_data)

        # print(res)
        # print(Match.objects.all())



    def test_submit_score(self):
        """aka match save method"""
        self.client.login(username='adminuser',password='password123')


        i=0
        matches=Match.objects.all()
        for match in matches:
            match_form_data = {
                'winner':match.player1.pk,
                'player1_score':f'{6+i},{78+i}',
                'player2_score':f'{2+i},{55+i}',
                }
            
            url=reverse('edit match',args=[match.pk])
            self.client.post(url,data=match_form_data)
            match_updated=Match.objects.get(pk=match.pk)
            # print(matches)
            self.assertEqual(match_updated.player1_score,f'5,{6+i},{78+i}')
            self.assertEqual(match_updated.player2_score,f'0,{2+i},{55+i}')
            self.assertEqual(match_updated.player1.wlrecord,'-W-')
            self.assertEqual(match_updated.player2.wlrecord,'-L-')
            i+=2
            
        # match=Match.objects.get(round__season__season_name="2025",round__round_number=1,winner=self.psf1)
        # print(f'sdfsdf\n{match.player1}\nmatch score: {match.player1_score}\n')
        #auto matchmaking builds the brackets backwards so we're testing the psf5 match b/c i is 0 in that loop
        match=Match.objects.get(round__season__season_name="2025",round__round_number=1,winner=self.psf5)
        url=reverse('edit match',args=[match.pk])
        self.client.post(url,data={
                                'winner':match.player1.pk,
                                'player1_score':'4,78',
                                'player2_score':'2,55',
                            })
        
        # since player1 is no longer winning by more than 5 and the point diff is 2 or less each players tournament points should have changed
        self.assertEqual(Match.objects.get(round__season__season_name="2025",round__round_number=1,winner=self.psf5).player1_score,'4,4,78')
        self.assertEqual(Match.objects.get(round__season__season_name="2025",round__round_number=1,winner=self.psf5).player2_score,'1,2,55')



        round_form_data = {
            'round_details':'mission for the round',
            'automate_matchmaking':True,
        }

        url=reverse('create round',args=[Season.objects.get(season_name='2025').pk])
        self.client.post(url,data=round_form_data)

        round_2_matches=Match.objects.filter(round__season__season_name="2025",round__round_number=2).order_by('id')
        
        url=reverse('edit match',args=[round_2_matches[0].pk])
        self.client.post(url,data={
                                'winner':round_2_matches[0].player1.pk,
                                'player1_score':'4,78',
                                'player2_score':'0,55',
                            })
        url=reverse('edit match',args=[round_2_matches[1].pk])
        res=self.client.post(url,data={
                                'winner':PlayerSeasonFaction.objects.get(season__season_name='2025',profile__user__username='Tie').pk,
                                'player1_score':'5,78',
                                'player2_score':'5,55',
                            })
        # print(res.content)
        url=reverse('edit match',args=[round_2_matches[2].pk])
        self.client.post(url,data={
                                'winner':round_2_matches[2].player2.pk,
                                'player1_score':'3,78',
                                'player2_score':'6,55',
                            })
        
        self.assertEqual(Match.objects.get(pk=round_2_matches[0].pk).player1_score,'4,4,78')
        self.assertEqual(Match.objects.get(pk=round_2_matches[0].pk).player2_score,'0,0,55')


        self.assertEqual(Match.objects.get(pk=round_2_matches[1].pk).player1_score,'3,5,78')
        self.assertEqual(Match.objects.get(pk=round_2_matches[1].pk).player2_score,'3,5,55')
        
        self.assertEqual(Match.objects.get(pk=round_2_matches[2].pk).player1_score,'0,3,78')
        self.assertEqual(Match.objects.get(pk=round_2_matches[2].pk).player2_score,'5,6,55')

        print(Match.objects.filter(round__season__season_name="2025",round__round_number=1))
        print(Match.objects.filter(round__season__season_name="2025",round__round_number=2))

        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf1.pk).score,'5,10,137')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf1.pk).wlrecord,'-W-L-')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf2.pk).wlrecord,'-L-W-')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf3.pk).wlrecord,'-W-W-')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf4.pk).wlrecord,'-L-L-')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf5.pk).wlrecord,'-W-T-')
        self.assertEqual(PlayerSeasonFaction.objects.get(pk=self.psf6.pk).wlrecord,'-L-T-')


        standings=PlayerSeasonFaction.objects.filter(season__season_name="2025").order_by("-internal_score")
        
        for player in standings:
            print(f'{player} Score: {player.score} Internal Score: {player.internal_score}')


    # def test_checkdb(self):
    #     matches=Match.objects.all()
    #     for match in matches:
    #         print(match.winner)

        

