from flask import Flask, render_template, request, redirect

import pandas as pd
import numpy as np
import dill
import os
from bokeh.embed import components
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8
from bokeh.charts import TimeSeries
from math import log, sqrt

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__)

app.vars = {}

opensecrets_api_key = os.environ['OPENSECRETS_API_KEY']

cols = ['A','B','C','D','E','F','G','H','J','K','L','M','Native American Tribes','T','X','Y','Z','Self','Individual Small','Individual Large']
sources = ['Agriculture',
           'Construction',
           'Communications',
           'Defense','Energy',
           'Finance',
           'General Commerce',
           'Health',
           'Single Issue',
           'Legal',
           'Labor/Unions',
           'Manufacturing',
           'Native Groups',
           'Transportation',
           'Other',
           'Unknown',
           'Political Party',
           'Self',
           'Small Ind',
           'Large Ind']


cluster_names = {0:'Self-Funded.',
                 1:'Rural and Industry Supported.',
                 2:'Connected Socialites.',
                 3:'Labor & Union Candidates.',
                 4:'High Profile Populists.',
                 5:'Culture Warriors.',
                 6:'Establishment-Backed.',
                 7:'Individual Supported.',
                 8:'Fundraisers and Bundlers.'}

cluster_sizes = {0:r'This is a moderately sized cluster (10% of candidates). It skews Republican (60%) with a fair proportion of Independent and Libertarian candidates (10%).',
                 1:r'This is a large and broad cluster (24% of candidates). It skews slightly towards Republican candidates (57%) with virtually no Independent/Libertarians',
                 2:r'This is a large cluster (21% of candidates). It skews quite heavily towards Republicans (63%; compared to 31% Democrats).',
                 3:r'This is one of the smallest and most specific clusters (2% of candidates). It is dominated by Democratic candidates (85%).',
                 4:r'This is a small cluster (5% of candidates). It is fairly evenly distributed across the parties, but with a high proportion of Independent/Libertarian candidates (15%) and more Democrats (48%) than Republicans (37%).',
                 5:r'This is a small cluster (3% of candidates). It is dominated by Republican candidates (70%).',
                 6:r'This is a small cluster (2% of candidates). It is quite evenly split across the two main parties, and 3rd party candidates (often for higher profile positions) are also strongly represented.',
                 7:r'This is a fairly large cluster (16% of candidates). It is evenly split across the two main parties (49% Democrat, 46% Republican).',
                 8:r'This is a fairly large cluster (17% of of candidates). It is evenly split across the two main parties (51% Democrat, 47% Republican), with little Independent/Libertarian membership.'}

cluster_descriptions = {0:r'Politicians in this group rely to a far greater extent than their peers on their own sources of income. In some cases this might simply reflect large personal wealth, but often also indicates a less well supported (but possibly more independent) candidate in general. This group see particularly few individual contributions compared to the average. Examples: Danny Tarkanian (R), Bob Montigel (D).',
                        1:r'Politicians in this group have a broad range of funding sources, but rely far less than the average on their political party, small donations, and Labor groups. Instead, they are more likely to receive support from industry sources, especially Defense, Energy, Agriculture and Transportation, as well as large individual donors. This may imply support for lower taxes and regulations amongst this group, in general. Many in this group also receive contributions from tribal groups, reflecting a rural bias. Examples: Mike Coffman (R), Scott Peters (D).',
                        2:r'Politicians in this group recieve the bulk of their funding in the form of large individual donations (>$1000). They are more likely to be based in wealthy, urban districts, or be well connected to wealthier circles. Examples: Hillary Clinton (D), Dana Rohrabacher (R).',
                        3:r'This cluster receives the highest support from unions. They skew to the left on economic, regulatory and labor issues. Examples: Joe Miklosi (D), Rahm Emanuel (D).',
                        4:r'Politicians in this group see the majority of their campaign contributions in the form of smaller (<$1000) individual contributions, and relatively less from industry and finance. Often this suggests a high-profile politician, or one with a strong grass-roots network. Examples: Bernie Sanders (I), Jose Luis Fernandez (R).',
                        5:r'Politicians in this group recieve far more of their funding from activist and single issue groups, and also the Legal profession. Examples: Tom Tierney (R), Gabriel Rothblatt (D).',
                        6:r'This is a core of establishment-backed candidates, often competing in higher profile or narrower races. They receieve a disproportionate amount of support from official party sources, and relatively less from individuals and their own fundraising. Examples: Chris McDaniel (R), Alma Adams (D).',
                        7:r'This group relies almost entirely on individual contributions, both small and large, for their funding. They tend to receive less from Manufacturing and Agriculture, and might tend to represent more urban districts. Less party support can indicate they run in less competitive races, or are high-profile enough to have strong personal fundraising. Examples: Alan Nunnelee (R), Tammy Baldwin (D).',
                        8:r'This group tend to be prolific fundraisers, especially from businesses, and in many cases redirect these contributions to their party and other candidates. Examples: Steny Hoyer (D), Tom Reed (R).'}


pols = dill.load(open('static/pols.p','rb'))
baseline = dill.load(open('static/baseline.p','rb'))

baseline = pd.DataFrame(baseline[cols])
name_list = list(pols.recipient_name)

def get_cluster(poli_name):
	'''
	Collect the cluster index.
	'''
	return pols[pols.recipient_name == poli_name].iloc[0]['cluster']

def comparison(row):
    if row['pol']/row['baseline'] > 1.33:
        return 'positive'
    elif row['pol']/row['baseline'] < 0.75:
        return 'negative'
    else:
        return 'neutral'

