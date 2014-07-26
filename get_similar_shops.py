import sys
import json
import math
import re
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

def main():

    print_details = False
    try:
        if len(sys.argv) > 1:
            shops = get_object_from_json(sys.argv[1])
            listing_treasury_hash = {}
            treasury_tag_hash = {}
        if len(sys.argv) > 3:
            listing_treasury_hash = get_object_from_json(sys.argv[2])
            treasury_tag_hash = get_object_from_json(sys.argv[3])
            logging.debug("Treasury tag hash found with " + str(len(treasury_tag_hash)) + " treasuries.")
            logging.debug("Listing treasury hash found with " + str(len(listing_treasury_hash)) + " listings.")
        if len(sys.argv) == 5 and sys.argv[4] == "details":            
            print_details = True
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
           
    # Collect the terms from each shop
    all_terms = []

    for shop in shops:
        terms = [] 
        terms += get_listing_terms(shop['listings'])
        terms += get_user_profile_terms(shop['user_profile'])
        terms += get_misc_terms(shop)
        terms += get_treasury_terms(shop['listings'], listing_treasury_hash, treasury_tag_hash)
        
        shop['term_counts'] = get_term_counts(clean_terms(terms))
        all_terms += shop['term_counts'].keys()
        
    # Calculate the number of shops that use each term      
    term_shop_counts = get_term_counts(all_terms)
                
    # Calculate the tf-idf weight for the terms in each shop
    for shop in shops:
        shop['term_weights'] = get_term_weights(
            shop['term_counts'], 
            term_shop_counts, 
            len(shops)
        )
    
    # Calculate five most similar shops to each shop
    for primary_shop in shops:          
        similar_shops = []
        for other_shop in shops:
            similarity = cosine_similarity(
                primary_shop['term_weights'], 
                other_shop['term_weights']
            )
            if similarity > 0:
                similar_shops.append((other_shop, similarity))
        similar_shops = sorted(similar_shops, key=lambda entry: -1 * entry[1]) 
        if print_details: 
            print_similar_shop_details(primary_shop, similar_shops[1:6]) 
        else:
            print_similar_shops(primary_shop, similar_shops[1:6])     

    return 0
    
def print_similar_shop_details(primary_shop, similar_shops):
    print primary_shop['shop_name'],
    print_top_terms(primary_shop['term_weights'])
    if len(similar_shops) <= 1:
        print "<No similar shops were found!>"
    else:
        i = 1
        for similar_shop in similar_shops:            
            print str(i) + ". " + str(similar_shop[1]) + " " + similar_shop[0]['shop_name'],
            print_top_terms(similar_shop[0]['term_weights'])
            i += 1
            
def print_similar_shops(primary_shop, similar_shops):
    print primary_shop['shop_name'] + ":",
    if len(similar_shops) <= 1:
        print "<No similar shops were found!>"
    else:
        for similar_shop in similar_shops[:-1]:
            print similar_shop[0]['shop_name'] + ",",
        print similar_shops[-1][0]['shop_name']

                    
def print_top_terms(term_weights):
    pairs = []
    for term in term_weights:
        pairs.append((term, term_weights[term]))
    pairs = sorted(pairs, key=lambda entry: -1 * entry[1])
    for pair in pairs[:5]:
        print " (" + pair[0] + " " + str(math.trunc(pair[1]*100)/100.0) + ")",
    print ""

def get_listing_terms(listings):
    terms = []
    for listing in listings:
        if listing['tags']:
            terms += listing['tags']
        if listing['materials']:
            terms += listing['materials']
        if listing['category_path']:
            terms += listing['category_path']
        if listing['style']:
            terms += listing['style']
        if listing['title']:
            terms += listing['title'].split()
        if listing['description']:
            terms += listing['description'].split()
        if listing['who_made']:
            terms.append(listing['who_made'].replace('_', ''))
        if listing['when_made']:
            terms.append(listing['when_made'].replace('_', ''))
        if listing['recipient']:
            terms.append(listing['recipient'].replace('_', ''))
        if listing['occasion']:
            terms.append(listing['occasion'].replace('_', ''))   
    return terms
    
def get_user_profile_terms(user_profile):
    terms = []
    if user_profile['country_id']:
        terms.append("countryid" + str(user_profile['country_id']))
    if user_profile['region']:
        terms.append(user_profile['region'])
    if user_profile['city']:
        terms.append(user_profile['city'])
    if user_profile['materials']:
        materials = user_profile['materials'].split('.')
        for material in materials:
            terms.append(material.replace('_', ' '))
    return terms

def get_misc_terms(shop):
    terms = []
    if shop['announcement']:
        terms += shop['announcement'].split()
    if shop['about']:
        terms += shop['about']['story_headline'].split()
        terms += shop['about']['story_leading_paragraph'].split()
        terms += shop['about']['story'].split()
    for team in shop['user_teams']:
        terms += team['tags']
    return terms
    
def get_treasury_terms(listings, listing_treasury_hash, tresury_tag_hash):
    terms = []
    total = 0
    for listing in listings:
        if str(listing['listing_id']) in listing_treasury_hash:
            total += 1
            terms += treasury_tag_hash[str(listing['listing_id'])]
    if total > 0:
        logger.debug("Shop found with " + str(total) + " treasuried listing(s).")
    return terms
	
def get_term_counts(terms):
    term_counts = {}
    if not terms:
        return term_counts
    for term in terms:
        if term not in term_counts:
            term_counts[term] = 0
        term_counts[term] += 1
    return term_counts

def clean_terms(terms):
    cleaned = []
    for term in terms:
        stems = re.sub('[^0-9a-zA-Z]+', ' ', term).lower().strip().split()
        for stem in stems:
            cleaned.append(stem)
    return cleaned

def get_term_weights(term_counts, term_shop_counts, num_shops):
    weights = {}
    max_count = 1
    for term in term_counts:
        max_count = max(max_count, term_counts[term])
    for term in term_counts:
        normalized_count = 0.5 + 0.5 * term_counts[term] / max_count
        weights[term] = normalized_count * math.log(float(num_shops) / term_shop_counts[term])
    return weights
    
def cosine_similarity(weights_1, weights_2):
    if not weights_1 or not weights_2:
        return 0.0
    intersection = set(weights_1.keys()) & set(weights_2.keys())
    numerator = sum([weights_1[term] * weights_2[term] for term in intersection])

    sum_1 = sum([weights_1[term]**2 for term in weights_1.keys()])
    sum_2 = sum([weights_2[term]**2 for term in weights_2.keys()])
    denominator = math.sqrt(sum_1) * math.sqrt(sum_2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator
        	
def get_object_from_json(file_name):
    file = open(file_name)
    object = json.load(file)
    return object

if __name__ == '__main__':
    main()








