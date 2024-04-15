from flask import Flask, render_template, request
from utils import search


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		raw_text = request.form['rawtext']
		results = search(raw_text)
		return render_template("results.html", results=results, raw_text=raw_text)
	else:
		return render_template("index.html")
@app.route('/home', methods=['GET', 'POST'])
def indexhome():
	return render_template("index.html")

@app.route('/results', methods=['GET', 'POST'])
def Home():
	if request.method == 'POST':
		raw_text = request.form['rawtext']
		results = search(raw_text)
		return render_template("results.html", results=results, raw_text=raw_text)
	else:
		return render_template("index.html")
if __name__ == '__main__':
	 app.run(debug= True, threaded=True)	