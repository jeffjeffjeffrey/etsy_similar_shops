import sys
import json

def main():
    treasuries = get_object_from_file(sys.argv[1])
    
    print "Creating treasury tag hash."
    treasury_tag_hash = make_treasury_tag_hash(treasuries)
    
    print "Creating listing-treasury hash."
    listing_treasury_hash = make_listing_treasury_hash(treasuries)
    
    print "Saving treasury tag hash (" + str(len(treasury_tag_hash)) + ") treasuries."
    output_json(treasury_tag_hash, "treasury_tag_hash.json")
    
    print "Saving listing-treasury hash."
    output_json(listing_treasury_hash, "listing_treasury_hash.json")

def make_treasury_tag_hash(treasuries):
	treasury_hash = {}
	for treasury in treasuries:
		treasury_hash[treasury['id']] = treasury['tags']
	return treasury_hash

def make_listing_treasury_hash(treasuries):    
    listing_treasury_hash = {}     
    for treasury in treasuries:
    	for listing in treasury['listings']:
    		listing_id = listing['data']['listing_id']
    		if listing_id in listing_treasury_hash:
    			listing_treasury_hash[listing_id].append(treasury['id'])
    		else:
    			listing_treasury_hash[listing_id] = [treasury['id']] 
    return listing_treasury_hash
    	
 
def get_object_from_file(file_name):   
    file = open(file_name)
    object = json.load(file)
    return object

def output_json(data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)    

if __name__ == '__main__':
    main()