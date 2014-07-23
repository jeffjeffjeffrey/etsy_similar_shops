import sys
import json
import math
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter

similarity_weights = {}
similarity_weights['tags'] = 10
similarity_weights['secondary'] = 1
similarity_weights['default'] = 5

def main():
    if len(sys.argv) > 0:
        shops = get_object_from_json(sys.argv[1])
    if len(sys.argv) == 4:
        listing_treasury_hash = get_object_from_json(sys.argv[3])
        treasury_tag_hash = get_object_from_json(sys.argv[2])
        print "Treasury tag hash found with " + str(len(treasury_tag_hash)) + " treasuries."
        print "Listing treasury hash found with " + str(len(listing_treasury_hash)) + " listings."

    # Calculate the term counts in each shop, grouped by term type
    for shop in shops:
        term_counts = {}
        
        term_counts_by_type['tags'] = get_term_counts(
            get_tag_terms(shop) + 
            get_treasury_terms(shop['listings'], listing_treasury_hash, treasury_tag_hash), 
            True
        )
        
        # for prose section, we'll make a separate object for each language
        terms_by_language = get_prose_terms(shop)
        for language in terms_by_language:
            make_stem = (language == 'language=en-US')
            term_counts_by_type[language] = get_term_counts(terms_by_language[language], make_stem)
        
        term_counts_by_type['secondary'] = get_term_counts(
            get_enum_terms(shop['listings']) +
            get_location_terms(shop['user_profile']) +
            get_connection_terms(shop) +
            get_group_terms(shop),
            False
        )

        shop['term_counts_by_type'] = term_counts_by_type
           
    # Calculate the number of shops that use each term 
    all_terms_by_type = {}
    for shop in shops:
        for term_type in shop['term_counts_by_type']:
            if term_type not in all_terms_by_type:
                all_terms_by_type[term_type] = []
            all_terms_by_type[term_type] += shop['term_counts_by_type'][term_type].keys()
    term_shop_counts_by_type = {}
    for term_type in all_terms_by_type:
        term_shop_counts_by_type[term_type] = get_term_counts(all_terms_by_type[term_type], False)
                
    # Calculate the tf-idf weight for the terms in each shop
    for shop in shops:
        shop['term_weights_by_type'] = {}
        for term_type in shop['term_counts_by_type']:
            shop['term_weights_by_type'][term_type] = get_term_weights(
                shop['term_counts_by_type'][term_type], 
                term_shop_counts_by_type[term_type], 
                len(shops)
            )

    for shop in shops:
        print "Shop " + str(shop['shop_id']) + " " + shop['shop_name'] + " (user " + str(shop['user_id']) + ")"
        for term_type in shop['term_counts_by_type']:
            print " Term type: " + term_type
            for term in shop['term_counts_by_type'][term_type]:
                print "  Term " + term + ": " + str(shop['term_counts_by_type'][term_type][term]) + " - " + str(term_shop_counts_by_type[term_type][term]) + " - " + str(shop['term_weights_by_type'][term_type][term])
    
    # Calculate five most similar shops to each shop
    for primary_shop in shops:
        print "Shop " + primary_shop['shop_name']
        similar_shops_by_term_type = {}
        similar_shops = []
        for other_shop in shops:
            total_similarity = 0.0
            for term_type in term_shop_counts_by_type:
                if term_type not in similar_shops_by_term_type:
                    similar_shops_by_term_type[term_type] = []
                if term_type in primary_shop['term_weights_by_type'] and term_type in other_shop['term_weights_by_type']:
                    similarity = cosine_similarity(primary_shop['term_weights_by_type'][term_type], other_shop['term_weights_by_type'][term_type])
                    if similarity > 0.00001:
                        if term_type in similarity_weights:
                            total_similarity += similarity * similarity_weights[term_type]
                        else:
                            total_similarity += similarity * similarity_weights['default']   
                        shop_and_similarity = (other_shop, similarity)
                        similar_shops_by_term_type[term_type].append(shop_and_similarity)
            if total_similarity > 0.00001:
                shop_and_total_similarity = (other_shop, total_similarity)
                similar_shops.append(shop_and_total_similarity)
        similar_shops = sorted(similar_shops, key=lambda entry: -1 * entry[1])
        print " Total similarity:"
        for total_similar_shop in similar_shops[1:11]:
            print "  " + str(total_similar_shop[1]) + " " + total_similar_shop[0]['shop_name']
        for term_type in shop['term_counts_by_type']:
            #if term_type in similarity_weights and similarity_weights[term_type] == 0:
            #    continue
            print " Similarity by " + term_type + ":"
            similar_shops_by_term_type[term_type] = sorted(similar_shops_by_term_type[term_type], key=lambda entry: -1 * entry[1])
            for similar_shop in similar_shops_by_term_type[term_type][1:11]:
                print "  " + str(similar_shop[1]) + " " + similar_shop[0]['shop_name']
    return 0

