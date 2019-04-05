# -*- coding: utf-8 -*-
import json
import random

import jieba
import numpy as np
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

    def __init__(self, default_resp, all_coll=None,interested_topic=None, topic_detail=None, scenario=None):
        self.default_resp = default_resp
        self.all_coll = all_coll # different collection in mongoDB with different data
        self.topic = interested_topic # store through process
        self.topic_detail = topic_detail # store through process
        self.scenario = scenario # store through process

    def get_resp(self, query):
        '''

        '''
        if self.scenario is None:
            msg_scenario = config.scenario_dict.get(query)
            
            # classify scenario at first
            resp_candidate = self.default_resp.get(msg_scenario)# list -> random select one
            resp = {"answer": random.choice(resp_candidate), 
                    "confidence":1.0}# default msg based on each scenario
            self.scenario = msg_scenario # save for the next answer

        else : # already in scenario

            # find detail keyword in given scenario
            with open('data/scenario_keyword.json', encoding='utf-8') as f:
                kw_dict = json.load(f)
            scn_kw_dict = kw_dict.get(self.scenario) # get kw_dict based on last answer accroding to scenario
            all_kw = [' '.join(sub_kw_list) for sub_kw_list in list(scn_kw_dict.values())] # ex: ([happy related], [sad realted], .., [query])
            all_kw.extend(jieba.lcut(query)) 
            np_kw = np.array([word_list for word_list in all_kw])
            
            # td-idf to find the similar answer
            vectorizer = TfidfVectorizer()  
            tfidf = vectorizer.fit_transform(np_kw).toarray()
            cosine_similarities = linear_kernel(tfidf[-1].reshape(1,-1), tfidf).flatten() # simlarity between query and all the other
            related_docs_indices = cosine_similarities.argsort()[-2] # top1(excluse itself)

            # transform found scenario keyword from chinese to english
            tar_kw_value = (list(all_kw)[related_docs_indices]).split(' ') # ex: '生氣 憤怒' -> ['生氣', '憤怒'] to search corresponding key "angry"    
            for key_detail, kw_list in kw_dict.items():  
                if tar_kw_value in list(kw_list.values()): # get key based on value 
                    for eng_code, chi_code in list(kw_list.items()):
                        if tar_kw_value == chi_code:
                            resp_kw = eng_code  
        
            with open("data/resp/{}.json".format(self.scenario), encoding='utf-8') as f:
                resp_dict = json.load(f) # ex: mood_json
                try: # resp_kw exist
                    answer = "{introduction}{song}".format(
                        introduction=random.choice(resp_dict.get('introduction')),
                        song=random.choice(resp_dict.get('song').get(resp_kw))
                        )
                except: # unfound keyword for resp_kw
                    answer = self.default_resp.get(self.scenario)[0] + '\n 或是輸入 「聽歌」來重選各種情境喔!'
            
            resp = {"answer": answer, 
                    "confidence": cosine_similarities[related_docs_indices]} 

        return resp

if __name__ == '__main__':

    Bot = YuBot.activate_bot()
    for query in ['心情', '你是誰']:
        print("For query: '{}'".format(query))
        resp = Bot.get_resp(query=query)
        print(resp)
    