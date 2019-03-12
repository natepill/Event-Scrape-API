from bs4 import BeautifulSoup
import json
from collections import OrderedDict
import requests
import csv
import re
import os

def construct_url(form_parameters):
    '''Need node app to structure request to be sent as an array of parameters'''
    '''Takes in array of parameters and constructs requested url'''

    ## TODO: Array needs to be a set size, or every field must be required or if no answer is given then a null value must be appended to the array

    url = 'https://www.eventbrite.com/d/{}/{}--{}--{}/{}'.format(form_parameters[0], form_parameters[1],form_parameters[2],form_parameters[3],form_parameters[4],form_parameters[5])
    # https://www.eventbrite.com/d/{location}/{category}--{event-type}--{date}/{page-number}
    return url


def scrape_and_format(url):
    """Returns a zip object containing all scraped and formatted event details"""

    source = requests.get(str(url)).text #grabs text (html) from response object
    #example url: https://www.eventbrite.com/d/ca--san-francisco/business--events/
    soup = BeautifulSoup(source, 'lxml')


    unordered_list_tag = soup.find('ul', class_='search-main-content__events-list') #find the list of all event <li> tags
    list_of_events = unordered_list_tag.find_all('li')

    #Containers for scraped data
    event_titles = list()
    locations = list()
    dates = list()
    prices = list()

    #iterate through each <li> tag and find append data if found
    for event in list_of_events:

        try:
            event_titles.append(event.find('div', class_='event-card__formatted-name--is-clamped').text)
        except:
            event_titles.append(None)

        try:
            dates.append(event.find('div', class_='eds-text-bs--fixed eds-text-color--grey-600 eds-l-mar-top-1').text)
        except:
            dates.append(None)

        try:
            locations.append(event.find('div', class_='card-text--truncated__one').text)
        except:
            locations.append(None)

        try:
            prices.append(event.find_all('div', class_='eds-text-bs--fixed eds-text-color--grey-600 eds-l-mar-top-1'))
        except:
            prices.append('0')


    date_pattern = re.compile(r'\w\w\w, \w\w\w [0-9]?\d')
    location_pattern = re.compile(r'[A-Z]{2}$')
    price_pattern = re.compile(r'^Starts')
    price_pattern2 = re.compile(r'^Free')


    price_text = list()
    for items in prices:
        for price in items:
            price_text.append(price.text)

    print(price_text)
    all_prices = list()

    #Fill in the empty spaces in the event prices event_data
    for index, detail in enumerate(price_text):

        if re.match(price_pattern, detail) is not None or re.match(price_pattern2, detail) is not None:
            all_prices.append(detail)

        if (index+1 > len(price_text)-1):
            # IF NOT WORKING: try expect function to return 1 or 0 for the incrementor value
            break

        elif (detail == '' and price_text[index+1] == ''):
            all_prices.append(detail)

    ## TODO: Clean price data by only having numerical values or empty strings
    # price_pattern3 = re.compile(r'\d+')
    # def clean_prices(list_of_prices):
    #     for price in list_of_prices:
    #         if re.split(price_pattern3, price)


    # print(all_prices)
    # print(index)
    # print(len(price_text))

    # print(len(all_prices))
    # print(len(event_titles))
    # print(len(locations))
    # print(len(dates))

    all_events = zip(event_titles, locations, dates, all_prices) #create an iterator of tuples with each event information
    return all_events

def csv_generate(all_events, url):
    '''Writes data from zipped object to a csv file, reads new csv file and returns an array of the csv '''

    # csv_file = open(filename, 'w') #need to make filename creation dynamic
    url = url.replace('/', '-') #Prevents the file name being interpreted as having multiple directories due to "/"'s in the URL
    filename_pattern = re.compile('www.*')

    url = re.search(filename_pattern, url).group(0)
    print('This is url:', url)

    filename = '{}.csv'.format(str(url))

    # dirname = os.path.dirname(filename)
    # if not os.path.exists(dirname):
    #     os.makedirs(dirname)


    with open(os.path.join('event_csv', filename), 'w') as csv_file:


        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['title', 'location', 'date', 'time', 'price'])



        # Parsing for time and date AND writing to csv
        for event in all_events:
            time_pattern = re.compile(r'\d:\d\d\w\w')
            date_pattern = re.compile(r'\w\w\w, \w\w\w \d\d')

            title = event[0]
            location = event[1]
            date_object = date_pattern.finditer(event[2])
            # date = re.match(date_pattern, event[2]).group(0)
            # time = re.match(time_pattern, event[2]).group(0)
            for date_item in date_object:
                date = date_item[0]
            time_object = time_pattern.finditer(event[2])
            for time_item in time_object:
                time = time_item[0]

            price = event[3]

            csv_writer.writerow([title, location, date, time, price])



    csv_array = list()
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            csv_array.append(row)
    return csv_array

    # Example of event with no price found
    # ('DeveloperWeek 2019 Hiring Expo', 'SF Bay Area | Oakland Convention Center, Oakland, CA', 'Wed, Feb 20,
    #  5:00pm', '')

def json_generate(csv_filename, url):
    """Convert Generated CSV file to a JSON Array """

    fieldnames = ('title', 'location', 'date', 'time', 'price')
    entries = []



    with open(os.path.join('event_csv', csv_filename), 'r') as csv_file:
        #python's standard dict is not guaranteeing any order,
        #but if you write into an OrderedDict, order of write operations will be kept in output.
        reader = csv.DictReader(csv_file, fieldnames)
        for row in reader:
            entry = OrderedDict()
            for field in fieldnames:
                entry[field] = row[field]
            entries.append(entry)

    output = {
        "Events": entries
    }


    with open(os.path.join('event_json', '{}.json'.format(url)), 'w') as jsonfile:
        json.dump(output, jsonfile)
        jsonfile.write('\n')

    return output
