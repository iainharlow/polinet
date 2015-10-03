from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8
from bokeh.charts import TimeSeries

app_polinet = Flask(__name__)

app_polinet.vars = {}

'''
Main functions here
'''

def get_pol_name(pol_name):
	'''
	Simple test function. pol_name should be a string, this converts it
	to caps.
	'''
	return pol_name.upper()

def get_pol_data(pol_name):
	'''
	Look up the basic details for the politician chosen.
	'''
	return pol_name.upper()





'''
Route functions here
'''

@app_polinet.route('/')
def redirect_to_polinet():
	return redirect('/polinet')


@app_polinet.route('/polinet', methods=['POST','GET'])
def polinet():

	error = None
	if request.method == 'POST':
		try:
			app_polinet.vars['pol_name'] = get_pol_name(request.form['pol_name'])
		except:
			app_polinet.vars['pol_name'] = 'Not a valid name'

	else:
		app_polinet.vars['pol_name'] = 'Bernard Sanders'


	app.vars['pol_data'] = pd.DataFrame([[1,2,3,1,3,2,4,1]])
	fig = TimeSeries(app.vars['pol_data'])

	plot_resources = RESOURCES.render(
		js_raw=INLINE.js_raw,
		css_raw=INLINE.css_raw,
		js_files=INLINE.js_files,
		css_files=INLINE.css_files
		)
	script, div = components(fig, INLINE)

	return render_template('polinet.html',
		                   name=app_polinet.vars['pol_name'],
		                   data=app_polinet.vars['pol_data'],
		                   plot_script=script,
		                   plot_div=div,
		                   plot_resources=plot_resources)

'''
Run app
'''

if __name__ == '__main__':
    app_polinet.run(host='0.0.0.0', debug=False)




