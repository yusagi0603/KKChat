# -*- coding: utf-8 -*-
import json
import random

import jieba
import numpy
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from config import config, db

class YuBot():

    @classmethod
    def activate_bot(cls):

        '''
        # connect to mongoDB with data saved
        client = MongoClinet(host=db.MONGO_SETTING['URL'])
        db = client(db.MONGO_SETTING['Database'])
        
        all_coll = {
            "resp": db['response'],
            "song": db['song']
        }
        '''
        with open('data/resp.json', 'r', encoding='utf-8') as f:
            resp = json.load(f)
        default_resp = resp.get('scenario_default')

        return cls(default_resp)

    def __init__(self, default_resp, all_coll=None,interested_topic=None, topic_detail=None):
        self.default_resp = default_resp
        self.all_coll = all_coll # different collection in mongoDB with different data
        self.topic = interested_topic # store through process
        self.topic_detail = topic_detail # store through process
        self.scenario = None

    def get_resp(self, query):

        msg_scenario = config.scenario_dict.get(query)
        # print(msg_scenario)
        
        # classify scenario at first
        if msg_scenario is not None: # init or reset
            resp_candidate = self.default_resp.get(msg_scenario)# list -> random select one
            resp = {"answer": random.choice(resp_candidate), 
                    "confidence":1.0}# default msg based on each scenario
            self.scenario = msg_scenario

        else : # already in scenario
            
            '''
            # # Neural Network embedding version
            # connect different collection based on scenario
            # compare similarity of embedding vector of between query & song/playlist
            # return the top n nearest answer.
            '''
            with open("data/resp/{}.json".format(self.scenario), encoding='utf-8') as f:
                resp_dict = json.load(f)  
            
            vectorizer = TfidfVectorizer()
            all_query = np.array((list(resp_dict.keys())).append(query))
            tfidf = vectorizer.fit_transform(all_query).toarray()
            
            cosine_similarities = linear_kernel(tfidf[-1], tfidf).flatten() # simlarity between query and all the other
            related_docs_indices = cosine_similarities.argsort()[-2] # top1(excluse itself)
            
            resp = {"answer":list(all_query)[related_docs_indices], 
                    "confidence":cosine_similarities[-2]}  # resp, similarity
            
        return resp

if __name__ == '__main__':

    Bot = YuBot.activate_bot()
    resp = Bot.get_resp(query='來聊天')
    print(resp)
    # bot.get_resp(query='心情')