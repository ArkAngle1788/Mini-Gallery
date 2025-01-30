
from .models import PlayerSeasonFaction, Round, Match


def inner_matching(players_remaining, lookup, safety):
    """
    recursive function for determining matchmaking pairs
    returns None an an invalid pair and an array of
    maches on success
    """

    num_left = players_remaining.count()

    if num_left <= 1:
        # print('number of players remaining is less than 1 (inner)')
        # if we hit this something is broken b/c this should be caught at the end of the function
        return None
    player1 = players_remaining.first()
    # print('\n previous opponents are : '+str(player1.previous_opponents.all()))

    # we exclude player 1 and later the lookup to simulate them being matched
    players_remaining_edit = players_remaining.exclude(
        id=player1.id)

    # this removes everybody that player one has already played
    unplayed_players_remaining = players_remaining_edit.exclude(
        previous_opponents=player1)
    # print('options for '+str(player1)+' to play are :'+str(unplayed_players_in_season)+'\n')

    # if this is null then there are no possible matches and we need to try a different lookup
    if not unplayed_players_remaining:
        # print('Unplayed_players_remaining is empty')
        return None

    if lookup >= unplayed_players_remaining.count():
        # print('iterated too much against unplayed players')
        return None

    # pick an opponent for player1 based on lookup and exclude them
    player2 = unplayed_players_remaining[lookup]
    players_remaining_edit = players_remaining_edit.exclude(
        id=player2.id)

    # if count is 0 we're at the deepest level and have found successful
    # matchup pairs to return. Returning something other than None will
    # break us out of the recursion
    if players_remaining_edit.count() == 0 and player1 and player2:

        im_bad_at_arrays = []
        im_bad_at_arrays += [player1]
        im_bad_at_arrays += [player2]
        return im_bad_at_arrays

    # this is set to zero here because each time
    # we go deeper we want to start looking at the start again
    lookup = 0

    output = None
    while not output and safety < 10:
        output = inner_matching(players_remaining_edit, lookup, safety)
        if output:

            output += [player1]
            output += [player2]

            return output

        else:

            if lookup >= num_left:
                # print('bad lookup no matches found?')
                return None

            # increment control variables and loop again
            lookup += 1
            safety += 1
            # print('did not find a match. incrementing lookup. Lookup is : ' +
            #       str(lookup)+' safety is : '+str(safety))

    return None



def auto_round_matches_basic(season):
    """
    This function returns false if successful
    and a string with the error case if unsuccessful

    It will also actually create and save the match entries
    """

    # UserImage.objects.annotate(Count('popularity')).order_by('-popularity__count')

    players_in_season = PlayerSeasonFaction.objects.filter(
        season=season).order_by('internal_score')


    # for player in players_in_season:
    #     print(f'player {player.profile} Score: {player.score} Internal Score: {player.internal_score}')


    players_in_season = players_in_season.exclude(
        profile__user__username='Tie')

    if season.seasons_rounds.all().last().round_number >= (players_in_season.count()-1):
        return "Automatic Matchmaking Does not support this many rounds. Rematches Will Occur."

    if players_in_season.count() % 2 != 0:
        return "Auto Matchmaking Cannot run with an odd number of players"

    players_in_season = players_in_season.exclude(matched=True)
    if not players_in_season:
        return 'unmatched player list is empty'
    matchmaking_list = []

    # print("initial list of players: "+str(players_in_season)+'\n')

    matchmaking_results = inner_matching(players_in_season, 0, 0)
    # print("\n\n\n Final output is :\n")
    # print(matchmaking_results)
    # print()

    if not matchmaking_results:
        return "Something has gone horribly wrong. \
            The safety var to stop infinite loops has been activated. \
                No matches were able to be found. Are there an even number of players?"

    matchmaking_list = matchmaking_results

    round_var = Round.objects.filter(season=season).order_by('-id').first()

    while matchmaking_list:

        player1 = matchmaking_list[0].id
        player2 = matchmaking_list[1].id
        matchmaking_list.pop(0)
        matchmaking_list.pop(0)

        updated_match = Match(round=round_var, player1=PlayerSeasonFaction.objects.get(
            pk=player1), player2=PlayerSeasonFaction.objects.get(pk=player2))

        # print(updated_match)

        updated_match.save()

    # we retun false on successful completion b/c if we fail we return a string
    # and we need to be able to clearly differientiate from that
    return False


def match_permission_check(match,user):
    """
    Makes sure you are part of a season to upload match pictures
    Returns True if user has valid permissions and false otherwise
    """

    try:
        user.profile
    except:
        return False
        

    if user.is_staff:
        return True

    if user.profile in (match.player1.profile,match.player2.profile):
        return True

    group=match.round.season.league.group
    for admin in group.group_primary_admins.all():
        if admin.userprofile == user.profile:
            return True
    for admin in group.group_secondary_admins.all():
        if admin.userprofile == user.profile:
            return True
    return False
