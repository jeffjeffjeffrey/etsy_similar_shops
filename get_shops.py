import sys
import json
import urllib2
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

KEYSTRING = "<REMOVED>" 
URL_BASE = "https://openapi.etsy.com/v2/"

def main():

    # Command line arguments (3): 
    #         1. the total number of shops to download,
    #         2. the size of the sample of these shops to get additional data for,
    #         3. the name of the output .json file.
    # Output: a .json file of an array of shops augmented by additional data

    # Check command line arguments    
    try:
        total = (int)(sys.argv[1])
        sample_size = (int)(sys.argv[2])
        output_file = sys.argv[3]
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
 
    # Fetch the initial set of shops, batched by 100       
    logging.info("Getting shops.")    
    shops = []
    for offset in range(0, total, 100):
        limit = min(total - offset, 100)
        logging.info("Fetching shops " + str(offset + 1) + " - " + str(offset + limit))
        shops += get_shops(limit, offset) 
          
    # Select a sample of these shops and get associated data from that sample  
    logging.info("Taking a sample of " + str(min(sample_size, total)) + " shops.") 
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

    logging.info("Getting listings.")
    for shop in shops:
        shop['listings'] = get_listings(shop['shop_id'])
        total_listings += len(shop['listings'])
        
    # Get additional data related to each shop

    logging.info("Getting abouts.")
    for shop in shops:
        shop['about'] = get_about(shop['shop_id'])
        if shop['about']:
            total_abouts += 1

    logging.info("Getting user profiles.")
    for shop in shops:
        shop['user_profile'] = get_user_profile(shop['user_id'])

    logging.info("Getting user teams.")
    for shop in shops:
        shop['user_teams'] = get_user_teams(shop['user_id'])
                
    logging.info("Total shops: " + str(len(shops)))           
    logging.info("Total listings: " + str(total_listings))
    logging.info("Total abouts: " + str(total_abouts))
    logging.info("Total announcements: " + str(total_announcements))
    logging.info("Total user teams: " + str(total_user_teams))
    
    # Save shop data to a file in .json format
    logging.info("Saving outputs to " + output_file + ".")
    output_json(shops, output_file)
  
def get_shops(limit, offset):
    
    # Inputs: limit = the number of shops to download,
    #         offset = the starting index of shops to fetch
    # Output: A list of shops, from the Etsy API
    
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

    # Input: a shop_id
    # Output: A list of listings from that shop, from the Etsy API
    
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

    # Input: a shop_id
    # Output: the ShopAbout object, if it exists, for that shop, from the Etsy API
    # Note: This method throws errors whenever the ShopAbout section does not exist.
    #       I'm not sure how to avoid this.
    
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

    # Input: a user_id
    # Output: a UserProfile object, if it exists, for this user, from the Etsy API
    
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

    # Input: a user_id
    # Output: A list of Team objects that the user belongs to, from the Etsy API
    
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
    
    
    