

    # scoring mechanics:

    # infinity: Tournament Points -- Objective Points -- Victory Points (final tiebreaker is total objective points of opponents played)


# Victory 4 Earning more Objective Points than the opponent.
# Tie 2 Earning as many Objective Points as the opponent.
# Defeat 0 Earning fewer Objective Points than the opponent.
# Offensive Bonus +1 Earning 5 or more Objective Points. This Tournament Point is added to the obtained result.
# Defensive Bonus +1 Losing by 2 or less Objective Points. This Tournament Point is added to the obtained result



# Byes:

#  A player who takes a bye is awarded a Victory (worth 4 Tournament Points), 0 Objective Points and 0 Victory Points for that Round. 

# When players take a bye, they must make a note of it in their Tournament Control Sheet. Once the last Tournament Round ends, players who were given a bye follow these steps:
# ◼ Add up all Objective Points the player earned during the tournament.
# ◼ Multiply the result by the number of Tournament Rounds of the tournament.
# ◼ Divide the result by the number of Tournament Rounds played (one less than the total Tournament Rounds of the tournament) and then round up.
# ◼ The end result is their final Objective Points score. In the event of a tie, repeat the process with the player’s Victory Points.






# Custom functions must exist for:

# end of season: apply bye mods (not required by all game types) (if using signals the infinity version would require an end of season check as well so that if you save after the season is over it doesn't break byes)

def calculate_score_infinity(self,player1_score_list,player2_score_list,bye_player):
    """
    calculates the new TP/OP/VP for the match
    edits self and player1_score_list/player2_score_list
    score difference adjustments for psf score not handled here
    """


    # calculate objective points
    p1_objective_points=int(player1_score_list[0])
    p2_objective_points=int(player2_score_list[0])
    p1_tournament_points=0
    p2_tournament_points=0

    if bye_player:
        bye_player=bye_player[0]

    if self.player1==bye_player or self.player2==bye_player:
        if self.player1==bye_player:
            p2_tournament_points=4
        if self.player2==bye_player:
            p1_tournament_points=4
    else:
        if (p1_objective_points-p2_objective_points)>0:
            # earn 4 p1
            p1_tournament_points=4
            if p1_objective_points>=5:
                # earn +1 p1
                p1_tournament_points+=1
            if p1_objective_points-p2_objective_points <=2:
                # earn +1 p2
                p2_tournament_points+=1
        elif (p1_objective_points-p2_objective_points)==0:
            # earn 2 both
            p1_tournament_points=2
            p2_tournament_points=2
            
            if p2_objective_points>=5:
                # earn +1 p2
                p2_tournament_points+=1
            if p1_objective_points>=5:
                # earn +1 p1
                p1_tournament_points+=1
        elif (p1_objective_points-p2_objective_points)<0:
            # earn 4 p2
            p2_tournament_points=4
            if p2_objective_points>=5:
                # earn +1 p2
                p2_tournament_points+=1
            if p2_objective_points-p1_objective_points<=2:
                # earn +1 p1
                p1_tournament_points+=1
    self.player1_score =f'{p1_tournament_points},{int(player1_score_list[0])},{int(player1_score_list[1])}'
    self.player2_score =f'{p2_tournament_points},{int(player2_score_list[0])},{int(player2_score_list[1])}'

        # Victory 4 Earning more Objective Points than the opponent.
        # Tie 2 Earning as many Objective Points as the opponent.
        # Defeat 0 Earning fewer Objective Points than the opponent.
        # Offensive Bonus +1 Earning 5 or more Objective Points. This Tournament Point is added to the obtained result.
        # Defensive Bonus +1 Losing by 2 or less Objective Points. This Tournament Point is added to the obtained result

        #a bye gives 4 TP and OP/VP calculated at the end of the event


def calculate_score_other(self,player1_score_list,player2_score_list,bye_player):
    """
    Default 'Other' score calculation. Expects format to be TP/score
    calculates the new TP/OP for the match
    edits self and player1_score_list/player2_score_list
    score difference adjustments for psf score not handled here
    """


    # calculate objective points
    p1_objective_points=int(player1_score_list[0])
    p2_objective_points=int(player2_score_list[0])
    p1_tournament_points=0
    p2_tournament_points=0


    if bye_player:
        bye_player=bye_player[0]

    if self.player1==bye_player or self.player2==bye_player:
        if self.player1==bye_player:
            p2_tournament_points=4
        if self.player2==bye_player:
            p1_tournament_points=4
    else:
        if (p1_objective_points-p2_objective_points)>0:
            # earn 4 p1
            p1_tournament_points=4
        elif (p1_objective_points-p2_objective_points)==0:
            # earn 2 both
            p1_tournament_points=2
            p2_tournament_points=2
        elif (p1_objective_points-p2_objective_points)<0:
            # earn 4 p2
            p2_tournament_points=4

    self.player1_score =f'{p1_tournament_points},{int(player1_score_list[0])}'
    self.player2_score =f'{p2_tournament_points},{int(player2_score_list[0])}'


