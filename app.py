from flask import Flask, jsonify, request
from WebScraperAndFormatter import scrape_and_format, csv_generate, json_generate, construct_url
import re


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    req_data = request.get_json() # converts the JSON object into Python data
    # {'form_data': {'location': 'San Francisco', 'num_of_pages': '1', 'category': 'any_category', 'event-type': 'appearance', : 'today'}}
    location = req_data['form_data'["location"]]
    category = req_data['form_data'["category"]]
    event_type = req_data['form_data'['event-type']]
    time_frame = req_data['form_data'['time-frame']]
    num_of_pages = req_data['form_data'["num_of_pages"]]

    form_parameters = list(location, category, event_type, time_frame)

    url = 'https://www.eventbrite.com/d/ca--san-francisco/business--events/' #NOTE: Will replace with constructed url

    urls_to_scrape = generate_urls(form_parameters, num_of_pages)
    
    #TODO: Need to pass in an array of urls to scrape.
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
    app.run(debug=True, port=3000)
