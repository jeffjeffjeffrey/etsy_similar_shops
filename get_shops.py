import sys
import json
import urllib2

KEYSTRING = "<REMOVED>" 

URL_BASE = "https://openapi.etsy.com/v2/"

START = 0
LIMIT = 100
TOTAL = 5000
SAMPLE_SIZE = 300

def main():
    # Get 5000 shops.
    print "Getting shops."
    
    shops = []
    for offset in range(START, START + TOTAL, LIMIT):
        print "Fetching shops " + str(offset + 1) + " - " + str(offset + LIMIT)
        shops += get_shops(LIMIT, offset) 
    
    print "Found " + str(len(shops)) + " shops."
      
    # Select a sample of these shops and get listing data from that sample
    
    shops = shops[:SAMPLE_SIZE]
    
    total_listings = 0
    total_abouts = 0
    total_announcements = 0
    total_connected_users = 0
    total_user_teams = 0
    total_other_team_users = 0
      
    for shop in shops:
        if shop['announcement']:
            total_announcements += 1

    print "Getting listings."
    for shop in shops:
        shop['listings'] = get_listings(shop['shop_id'])
        total_listings += len(shop['listings'])
        
    # Get additional data related to each shop

    print "Getting abouts."
    for shop in shops:
        shop['about'] = get_about(shop['shop_id'])
        if shop['about']:
            total_abouts += 1

    print "Getting user profiles."
    for shop in shops:
        shop['user_profile'] = get_user_profile(shop['user_id'])

    print "Getting connected users."
    for shop in shops:
        shop['connected_users'] = get_connected_users(shop['user_id'])
        if shop['connected_users']:
            total_connected_users += 1

    print "Getting user teams."
    for shop in shops:
        shop['user_teams'] = get_user_teams(shop['user_id'])
        if shop['user_teams']:
            total_user_teams += 1
            print " Getting other users on team."
            for team in shop['user_teams']:
                team['users'] = get_users_for_team(team['group_id'])
                total_other_team_users += 1
                
    print "Total shops: " + str(len(shops))           
    print "Total listings: " + str(total_listings)
    print "Total abouts: " + str(total_abouts)
    print "Total announcements: " + str(total_announcements)
    print "Total connected users: " + str(total_connected_users)
    print "Total user teams: " + str(total_user_teams)
    print "Total other team users: " + str(total_other_team_users)
    
    # Save shop data to a file in json format
    print "Saving outputs."
    output_json(shops, "shops.json")
  
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
            
def get_connected_users(user_id):
    url = (
        URL_BASE 
        + "users/" 
        + str(user_id)
        + "/connected_users?"
        + "&api_key=" + KEYSTRING
    )
    object = get_data_from_api(url)
    if object and object['results']:
        return object['results']
    else:
        return []
            
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
            
def get_users_for_team(team_id):
    url = (
        URL_BASE 
        + "teams/" 
        + str(team_id)
        + "/users?"
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
    
    
    