from flask import Flask, render_template, request, redirect

import os
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

testapp = Flask(__name__)

@testapp.route('/')
def redirect_to_index():
    print render_template('test.html')
    return render_template('test.html')

@testapp.route('/test')
def testpage():
    try:
        print render_template('index.html')
        return render_template('index.html')
    except:
        return os.getcwd()

if __name__ == '__main__':
	testapp.run(host='0.0.0.0',debug=True)



