from bokeh.embed import components
from bokeh.plotting import figure
from flask import Flask, render_template
from multiprocessing import Process, Value
import time
import numpy as np
from requests


app = Flask(__name__, template_folder='.')

TRANSFERWISE_KEY = 'dad99d7d8e52c2c8aaf9fda788d8acdc'

def record_loop(loop_on):
   while True:
      if loop_on.value == True:
          with open('data/test.txt','a') as f:
              print(np.random.randint(0,10),file=f)
      time.sleep(1)

# Create the main plot
def create_figure():
    # prepare some data
    x = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    y0 = [i ** 2 for i in x]
    y1 = [10 ** i for i in x]
    y2 = [10 ** (i ** 2) for i in x]

    # create a new plot
    p = figure(
        tools="pan,box_zoom,reset,save", y_range=[0.001, 10 ** 11], title="magic",
        x_axis_label='sections', y_axis_label='particles'
    )

    # add some renderers
    p.line(x, x, legend="y=x")
    p.circle(x, x, legend="y=x", fill_color="white", size=8)
    p.line(x, y0, legend="y=x^2", line_width=3)
    p.line(x, y1, legend="y=10^x", line_color="red")
    p.circle(x, y1, legend="y=10^x", fill_color="red", line_color="red", size=6)
    p.line(x, y2, legend="y=10^x^2", line_color="orange", line_dash="4 4")
    return p


@app.route('/')
def hello_world():
    # Create the plot
    plot = create_figure()

    # Embed plot into HTML via Flask Render
    script, div = components(plot)
    try:
        with open('data/test.txt','r') as f:
            text=f.readlines()[-1]
    except Exception as e:
        print(e)
        text='test'
    return render_template("hello_world.html", script=script, div=div,title=text)


if __name__ == '__main__':
    recording_on = Value('b', True)
    p = Process(target=record_loop, args=(recording_on,))
    p.start()
    app.run(host='0.0.0.0', port=8080)

    p.join()
