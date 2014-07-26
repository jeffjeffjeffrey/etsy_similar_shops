import sys
import json
import urllib2
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

KEYSTRING = "<REMOVED>" 
URL_BASE = "https://openapi.etsy.com/v2/"

def main():

    # Command line arguments (2): 
    #         1. the total number of treasuries to download,
    #         2. the name of the output .json file.
    # Output: a .json file of an array of treasuries
    
    # Check command line arguments
    try:
        total = (int)(sys.argv[1])
        output_file = sys.argv[2]
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
        
    # Fetch treasuries from API, 25 at a time
    logging.info("Getting treasuries.")
    treasuries = []
    for offset in range(0, total, 25):
    	limit = min(total - offset, 25)
    	logging.info("Fetching treasuries " + str(offset + 1) + " - " + str(offset + limit))
    	treasuries += get_treasuries(limit, offset)   	
    logging.info("There were " + str(len(treasuries)) + " treasuries found.")
 
    # Save treasuries to output_file in json format    
    logging.info("Saving outputs to " + output_file + ".")
    output_json(treasuries, output_file)
  
def get_treasuries(limit, offset):
	
	# Inputs: limit = the number of treasuries to download,
    #         offset = the starting index of treasuries to fetch
    # Output: A list of treasuries, from the Etsy API
     
    url = (
        URL_BASE 
        + "treasuries?"
        + "&limit=" + str(limit)
        + "&offset=" + str(offset)
        + "&api_key=" + KEYSTRING
    ) 
    object = get_data_from_api(url)
    if object and object['results']:
        return object['results']
    else:
        return []

def get_data_from_api(url):

    # Input: a url
    # Output: the .json objects found at that url
    
    try:
        data = urllib2.urlopen(url).readline()
        objects = json.loads(data)
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error (" + str(e) + ") with url " + url + ".")
        objects = None
    return objects
    
def output_json(data, file_name):

    # Input: any object, and an output file_name
    # Output: saves the object in .json format to the specified file_name
    
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
  
  
  
  
  
  
  
  
  
  