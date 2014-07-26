import sys
import json
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main():

    # Command line arguments (3): 
    #         1. the name of the treasuries input .json file,
    #         2. the name of the listing treasury hash output .json file,
    #         3. the name of the treasury tag hash output .json file.
    # Output: 1. a .json file of a hash from listing id to the ids of all treasuries 
    #            containing that listing, and
    #         2. a .json file of a hash from treasury id to tags

    # Check command line arguments and import the treasuries list
    try:
        treasuries = get_object_from_file(sys.argv[1])
        listing_treasury_hash_file = sys.argv[2]
        treasury_tag_hash_file = sys.argv[3]
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
                 
    # Create the hashes from the treasuries list         
    logging.info("Creating listing-treasury hash.")
    listing_treasury_hash = make_listing_treasury_hash(treasuries)
    
    logging.info("Creating treasury tag hash.")
    treasury_tag_hash = make_treasury_tag_hash(treasuries)
    
    # Save the two hashes in .json format
    logging.info("Saving listing-treasury hash (" + str(len(listing_treasury_hash)) + ") listings.")
    output_json(listing_treasury_hash, listing_treasury_hash_file)
    
    logging.info("Saving treasury tag hash (" + str(len(treasury_tag_hash)) + ") treasuries.")
    output_json(treasury_tag_hash, treasury_tag_hash_file)


def make_treasury_tag_hash(treasuries):

    # Input: a list of treasuries
    # Output: a hash from treasury id to tags
    
	treasury_hash = {}
	for treasury in treasuries:
		treasury_hash[treasury['id']] = treasury['tags']
	return treasury_hash

def make_listing_treasury_hash(treasuries):    
    
    # Input: a list of treasuries
    # Output: a hash from listing id to the ids of treasuries containing that listing
    
    listing_treasury_hash = {}     
    for treasury in treasuries:
    	for listing in treasury['listings']:
    		listing_id = listing['data']['listing_id']
    		if listing_id not in listing_treasury_hash:
    			listing_treasury_hash[listing_id] = [] 
    		listing_treasury_hash[listing_id].append(treasury['id'])
    return listing_treasury_hash
    	
def get_object_from_file(file_name):   

    # Input: the name of a known .json file
    # Output: a python object made from that file's contents
    
    file = open(file_name)
    object = json.load(file)
    return object

def output_json(data, file_name):

    # Input: any object, and an output file_name
    # Output: saves the object in .json format to the specified file_name
    
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)    

if __name__ == '__main__':
    main()