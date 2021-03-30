import json
import os

import cpca
from flask import Flask, render_template, flash, request
from flask_restful import reqparse, Api, Resource
from jieba import posseg

import raw2json
from forms import KeywordSearchForm
from neo4j_models import Neo4jTool

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
api = Api(app)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))  # API中文支持
app.config['SECRET_KEY'] = SECRET_KEY

global entity_json
neo_con = Neo4jTool()
neo_con.connect2neo4j()


@app.route('/', methods=['GET', 'POST'])
def main():
    print('Neo4j has connected...')
    form = KeywordSearchForm(request.form)
    try:
        if form.validate_on_submit():
            print("Submit successfully...")
            keyword = form.keyword.data.strip()
            res = entity_analysis(keyword)
            try:
                if len(res) == 0:
                    nothing = {'title': '<h1>Not Found</h1>'}
                    return render_template('entity.html', nothing=json.dumps(nothing, ensure_ascii=False), form=form)
                else:
                    res_json = raw2json.analysis(json.loads(json.dumps(res, ensure_ascii=False)))
                    return render_template('entity.html', data=res_json['data'], links=res_json['links'],
                                           format_triple=res_json['format_triple'], categories=res_json['categories'],
                                           form=form)
            except:
                print("[log-neo4j] some error exist!!!")
                flash("some error exist!!!")
        else:
            flash("valid form")
    except:
        print("[log-neo4j] empty form")

    return render_template('entity.html', form=form)


def is_loc(loc):
    d = cpca.transform([loc])
    if str(d['省'][0]):
        return True
    if str(d['市'][0]):
        return True
    if str(d['区'][0]):
        return True
    return False


def entity_analysis(entity):
    db = neo_con
    words = entity.split(' ')
    if len(words) == 1:
        if is_loc(words[0]):
            return db.match_location4event_patient(entity)
        else:
            wordp = posseg.cut(words[0])
            for w in wordp:
                if w.flag in ['v', 'vd', 'vn', 'vg']:
                    return db.match_topic4event(entity)
                elif w.flag in ['nr']:
                    return db.match_patient_name(entity)
    elif len(words) == 2:
        isloc_dict = {}
        flag = 0
        for word in words:
            isloc_dict[word] = is_loc(word)
            if isloc_dict[word]:
                flag = 1
        if isloc_dict[words[0]]:
            wordp = posseg.cut(words[1])
            for w in wordp:
                if w.flag in ['v', 'vd', 'vn', 'vg']:
                    return db.match_location_topic4event(words[0], words[1])
                elif w.flag in ['m']:
                    return db.match_location_time4event_patient(words[0], words[1])
                else:
                    gender = words[1].replace('性', '').replace('生', '')
                    return db.match_location_gender4patient(words[0], gender)
        else:
            wordp = posseg.cut(words[0])
            for w in wordp:
                if w.flag in ['v', 'vd', 'vn', 'vg']:
                    return db.match_location_topic4event(words[1], words[0])
                elif w.flag in ['m']:
                    return db.match_location_time4event_patient(words[1], words[0])
                else:
                    gender = words[0].replace('性', '').replace('生', '')
                    return db.match_location_gender4patient(words[1], gender)

        if not flag:
            wordp = posseg.cut(words[0])
            for w in wordp:
                if w.flag in ['m']:
                    return db.match_name_time4location_event(words[1], words[0])
                else:
                    return db.match_name_time4location_event(words[0], words[1])
    elif len(words) == 3:
        loc = ''
        for word in words:
            if is_loc(word):
                loc = word
                words.remove(word)
                break
        wordp = posseg.cut(words[0])
        for w in wordp:
            if w.flag in ['m']:
                return db.match_location_time_topic4patient(loc, words[0], words[1])
            else:
                return db.match_location_time_topic4patient(loc, words[1], words[0])

    else:
        answer = db.match_location4event_patient(words[0])
        if len(answer) == 0:
            answer = db.match_topic4event(words[0])
        return answer


#  For Api


parser = reqparse.RequestParser()
parser.add_argument('string', type=str)


class post_data(Resource):
    def post(self):
        args = parser.parse_args()
        print('@', args)
        entity_json = raw2json.analysis(json.loads(json.dumps(entity_analysis(args['string']), ensure_ascii=False)))
        return entity_json


class get_data(Resource):
    def get(self, string):  # 根据string获取对应的value
        entity_json = raw2json.analysis(json.loads(json.dumps(entity_analysis(string), ensure_ascii=False)))
        return entity_json


api.add_resource(get_data, '/api/<string>')
api.add_resource(post_data, '/api')

if __name__ == '__main__':
    app.run()
