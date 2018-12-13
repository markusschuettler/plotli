from bokeh.embed import components
from bokeh.plotting import figure
from flask import Flask, render_template

app = Flask(__name__, template_folder='.')


# Create the main plot
def create_figure():
    # prepare some data
    x = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    y0 = [i ** 2 for i in x]
    y1 = [10 ** i for i in x]
    y2 = [10 ** (i ** 2) for i in x]

    # create a new plot
    p = figure(
        tools="pan,box_zoom,reset,save",
        y_axis_type="log", y_range=[0.001, 10 ** 11], title="log axis example",
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
    return render_template("hello_world.html", script=script, div=div)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
