from flask import Flask, jsonify, request
from WebScraperAndFormatter import scrape_and_format, csv_generate, json_generate, construct_url
import re


app = Flask(__name__)

@app.route('/')
def index():
    url = 'https://www.eventbrite.com/d/ca--san-francisco/business--events/'
    events = scrape_and_format(url) #zipped object of events
    csv = csv_generate(events, url)

    url = url.replace('/', '-') #Prevents the file name being interpreted as having multiple directories due to "/"'s in the URL
    filename_pattern = re.compile('www.*')
    url = re.search(filename_pattern, url).group(0)

    csv_filename = '{}.csv'.format(url)
    csv_to_json = json_generate(csv_filename, url)
    return jsonify(csv_to_json)

# @app.route('/csv', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'
#
# @app.route('/json', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'



if __name__ == "__main__":
    app.run(debug=True)
