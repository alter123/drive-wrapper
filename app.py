import json
import os
import time
import redis

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, disconnect, emit
from rq import Queue
from rq.job import Job

from util import download_data
from worker import conn


q = Queue(connection=conn)
async_mode = None

app = Flask(__name__)
socketio = SocketIO( app, async_mode=async_mode )


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', async_mode = socketio.async_mode)


@socketio.on('search', namespace='/tasks')
def article_search(article):
    job = q.enqueue_call(func=download_data, args=(article['data'],), timeout=50)
    emit('job_id', {'data': str(job.get_id())})


@socketio.on('status', namespace='/tasks')
def status(data):
	job = Job.fetch(data['job_id'], connection=conn)
	emit('fetching', {'data': str(job.is_finished), 
	'article': ( json.dumps(job.return_value) if job.is_finished else None) } )


@socketio.on('back', namespace='/tasks')
def back():
    id = '14lalKFVdeeRh1ORz0ddRNRetb52Qi80J'
    job = q.enqueue_call(func=download_data, args=(id,), timeout=50)
    emit('job_id', {'data': str(job.get_id())})


@socketio.on('connect', namespace='/tasks')
def connect():
    id = '14lalKFVdeeRh1ORz0ddRNRetb52Qi80J'
    job = q.enqueue_call(func=download_data, args=(id,), timeout=50)
    emit('job_id', {'data': str(job.get_id())})


if __name__ == '__main__':
    socketio.run(app)
