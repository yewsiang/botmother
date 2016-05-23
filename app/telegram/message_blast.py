
class MessageBlast:
    '''
    The MessageBlast class regulates situations when we have to send
    messages from one to many
    Possible Reasons:
    1) User asks question => question to be sent to those subscribed
    2) Question has been answered => answers to be sent to be voted
    3) Voting results are out + Asker's vote is out => Results to be
    sent to those who participated along with forum link
    '''
    @classmethod
    def message_blast(cls):
        print "Sup"
