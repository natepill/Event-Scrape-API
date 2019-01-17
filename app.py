from flask import Flask, jsonify, request
from WebScraperAndFormatter import scrape_and_format, csv_generate, json_generate

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    url = 'https://www.eventbrite.com/d/ca--san-francisco/business--events/'
    events = scrape_and_format(url) #zipped object of events
    csv = csv_generate(events, url)
    csv_filename = '{}.csv'.format(url)
    json = json_generate(csv_filename, url)
    return 'SUCCESSFUL DEPLOYMENT'

# @app.route('/csv', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'
#
# @app.route('/json', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'



if __name__ == "__main__":
    app.run(debug=True, port=33507)
