
class CallbackQueries:
    # This class handles the callback functions
    @classmethod
    def question_answered(cls, bot, query_id):
        print "Question received by callback function!"
        print "This is query_id: " + query_id
        bot.sender.sendMessage("Question received by callback function!")
