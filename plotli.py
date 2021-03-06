import time
from datetime import datetime as dt
from multiprocessing import Process, Value
import logging

import numpy as np
import requests
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, Span
from flask import Flask, render_template, request

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, template_folder='.')

TRANSFERWISE_KEY = 'dad99d7d8e52c2c8aaf9fda788d8acdc'
FILENAME = 'rates.txt'


def record_loop(loop_on,lasttimestamp):
    lastrate = 0
    try:
        with open('data/' + FILENAME, 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                lastrate = float(lines[-1].split()[1])
                logging.info(f'Last rate found in {FILENAME}: {lastrate}')
    except Exception as e:
        logging.error(f'Something went horribly wrong while trying to read the last rate: {e}')

    logging.debug(f'At the beginning of record loop with loop_on={loop_on.value}')
    while loop_on.value:
        url = "https://transferwise.com/api/v1/payment/calculate?amount=1" \
              "&sourceCurrency=CHF&targetCurrency=EUR"
        try:
            req = requests.get(url, headers={'X-Authorization-key': TRANSFERWISE_KEY})
        except Exception as e:
            logging.error(f'Something went horribly wrong while trying to read the last rate: {e}')
        else:
            logging.debug(req.status_code)
            logging.debug(req.content)
            if req.status_code == requests.codes.ok:
                rate = req.json()['transferwiseRate']
                lasttimestamp.value = dt.now().timestamp()
                if rate != lastrate:
                    with open('data/' + FILENAME, 'a') as f:
                        logging.debug(f'Writing to rates file: {lasttimestamp.value}, {rate}')
                        print(lasttimestamp.value, rate, file=f)
                    lastrate = rate
        time.sleep(10)


# Create the main plot
def create_figure(data):
    # prepare some data

    # create a new plot
    p = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        y_axis_label='EUR/CHF', x_axis_type="datetime",
        title='teeny tiny graph'
    )
    # p.sizing_mode='stretch_width'
    if data is not None and len(data.shape) == 2:
        args=request.args
        amount=5000
        if 'amount' in args:
            amount=int(args['amount'])
        maxline=0.89
        minline=0.88
        if 'max' in args:
            maxline=float(args['max'])
        if 'min' in args:
            minline=float(args['min'])
        x = data[:, 0].astype('i8').view('datetime64[s]')
        y = data[:, 1]
        # always plot the last value up to the current time
        x=np.hstack((x,dt.now()))
        y=np.hstack((y,y[-1]))
        # add some renderers
        hline=Span(location=y[-1],dimension='width',line_color='black')
        hline_min=Span(location=minline,dimension='width',line_color='red')
        hline_max=Span(location=maxline,dimension='width',line_color='green')

        p.renderers.extend([hline,hline_min,hline_max])
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
        off=y.ptp()*0.04
        minrate=y.min()-off
        maxrate=y.max()+off
        fee=amount*0.002991+1.49578
        min_amount=(amount-fee)*(minrate)
        max_amount=(amount-fee)*(maxrate)
        p.y_range=Range1d(start=y.min()-off,end=y.max()+off)
        p.extra_y_ranges = {"magic": Range1d(start=min_amount, end=max_amount)}

        # add the second axis to the plot
        p.add_layout(LinearAxis(y_range_name="magic", axis_label='EUR'), 'right')
    return p


@app.route('/')
def hello_world():
    global lasttimestamp
    data = None
    try:
        data = np.loadtxt('data/' + FILENAME, delimiter=' ')
    except Exception as e:
        logging.error(f'Something went horribly wrong while trying to read the damned data: {e}\nas if that\'s ever gonna happen...')
    # Create the plot
    plot = create_figure(data)

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    if data is not None and len(data.shape) == 2:
        timetext=dt.fromtimestamp(lasttimestamp.value+3600).strftime('%H:%M:%S')
        text = f'{data[-1, 1]:.5f} CHF/EUR @ {timetext}'
    else:
        text = 'test'
    return render_template("plotli.html", script=script, div=div, title=text)


if __name__ == '__main__':
    recording_on = Value('b', True)
    lasttimestamp=Value('d',0)
    process = Process(target=record_loop, args=(recording_on,lasttimestamp))
    process.start()
    app.run(host='0.0.0.0', port=8080)

    process.join()
