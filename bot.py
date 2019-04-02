import jieba

class LineBot():

    def __init__(self, interested_topic, topic_detail=None):
        self.topic = interested_topic
        self.topic_detail = topic_detail

    def get_resp(self, query):

        return resp