def get_data(poli_name):
	'''
	Collects the funding data for poli_name, creates a df in
	the right format for plotting along with cluster.
	'''
	f = pols[pols.recipient_name == poli_name]
	cluster = f['cluster']
	f = f[cols].transpose()
	f = pd.concat([f,baseline],axis=1)
	f.columns = ['pol','baseline']
	f['source'] = sources
	f.sort('baseline',ascending=True,inplace=True)
	f['comparison'] = f.apply(lambda row: comparison(row), axis=1)
	f.reset_index(inplace=True)
	f.drop('index',axis=1,inplace=True)
	return f

def get_crp_id(poli_name):
	

def get_opensecrets_contribs(crp_id,cycle='2016'):
    endpoint = 'http://www.opensecrets.org/api/?method=candContrib&cid='+crp_id
    query_params = {'apikey': opensecrets_api_key,
                    'output': 'json',
                    'cycle': cycle
                   }                    
    try:
        data = requests.get( endpoint, params=query_params).json()
    except:
        return None 
    return data


@app.route('/')
def redirect_to_index():
	print 'redirecting'
	return redirect('/index')

@app.route('/index', methods=['POST','GET'])
def index():
	print 'index'
	error = None
	if request.method == 'POST':
		try:
			app.vars['poli_name'] = request.form['poli_name']
			app.vars['data_table'] = get_data(app.vars['poli_name'])
		except:
			app.vars['poli_name'] = 'Ooops! Something went wrong. Choose someone else?'
			app.vars['data_table'] = get_data(app.vars['Bernie Sanders (I)'])
	else:
		app.vars['poli_name'] = 'Steny H. Hoyer (D)'
		app.vars['data_table'] = get_data('Steny H. Hoyer (D)')

	df = app.vars['data_table']
	cluster = get_cluster(app.vars['poli_name'])
	cluster_name = cluster_names[cluster]
	cluster_size = cluster_sizes[cluster]
	cluster_description = cluster_descriptions[cluster]

	crp_id = 

	'''
	EXPERIMENTAL FIGURE CODE
	'''

	comparison_color = {
	    "positive" : "#aad975",
	    "neutral" : "#e6e684",
	    "negative" : "#e6bb99",
	}

	width = 800
	height = 800
	inner_radius = 90
	outer_radius = 300 - 10

	minr = sqrt(log(.0001 * 1E4))
	maxr = sqrt(log(1 * 1E4))
	a = (outer_radius - inner_radius) / (maxr - minr)
	b = inner_radius - a * minr

	def rad(mic):
	    return a * np.sqrt(np.log(mic * 1E4)) + b

	big_angle = 2.0 * np.pi / (len(df) + 1)
	small_angle = big_angle / 7

	x = np.zeros(len(df))
	y = np.zeros(len(df))

	p = figure(plot_width=width, plot_height=height, title="Campaign Finance Sources: %s" %app.vars['poli_name'],
	    x_axis_type=None, y_axis_type=None,
	    x_range=[-420, 420], y_range=[-420, 420],
	    min_border=0, outline_line_color='#cccccc',
	    background_fill='#ffffff', border_fill='#e0e0e0')

	p.line(x+1, y+1, alpha=0)

	# large pol wedges
	angles = np.pi/2 - big_angle/2 - df.index.to_series()*big_angle
	colors = [comparison_color[comparison] for comparison in df.comparison]
	p.annular_wedge(
	    x, y, inner_radius, rad(df.baseline), -big_angle+angles, angles, color=colors,
	)

	# small baseline wedges
	p.annular_wedge(x, y, inner_radius, rad(df.pol),
		-big_angle+angles+2*small_angle, -big_angle+angles+5*small_angle,
	    fill_color="black", line_color="black")


	# circular axes and lables
	labels = np.power(10.0, np.arange(-4, 2))
	radii = a * np.sqrt(np.log(labels * 1E4)) + b
	p.circle(x[:-1], y[:-1], radius=radii[:-2], fill_color=None, line_color="#555555")
	p.text(x[:-2], radii[1:-1], [str(r) for r in labels[1:-1]],
	    text_font_size="8pt", text_align="center", text_baseline="middle")

	# radial axes
	p.annular_wedge(x, y, inner_radius-10, outer_radius+10,
	    -big_angle+angles, -big_angle+angles, color="#555555")

	# source labels
	xr = (radii[-1]+50)*np.cos(np.array(-big_angle/2 + angles))
	yr = (radii[-1]+50)*np.sin(np.array(-big_angle/2 + angles))
	label_angle=np.array(-big_angle/2+angles)
	label_angle[label_angle < -np.pi/2] += np.pi
	p.text(xr, yr, df.source, angle=label_angle,
	    text_font_size="11pt", text_align="center", text_baseline="bottom")

	# Legend
	p.circle([-45, -45, -45], [9, -9, -27], color=list(comparison_color.values()), radius=5)
	p.text([-30, -30, -30], [9, -9, -27], text=['Above average','Average','Below Average'],
	    text_font_size="9pt", text_align="left", text_baseline="middle")

	p.rect([-45], [27], width=20, height=13,
	    color="black")
	p.text([-30], [27], text=["Proportion"],
	    text_font_size="9pt", text_align="left", text_baseline="middle")

	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None

	'''
	EXPERIMENTAL FIGURE CODE END
	'''

	plot_resources = RESOURCES.render(
		js_raw=INLINE.js_raw,
		css_raw=INLINE.css_raw,
		js_files=INLINE.js_files,
		css_files=INLINE.css_files
		)

	script1, div1 = components(p, INLINE)

	return render_template('index.html',
		                   name=app.vars['poli_name'],
		                   cluster=cluster_name,
		                   clustersize=cluster_size,
		                   clusterdef=cluster_description,
		                   name_list=name_list,
		                   plot_script=script1,
		                   plot_div=div1,
		                   plot_resources=plot_resources)
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)



