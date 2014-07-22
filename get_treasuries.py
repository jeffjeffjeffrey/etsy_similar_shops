import sys
import json
import urllib2

KEYSTRING = "<REMOVED>" 

URL_BASE = "https://openapi.etsy.com/v2/"

def main():
    # Get info for 25000 treasuries.
    print "Getting treasuries."
    start = 0
    total = 25005
    limit = 25
    treasuries = []
    for offset in range(start, total, limit):
    	print "Fetching treasuries " + str(offset + 1) + " - " + str(offset + limit)
    	treasuries += get_treasuries(limit, offset) 
    	
    print "There were " + str(len(treasuries)) + " treasuries found."  
 
    # Save shop data to a file in json format
    print "Saving outputs."
    output_json(treasuries, "treasuries.json")
  
def get_treasuries(limit, offset):
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
    try:
        data = urllib2.urlopen(url).readline()
        objects = json.loads(data)
    except:
        e = sys.exc_info()[0]
        print "We had an error (" + str(e) + ") with url " + url + "." 
        objects = None
    return objects
    
def output_json(data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
  
  
  
  
  
  
  
  
  
  