def get_tag_terms(shop):
    terms = []
    for listing in shop['listings']:
        terms += listing['tags'] + listing['materials'] + listing['category_path'] + listing['style'] + listing['title'].split()
    if shop['user_profile']['materials']:
        user_materials = shop['user_profile']['materials'].split('.')
        for material in user_materials:
            material = material.replace('_', ' ')
        terms += user_materials
    for team in shop['user_teams']:
        terms += team['tags']
    # treasury tags
    return terms

# for prose section, we'll make a separate object for each language
def get_prose_terms(shop):
    terms_by_language = {}
    for listing in shop['listings']:
        # get the language of the listing
        listing_language = "language=" + listing['language']
        if listing_language not in terms_by_language:
            terms_by_language[listing_language] = []
        terms_by_language[listing_language] += listing['description'].split()

    # get the first listed language of the shop
    shop_language = "language=" + shop['languages'][0]
    if shop_language not in terms_by_language:   
        terms_by_language[shop_language] = []     
    if shop['announcement']:
        terms_by_language[shop_language] += shop['announcement'].split()
    if shop['about']:
        terms_by_language[shop_language] += shop['about']['story_headline'].split()
        terms_by_language[shop_language] += shop['about']['story_leading_paragraph'].split()
        terms_by_language[shop_language] += shop['about']['story'].split()
    return terms_by_language

def get_enum_terms(listings):
    terms = []
    for listing in listings:
        if listing['who_made']:
            terms.append("who_made=" + listing['who_made'])
        if listing['when_made']:
            terms.append("when_made=" + listing['when_made'])
        if listing['recipient']:
            terms.append("recipient=" + listing['recipient'])
        if listing['occasion']:
            terms.append("occasion=" + listing['occasion'])    
    return terms    

def get_location_terms(user_profile):
    terms = []
    if user_profile['country_id']:
        terms.append("country_id=" + str(user_profile['country_id']))
    if user_profile['region']:
        terms.append("region=" + user_profile['region'])
    if user_profile['city']:
        terms.append("city=" + user_profile['city'])
    return terms

def get_connection_terms(shop):
    terms = [str(shop['user_id'])]
    for connection in shop['connected_users']:
        terms.append(str(connection['user_id']))
    for team in shop['user_teams']:
        for user in team['users']:
            if user['user_id'] != shop['user_id']:
                terms.append(str(user['user_id']))
    return terms

def get_group_terms(shop):
    terms = []
    for team in shop['user_teams']:
        terms.append(str(team['group_id']))
    # treasury names
    return terms
    
def get_treasury_terms(listings, listing_treasury_hash, tresury_tag_hash):
    terms = []
    total = 0
    for listing in listings:
        if str(listing['listing_id']) in listing_treasury_hash:
            total += 1
            terms += treasury_tag_hash[str(listing['listing_id'])]
    if total > 0:
        print "Shop found with " + str(total) + " treasuried listing(s)."
    return terms
	
def normalize_counts(term_counts):   
    max_count = 1
    for term in term_counts:
        max_count = max(max_count, term_counts[term])
    for term in term_counts.keys():
        term_counts[term] = 0.5 + 0.5 * term_counts[term] / max_count
    return term_counts
	
def get_term_counts(terms, make_stem):
    term_counts = {}
    if not terms:
        return term_counts
    lmtzr = WordNetLemmatizer()
    for term in terms:
        stem = term.lower()
        if make_stem:
            stem = lmtzr.lemmatize(stem)
        if stem not in term_counts:
            term_counts[stem] = 0
        term_counts[stem] += 1
    return term_counts

def get_term_weights(term_counts, term_shop_counts, num_shops):
    weights = {}
    normalized_counts = normalize_counts(term_counts)
    for term in term_counts:
        weights[term] = normalized_counts[term] * math.log(float(num_shops) / term_shop_counts[term])
    return weights
	
def get_object_from_json(file_name):
    file = open(file_name)
    object = json.load(file)
    return object
    
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

if __name__ == '__main__':
    main()








