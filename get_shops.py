import sys
import json
import urllib2
import logging

KEYSTRING = "<REMOVED>" 


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)



URL_BASE = "https://openapi.etsy.com/v2/"

def main():

    try:
        total = (int)(sys.argv[1])
        sample_size = (int)(sys.argv[2])
        output_file = sys.argv[3]
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
        
    logging.debug("Getting shops.")
    
    shops = []
    limit = min(100, total)
    for offset in range(0, total, min(total, limit)):
        logging.debug("Fetching shops " + str(offset + 1) + " - " + str(offset + limit))
        shops += get_shops(limit, offset) 
          
    # Select a sample of these shops and get listing data from that sample
    
    shops = shops[:sample_size]
    
    total_listings = 0
    total_abouts = 0
    total_announcements = 0
    total_connected_users = 0
    total_user_teams = 0
    total_other_team_users = 0
      
    for shop in shops:
        if shop['announcement']:
            total_announcements += 1

    logging.debug("Getting listings.")
    for shop in shops:
        shop['listings'] = get_listings(shop['shop_id'])
        total_listings += len(shop['listings'])
        
    # Get additional data related to each shop

    logging.debug("Getting abouts.")
    for shop in shops:
        shop['about'] = get_about(shop['shop_id'])
        if shop['about']:
            total_abouts += 1

    logging.debug("Getting user profiles.")
    for shop in shops:
        shop['user_profile'] = get_user_profile(shop['user_id'])

    logging.debug("Getting user teams.")
    for shop in shops:
        shop['user_teams'] = get_user_teams(shop['user_id'])
                
    logging.debug("Total shops: " + str(len(shops)))           
    logging.debug("Total listings: " + str(total_listings))
    logging.debug("Total abouts: " + str(total_abouts))
    logging.debug("Total announcements: " + str(total_announcements))
    logging.debug("Total user teams: " + str(total_user_teams))
    
    # Save shop data to a file in json format
    logging.debug("Saving outputs to " + output_file + ".")
    output_json(shops, output_file)
  
def get_shops(limit, offset):
    url = (
        URL_BASE 
        + "shops?"
        + "&limit=" + str(limit)
        + "&offset=" + str(offset)
        + "&api_key=" + KEYSTRING
    ) 
    object = get_data_from_api(url)
    if object and object['results']:
        return object['results']
    else:
        return []
        
def get_listings(shop_id):
    url = (
        URL_BASE 
        + "shops/" 
        + str(shop_id)
        + "/listings/active?"
        + "&api_key=" + KEYSTRING
    )
    object = get_data_from_api(url)
    if object and object['results']:
        return object['results']
    else:
        return []    

def get_about(shop_id):
    url = (
        URL_BASE 
        + "shops/" 
        + str(shop_id)
        + "/about?"
        + "&api_key=" + KEYSTRING
    )
    object = get_data_from_api(url)
    if object and object['results'] and len(object['results']) > 0:
        return object['results'][0]
    else:
        return None

def get_user_profile(user_id):
    url = (
        URL_BASE 
        + "users/" 
        + str(user_id)
        + "/profile?"
        + "&api_key=" + KEYSTRING
    )
    object = get_data_from_api(url)
    if object and object['results'] and len(object['results']) > 0:
        return object['results'][0]
    else:
        return None
            
def get_user_teams(user_id):
    url = (
        URL_BASE 
        + "users/" 
        + str(user_id)
        + "/teams?"
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
        logging.error("We had an error (" + str(e) + ") with url " + url + ".")
        objects = None
    return objects
    
def output_json(data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
    
    
    