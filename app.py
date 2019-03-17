from flask import Flask, jsonify, request
from WebScraperAndFormatter import scrape_and_format, csv_generate, json_generate, construct_url, clean_url, generate_urls
import re

# TODO: I may want to have the index route ONLY write the data to csv and json files
# TODO: May need '/csv' and '/json' routes in order to be utilized as a developer API
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    req_data = request.get_json() # converts the JSON object into Python data
    # {'form_data': {'location': 'San Francisco', 'num_of_pages': '1', 'category': 'any_category', 'event-type': 'appearance', : 'today'}}
    location = req_data['form_data']["location"]
    category = req_data['form_data']["category"]
    event_type = req_data['form_data']['event-type']
    time_frame = req_data['form_data']['time-frame']
    num_of_pages = int(req_data['form_data']["num_of_pages"])

    # location = req_data["location"]
    # category = req_data["category"]
    # event_type = req_data['event-type']
    # time_frame = req_data['time-frame']
    # num_of_pages = int(req_data["num_of_pages"])

    form_parameters = [location, category, event_type, time_frame]

    # url = 'https://www.eventbrite.com/d/ca--san-francisco/business--events/' #NOTE: Will replace with constructed url

    urls_to_scrape = generate_urls(form_parameters, num_of_pages) #List of urls that were scraped

    events = scrape_and_format(urls_to_scrape) #list of zipped objects of events

    csv_generate(events, urls_to_scrape) #Write to csv files

    list_of_json = list()

    #NOTE: There are a couple ways to go about passing in page numbers:
        # 1. If I enumerate over urls_to_scrape, then (index + 1) is equivalent to the page number I'm trying to pass in because each scraped url is one page
        # 2. Iterate over a range of num_of_pages
    for index, url in enumerate(urls_to_scrape):
        url = clean_url(url)
        csv_filename = '{}.csv'.format(url)
        csv_to_json = json_generate(csv_filename, url, index+1)
        list_of_json.append(csv_to_json)

    return jsonify(list_of_json)

# @app.route('/csv', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'
#
# @app.route('/json', methods=['GET'])
# def index():
#     return 'SUCCESSFUL DEPLOYMENT'



if __name__ == "__main__":
    app.run(debug=True, port=3000)
