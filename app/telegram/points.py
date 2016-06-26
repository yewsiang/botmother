from app.knowledgebase import KBManager


class Badges:
    '''
    This class holds the titles and badges of Users with the corresponding points.
    '''
    NOTHING = (0, "Peon")
    FIRST = (1, "Acolyte")
    SECOND = (5, "Apprentice")
    THIRD = (10, "Warrior")
    FOURTH = (25, "Promise")
    FIFTH = (50, "Knight")
    SIXTH = (100, "Hero")


class Points:
    '''
    This class handles all things related to the User's Points.
    1) Allows Users to check their points
    2) Adds points for Users.
    '''
    # /points - When User types /points to retrieve his points & badges
    @classmethod
    def points_command(cls, bot):
        '''
        title, points_to_next_level = Points.get_title(bot)
        text_to_send = "Dear " + title + ",\n"
           "You currently have " + points + " Karma points\n"
        if points_to_next_level is None:
           # The person is a hero
           text_to_send += "Thanks for your contribution to the community!\n"
        else:
           # Tell the person how many points he have to get in order to go to the next level
           if (points_to_next_level == 1):
                text_to_send += "You just need ONE more point to go to the next level!\n"
                "Earn points by contributing questions & answers that are rated to the community :)!\n"
            else:
                text_to_send += "You just need another " + points_to_next_level +
                    " points to advance to the next level!\n"
                    "Earn points by contributing questions & answers that are rated to the community :)!\n"
        '''
        print "hi"

    # According to the User's points, give him a title
    @classmethod
    def get_title(cls, bot):
        '''
        points = KBManager.get_points(bot.telegram_user_id)
        # Points = 0: Peon
        if points == Badges.NOTHING[0]:
            points_to_next_level = Badges.FIRST[0] - points
            return (Badges.NOTHING[1], points_to_next_level)
        # 1 to 4
        elif points < Badges.FIRST[0]:
            points_to_next_level = Badges.SECOND[0] - points
            return (Badges.FIRST[1], points_to_next_level)
        # 5 to 9
        elif points <= Badges.SECOND[0]:
            points_to_next_level = Badges.THIRD[0] - points
            return (Badges.SECOND[1], points_to_next_level)
        # 10 to 24
        elif points <= Badges.THIRD[0]:
            points_to_next_level = Badges.FOURTH[0] - points
            return (Badges.THIRD[1], points_to_next_level)
        # 25 to 49
        elif points <= Badges.FOURTH[0]:
            points_to_next_level = Badges.FIFTH[0] - points
            return (Badges.FOURTH[1], points_to_next_level)
        # 50 to 99
        elif points <= Badges.FIFTH[0]:
            points_to_next_level = Badges.SIXTH[0] - points
            return (Badges.FIFTH[1], points_to_next_level)
        # 100 and above: Hero
        else:
            return (Badges.SIXTH[1], None)
        '''
        print "hi"

    # Award a User with points because of participation
    # Returns a tuple of (True/False of awarding of points, Updated points of user)
    @classmethod
    def award_points(cls, telegram_user_id, points):
        # succeed, updated_points = KBManager.award_points(telegram_user_id, points)
        # return (succeed, updated_points)
        print "hi"
