import os
import sqlite3
import json
from flask import Flask, request, g, redirect
from flask_restful import Resource, Api, reqparse

# create our little application :)
app = Flask(__name__)
api = Api(app)
app.config.from_object(__name__)


userParser = reqparse.RequestParser()
userParser.add_argument('username', type=str, required=True)

jobParser = reqparse.RequestParser()
jobParser.add_argument('description', type=str, required=True)
jobParser.add_argument('location', type=str, required=True)
jobParser.add_argument('requester', type=int, required=True)

claimParser = reqparse.RequestParser()
claimParser.add_argument('id', type=int, required=True)
claimParser.add_argument('claimer', type=int, required=True)

idParser = reqparse.RequestParser()
idParser.add_argument('id', type=int, required=True)


DATABASE=os.path.join(app.root_path, 'plants.db')

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.commit()
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('plants/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


class ConsumerLogin(Resource):
    def post(self):
        args = userParser.parse_args()
        c = get_db().cursor()
        t = [args['username']]
        c.execute('SELECT COUNT(*) FROM `consumers` WHERE `username`=?;', t)
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO `consumers` (`username`) VALUES (?)", t)
        c.execute('SELECT `id` FROM `consumers` WHERE `username`=?', t)
        return c.fetchone()[0]


class ProviderLogin(Resource):
    def post(self):
        args = userParser.parse_args()
        c = get_db().cursor()
        t = [args['username']]
        c.execute('SELECT COUNT(*) FROM `providers` WHERE `username`=?;', t)
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO `providers` (`username`) VALUES (?);', t)
        c.execute('SELECT `id` FROM `providers` WHERE `username`=?', t)
        return c.fetchone()[0]


class AddJob(Resource):
    def post(self):
        args = jobParser.parse_args()
        c = get_db().cursor()
        t = [args['description'], args['location'], args['requester']]
        c.execute('INSERT INTO `jobs` (`description`, `location`, `requester`) VALUES (?, ?, ?);', t)


class ClaimJob(Resource):
    def post(self):
        args = claimParser.parse_args()
        c = get_db().cursor()
        t = [args['id']]
        c.execute('SELECT COUNT(*) FROM `jobs` WHERE `id`=? AND `claimer` IS NULL', t)
        if c.fetchone()[0] == 1:
            t = [args['claimer'], args['id']]
            c.execute('UPDATE `jobs` SET `claimer`=? WHERE `id`=?;', t)
            return 1
        return 0


class RetrieveAvailableJobs(Resource):
    def post(self):
        values = {'jobs': []}
        c = get_db().cursor()
        for row in c.execute('SELECT * FROM `jobs` WHERE `claimer` IS NULL'):
            values['jobs'].append({'description': row[1], 'location': row[2], 'id': row[0]})
        return values


class RetrievePendingJobs(Resource):
    def post(self):
        args = idParser.parse_args()
        values = {'jobs': []}
        t = [args['id']]
        c = get_db().cursor()
        for row in c.execute('SELECT * FROM `jobs` WHERE `requester`=? AND `completed`=0', t):
            values['jobs'].append({'description': row[1], 'location': row[2], 'claimer': row[4]})
        return values


class RetrieveClaimedJobs(Resource):
    def post(self):
        args = idParser.parse_args()
        values = {'jobs': []}
        t = [args['id']]
        c = get_db().cursor()
        for row in c.execute('SELECT * FROM `jobs` WHERE `claimer`=? AND `completed`=0', t):
            values['jobs'].append({'description': row[1], 'location': row[2]})
        return values


class CompleteJob(Resource):
    def post(self):
        args = idParser.parse_args()
        t = [args['id']]
        c = get_db().cursor()
        c.execute('UPDATE `jobs` SET `completed`=1 WHERE `id`=?', t)


api.add_resource(ConsumerLogin, '/consumerLogin')
api.add_resource(ProviderLogin, '/providerLogin')
api.add_resource(AddJob, '/addJob')
api.add_resource(ClaimJob, '/claimJob')
api.add_resource(RetrieveAvailableJobs, '/retrieveAvailableJobs')
api.add_resource(RetrievePendingJobs, '/retrievePendingJobs')
api.add_resource(RetrieveClaimedJobs, '/retrieveClaimedJobs')
api.add_resource(CompleteJob, '/completeJob')


if __name__ == '__main__':
    app.run(debug=True)
