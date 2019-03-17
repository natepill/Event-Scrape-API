from bs4 import BeautifulSoup
import json
from collections import OrderedDict
import requests
import csv
import re
import os

# NOTE: Number of pages to scrape needed to be a seperate parameter because we need to call the function multiple times with a different value for that parameter
def construct_url(form_parameters, page_number):
    '''Need node app to structure request to be sent as an array of parameters'''
    '''Takes in array of parameters and constructs requested url'''
    # NOTE:form_parameters = list(location, category, event_type, time_frame)
    # NOTE: IF we allow tags in the form, then we are going to have to add a conditional in this function that checks to see if they were passed through. If they were, then there is a different process to construct the url

    # TODO: Every field must be required or if no answer is given then a null value must be appended to the array
    url = 'https://www.eventbrite.com/d/{}/{}--{}--{}/{}'.format(form_parameters[0], form_parameters[1],form_parameters[2],form_parameters[3], page_number)
    # https://www.eventbrite.com/d/{location}/{category}--{event-type}--{date}/{page-number}
    #example url: https://www.eventbrite.com/d/ca--san-francisco/business--events/
    # TODO Strech Challenge: Accomodate Event tags in constructed url

    return url

def generate_urls(form_parameters, num_of_pages):
    '''Generate a list of urls to scrape based on the number of pages to paginate through'''


    list_of_urls = list()
    for page_number in range(num_of_pages):
        list_of_urls.append(construct_url(form_parameters, page_number))

    return list_of_urls

def clean_url(url):
    '''Removes characters that would mess up how we save a file. We use the url as part of the filename'''
    url = url.replace('/', '-') #Prevents the file name being interpreted as having multiple directories due to "/"'s in the URL
    filename_pattern = re.compile('www.*')
    url = re.search(filename_pattern, url).group(0)
    return url

def scrape_and_format(urls):
    # TODO: Instead of one url, it needs to take in a list of urls

    # TODO needs to return a list of zipped objects containing all scraped and formatted event details
    """Returns a zip object containing all scraped and formatted event details"""

    scraped_pages = list() #list of zipped objects. Each object is data from each page/url that was passed through the urls list
    for url in urls:
        source = requests.get(str(url)).text #grabs text (html) from response object
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


        all_events = zip(event_titles, locations, dates, all_prices) #create an iterator of tuples with each event information

        scraped_pages.append(all_events)

    return scraped_pages

def csv_generate(all_events, urls):
    '''Writes data from zipped object to a csv file, reads new csv file and returns an array of the csv '''

#TODO: Need to refactorto accomodate iterating over a list of all_events AND list of urls
#NOTE: Need to ensure that we are writing the correct data to the appropriate files, no empty objects
#NOTE: Should I Zip all_events and urls so that I just iterate over each index?
    zipped_page_results = zip(all_events, urls)

    for zipped_page in zipped_page_results:
        # csv_file = open(filename, 'w') #need to make filename creation dynamic
        url = clean_url(zipped_page[1])
        # zipped_page[1] = url.replace('/', '-') #Prevents the file name being interpreted as having multiple directories due to "/"'s in the URL
        # filename_pattern = re.compile('www.*')
        # zipped_page[1] = re.search(filename_pattern, zipped_page[1]).group(0)

        print('This is url:', url)

        filename = '{}.csv'.format(str(url))

        # dirname = os.path.dirname(filename)
        # if not os.path.exists(dirname):
        #     os.makedirs(dirname)


        with open(os.path.join('event_csv', filename), 'w') as csv_file:


            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['title', 'location', 'date', 'time', 'price'])



            # Parsing for time and date AND writing to csv
            for event in zipped_page[0]:
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



# NOTE: Not sure as to why I'm reading and return the csv file that I've already written to?
# NOTE: This is not currently being utilized in the app, but if its needed, then I need to refactor it to accomodate lists of objects

        # csv_array = list()
        # with open(filename, 'r') as file:
        #     reader = csv.reader(file)
        #     for row in reader:
        #         csv_array.append(row)
        # return csv_array

    return

        # Example of event with no price found
        # ('DeveloperWeek 2019 Hiring Expo', 'SF Bay Area | Oakland Convention Center, Oakland, CA', 'Wed, Feb 20,
        #  5:00pm', '')

def json_generate(csv_filename, url, page_number):
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

    # TODO: Access keys by url's page number instead of "Events" because we can have multiple keys due to scraping through pagination
    # NOTE: Need to look back to see wheter this method changes how we are saving/referencing values in our CSV file
    event_results_by_page = {
        "Page_{}".format(page_number): entries
    }


    with open(os.path.join('event_json', '{}.json'.format(url)), 'w') as jsonfile:
        json.dump(event_results_by_page, jsonfile)
        jsonfile.write('\n')

    return event_results_by_page
