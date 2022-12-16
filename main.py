from flask import Flask, flash, render_template, redirect, request, url_for
from flask_dance.contrib.github import github
from flask_bootstrap import Bootstrap
from flask_login import logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.exceptions import Forbidden
#from werkzeug.wrappers import request
from forms import NameForm
import json

import os
import pandas as pd
import numpy as np
import pyterrier as pt
from collections import Counter
import fastrank
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot as plt

from models import db, login_manager, Game, saved
from app.oauth import github_blueprint
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

f = open('recommend_graph.json')
graph = json.load(f)
f.close()

if not pt.started():
    pt.init()

index_dir = "./data_labeling/game_index_dir"

with open('washed_game_data.csv', 'r') as f:
    data_df = pd.read_csv(f)
data_df["userscore"] = data_df["userscore"].astype(str)

summaries = {}
for index, row in data_df.iterrows():
    summaries[row['name']] = row['summary']

docno_col = ['d' + str(i) for i in range(len(data_df))]
data_df.insert(0, "docno", docno_col)

RANK_CUTOFF = 15
SEED = 42

if not os.path.exists(os.path.join(index_dir, "data.properties")):
    indexer = pt.DFIndexer(index_dir, overwrite=True, tokeniser="UTFTokeniser", stopwords='terrier')
    index_ref = indexer.index(data_df["summary"], data_df["name"], data_df["date"], data_df["genre"], data_df["userscore"], data_df["docno"])
else:
    index_ref = pt.IndexRef.of(index_dir + "/data.properties")

index = pt.IndexFactory.of(index_ref)

bm25 = pt.BatchRetrieve(index, wmodel="BM25")
tfidf = pt.BatchRetrieve(index, wmodel="TF_IDF")
random_scorer = lambda keyFreq, posting, entryStats, collStats: 0
rand_retr = pt.BatchRetrieve(index, wmodel=random_scorer)

game_sothis_features = (tfidf % RANK_CUTOFF) >> pt.text.get_text(index, ["name", "date", "genre", "userscore"]) >> (
        pt.transformer.IdentityTransformer()
        ** 
        (pt.apply.doc_score(lambda row: float(row["userscore"])))
        ** # abstract coordinate match
        pt.BatchRetrieve(index, wmodel="CoordinateMatch")
    )
sname = ["random", "bm25", "tfidf", "game-sothis"]
fname = ["name", "userscore", "date"]

db_name = 'games.db'

app = Flask(__name__)

app.secret_key = "supersecretkey"
app.register_blueprint(github_blueprint, url_prefix="/login")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

#app.config['SECRET_KEY'] = 'RandomSecretKey'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()
    
bootstrap = Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    f = open('data.json')
    games = json.load(f)
    f.close()
    for i in range(100):
        
        game = db.session.query(Game).filter_by(name=games['name'][i]).first()
        print(game)
        game.genre = games['genre'][i]
   
        db.session.commit
    #bob =  db.session.query(Game).filter_by(name=games['name'][0]).first()
    #print(bob.genre)
    '''
    count = ""
    form = NameForm(request.form)
    if request.method == 'POST':
        return search_results(form)

    if current_user.is_authenticated: 
        uid = current_user.id
        count = db.session.query(saved).filter_by(user_id = uid).count() 
    
    return render_template('index.html', form = form, count = count)

@app.route('/results')
def search_results(form):
    #if form.validate_on_submit():

    count = ""
    if current_user.is_authenticated: 
        uid = current_user.id
        count = db.session.query(saved).filter_by(user_id = uid).count() 

    query = form.data['name']

    results = game_sothis_features.search(query)
    results_summary = [summaries[rows['name']] for i, rows in results.iterrows()]
    results['summary'] = results_summary
    #results = Game.query.filter(Game.name.contains(query)).order_by(Game.id).all()

    print(results)

    print(search_results)
    if results.empty:
        flash('No results found!')
        return redirect(url_for('index'))
    else:
        return render_template('results.html', form = form, count = count, results=results)

@app.route('/all' , methods=['GET', 'POST'])
def show_all():
    form = NameForm(request.form)
    if request.method == 'POST':
        return search_results(form)

    count = ""
    if current_user.is_authenticated: 
        uid = current_user.id
        count = db.session.query(saved).filter_by(user_id = uid).count()

    return render_template('show_all.html', form = form, count = count, games = Game.query.all())

@app.route("/github")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    res = github.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on GitHub"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))    

@app.route('/save', methods=['GET', 'POST'])
@login_required
def save():

    uid = current_user.id
    name = request.args.get("name")
    results = bool(db.session.query(saved).filter_by(user_id = uid, game_name = name).first())

    if not results:
        insert_stmnt = saved.insert().values(user_id=uid, game_name=name)
        db.session.execute(insert_stmnt) 
        db.session.commit()
        print('success!')
  
    return redirect(url_for('index'))

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    uid = current_user.id
    name = request.args.get("name")
    db.session.query(saved).filter_by(user_id = uid, game_name = name).delete()
    db.session.commit()
    print('success!')
    
    return redirect(url_for('index'))

@app.route('/mylist', methods=['GET', 'POST'])
@login_required
def my_list():
    form = NameForm(request.form)
    if request.method == 'POST':
        return search_results(form)

    count = ""
    if current_user.is_authenticated: 
        uid = current_user.id
        count = db.session.query(saved).filter_by(user_id = uid).count() 
        
    uid = current_user.id
    return render_template('my_list.html', form = form, count = count, my_games = db.session.query(saved).filter_by(user_id = uid).all() )

@app.route('/recommendations', methods=['GET', 'POST'])
@login_required
def recommend():
    form = NameForm(request.form)
    if request.method == 'POST':
        return search_results(form)

    count = ""
    if current_user.is_authenticated: 
        uid = current_user.id
        count = db.session.query(saved).filter_by(user_id = uid).count() 
        
    uid = current_user.id
    my_games = db.session.query(saved).filter_by(user_id = uid).all()
    most_recommend_set = {}
    recommend_dic = {}
    for item in my_games:
        if item == my_games[0]:
            most_recommend_set = set([x[0] for x in graph[item.game_name]])
            recommend_dic[item.game_name] = [x[0] for x in graph[item.game_name][:3]]
        else:
            most_recommend_set = most_recommend_set & set([x[0] for x in graph[item.game_name]])
            recommend_dic[item.game_name] = [x[0] for x in graph[item.game_name][:3]]
    #print(most_recommend_set)
    #print(recommend_dic)
    return render_template('recommend.html', form = form, count = count, most_recommends = None if len(most_recommend_set) == 0 else most_recommend_set,  recommends = recommend_dic )

'''
if __name__ == '__main__':  
    app.run(debug=True)
'''