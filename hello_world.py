from bokeh.embed import components
from bokeh.plotting import figure
from flask import Flask, render_template
from multiprocessing import Process, Value
import time
from datetime import datetime as dt
import numpy as np
import requests

app = Flask(__name__, template_folder='.')

TRANSFERWISE_KEY = 'dad99d7d8e52c2c8aaf9fda788d8acdc'

filename='rates.txt'

def record_loop(loop_on):
    lastrate=0
    try:
        with open('data/'+filename, 'r') as f:
            lines=f.readlines()
            if len(lines)>0:
                lastrate=float(lines[-1].split()[1])
                print(lastrate)
    except:
        pass
    while True:
        if loop_on.value == True:
            url = "https://transferwise.com/api/v1/payment/calculate?amount=1" \
                  "&sourceCurrency=CHF&targetCurrency=EUR"
            req = requests.get(url, headers={'X-Authorization-key': TRANSFERWISE_KEY})
            if req.status_code==requests.codes.ok:
                rate=req.json()['transferwiseRate']
                if rate!=lastrate:
                    with open('data/'+filename, 'a') as f:
                        print(dt.now().timestamp(), rate, file=f)
                    lastrate=rate
        time.sleep(10)


# Create the main plot
def create_figure(data):
    # prepare some data

    # create a new plot
    p = figure(
        tools="pan,box_zoom,reset,save",
        y_axis_label='EUR/CHF',x_axis_type="datetime"
    )
    #p.sizing_mode='scale_both'

    if data is not None and len(data.shape)==2:
        x = data[:,0].astype('i8').view('datetime64[s]')
        y=data[:,1]
        # add some renderers
        p.step(x, y)
    return p


@app.route('/')
def hello_world():
    data=None
    try:
        data=np.loadtxt('data/'+filename,delimiter=' ')
    except Exception as e:
        print(e)
    # Create the plot
    plot = create_figure(data)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    if data is not None and len(data.shape)==2:
        text = '{}CHF/EUR'.format(data[-1,1])
    else:
        text = 'test'
    return render_template("hello_world.html", script=script, div=div, title=text)


if __name__ == '__main__':
    recording_on = Value('b', True)
    p = Process(target=record_loop, args=(recording_on,))
    p.start()
    app.run(host='0.0.0.0', port=8080)

    p.join()
