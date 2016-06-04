from flask import Flask, jsonify, response


app = Flask('mind-me', static_url_path='')


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')

@app.route('/oauth2_callback')
def oauth_redirect():
	content = response.content
	import pdb; pdb.set_trace()
	return jsonify(status='ok', response=response.content)

@app.route('/calendar')
def authenticate():
	from calendar.oauth2 import connect_calendar
	connect_calendar()



if __name__ == '__main__':
    app.run(debug=True)
