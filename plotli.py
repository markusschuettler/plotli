import time
from datetime import datetime as dt
from multiprocessing import Process, Value
import logging

import numpy as np
import requests
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter
from bokeh.plotting import figure
from flask import Flask, render_template

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, template_folder='.')

TRANSFERWISE_KEY = 'dad99d7d8e52c2c8aaf9fda788d8acdc'
FILENAME = 'rates.txt'


def record_loop(loop_on):
    lastrate = 0
    lasttimestamp = 0
    try:
        with open('data/' + FILENAME, 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                lastrate = float(lines[-1].split()[1])
                logging.info(f'Last rate found in {FILENAME}: {lastrate}')
    except Exception as e:
        logging.error(f'Something went horribly wrong while trying to read the last rate: {e}')

    while True:
        logging.debug(f'At the beginning of record loop with loop_on={loop_on.value}')
        if loop_on.value:
            url = "https://transferwise.com/api/v1/payment/calculate?amount=1" \
                  "&sourceCurrency=CHF&targetCurrency=EUR"
            req = requests.get(url, headers={'X-Authorization-key': TRANSFERWISE_KEY})
            logging.debug(req.status_code)
            logging.debug(req.content)
            if req.status_code == requests.codes.ok:
                rate = req.json()['transferwiseRate']
                if rate != lastrate or dt.now().timestamp() - lasttimestamp > 300:
                    lasttimestamp = dt.now().timestamp()
                    with open('data/' + FILENAME, 'a') as f:
                        logging.debug(f'Writing to rates file: {lasttimestamp}, {rate}')
                        print(lasttimestamp, rate, file=f)
                    lastrate = rate
        time.sleep(10)


# Create the main plot
def create_figure(data):
    # prepare some data

    # create a new plot
    p = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        y_axis_label='EUR/CHF', x_axis_type="datetime"
    )
    # p.sizing_mode='scale_both'

    if data is not None and len(data.shape) == 2:
        x = data[:, 0].astype('i8').view('datetime64[s]')
        y = data[:, 1]
        # add some renderers
        p.step(x, y, mode='after')

        p.xaxis.major_label_orientation = 3.14 / 4
        p.xaxis.formatter = DatetimeTickFormatter(
            minutes=["%H:%M"],
            hourmin=["%H:%M"],
            hours=["%H:%M"],
            days=["%d.%m."],
            months=["%b"],
            years=["%Y"],
        )
    return p


@app.route('/')
def hello_world():
    data = None
    try:
        data = np.loadtxt('data/' + FILENAME, delimiter=' ')
    except Exception as e:
        logging.error(f'Something went horribly wrong while trying to read the last rate: {e}')
    # Create the plot
    plot = create_figure(data)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    if data is not None and len(data.shape) == 2:
        text = '{}CHF/EUR'.format(data[-1, 1])
    else:
        text = 'test'
    return render_template("plotli.html", script=script, div=div, title=text)


if __name__ == '__main__':
    recording_on = Value('b', True)
    process = Process(target=record_loop, args=(recording_on,))
    process.start()
    app.run(host='0.0.0.0', port=8080)

    process.join()
