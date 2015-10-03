from flask import Flask, render_template, request, redirect
import Quandl
import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8
from bokeh.charts import TimeSeries

app = Flask(__name__)

app.vars = {}


def stock_to_caps(stock_name):
	'''
	Simple test function. stock_name should be a string, this converts it
	to caps and chops off all but the first four letters.
	'''
	return stock_name.upper()[:4]

def get_data(stock_name):
	return Quandl.get("".join(["WIKI/",stock_to_caps(stock_name),".4"]),authtoken="ppGMYxKEUmJ16a11sa23")



@app.route('/')
def redirect_to_index():
	return redirect('/index')

@app.route('/index', methods=['POST','GET'])
def index():
	error = None
	if request.method == 'POST':
		try:
			app.vars['stock_name'] = stock_to_caps(request.form['ticker'])
			app.vars['data_table'] = get_data(app.vars['stock_name'])
		except:
			app.vars['stock_name'] = 'GOOG'
			app.vars['data_table'] = get_data('GOOG')

	else:
		app.vars['stock_name'] = 'GOOG'
		app.vars['data_table'] = get_data('GOOG')
	fig = TimeSeries(app.vars['data_table'])

	plot_resources = RESOURCES.render(
		js_raw=INLINE.js_raw,
		css_raw=INLINE.css_raw,
		js_files=INLINE.js_files,
		css_files=INLINE.css_files
		)
	script, div = components(fig, INLINE)

	return render_template('index.html',
		                   name=app.vars['stock_name'],
		                   data=app.vars['data_table'],
		                   plot_script=script,
		                   plot_div=div,
		                   plot_resources=plot_resources)
	
if __name__ == '__main__':
	app.run(host='0.0.0.0')




