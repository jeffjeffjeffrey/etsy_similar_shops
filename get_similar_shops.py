import sys
import json
import math
from nltk.stem.wordnet import WordNetLemmatizer

def main():
    shops = get_shops_from_file(sys.argv[1])

    min_listings = 1    
    full_shops = []
    for shop in shops:
        if len(shop['listings']) >= min_listings:
            full_shops.append(shop)
    shops = full_shops

    # Calculate the (normalized) term frequencies in each shop, grouped by term type
    for shop in shops:
        term_frequencies = {}
        term_frequencies['tags'] = get_tag_frequencies(shop)
        # for prose section, we'll make a separate object for each language
        term_frequencies = get_prose_frequencies(shop, term_frequencies)
        term_frequencies['enums'] = get_enum_frequencies(shop['listings'])
        term_frequencies['location'] = get_location_frequencies(shop['user_profile'])
        term_frequencies['connections'] = get_connection_frequencies(shop)
        term_frequencies['groups'] = get_group_frequencies(shop)
        
        term_frequencies['secondary'] = dict(term_frequencies['enums'].items() + term_frequencies['location'].items() + term_frequencies['connections'].items() + term_frequencies['groups'].items())
        
        for term_type in term_frequencies:
            term_frequencies[term_type] = normalize_frequencies(term_frequencies[term_type])
        shop['term_frequencies'] = term_frequencies
    
    similarity_weights = {}
    similarity_weights['tags'] = 10
    similarity_weights['enums'] = 0
    similarity_weights['location'] = 0
    similarity_weights['connections'] = 0
    similarity_weights['groups'] = 0
    similarity_weights['secondary'] = 1
    similarity_weights['default'] = 5
       
    # Calculate the number of shops that use each term 
    term_shop_frequencies = {}
    for shop in shops:
        for term_type in shop['term_frequencies']:
            if term_type not in term_shop_frequencies:
                term_shop_frequencies[term_type] = {}
            term_shop_frequencies[term_type] = collect_terms(shop['term_frequencies'][term_type].keys(), term_shop_frequencies[term_type], False)
        
    # Calculate the tf-idf for the terms in each shop
    for shop in shops:
        shop['term_weights'] = {}
        for term_type in shop['term_frequencies']:
            # Exception handling here
            shop['term_weights'][term_type] = get_term_weights(shop['term_frequencies'][term_type], term_shop_frequencies[term_type], len(shops))

    for shop in shops:
        print "Shop " + str(shop['shop_id']) + " " + shop['shop_name'] + " (user " + str(shop['user_id']) + ")"
        for term_type in shop['term_frequencies']:
            print " Term type: " + term_type
            for term in shop['term_frequencies'][term_type]:
                print "  Term " + term + ": " + str(shop['term_frequencies'][term_type][term]) + " - " + str(term_shop_frequencies[term_type][term]) + " - " + str(shop['term_weights'][term_type][term])
    
    # Calculate five most similar shops to each shop
    for primary_shop in shops:
        if len(primary_shop['listings']) < min_listings:
            continue
        print "Shop " + primary_shop['shop_name']
        similar_shops_by_term_type = {}
        similar_shops = []
        for other_shop in shops:
            if len(other_shop['listings']) < min_listings:
                continue
            total_similarity = 0.0
            for term_type in term_shop_frequencies:
                if term_type not in similar_shops_by_term_type:
                    similar_shops_by_term_type[term_type] = []
                if term_type in primary_shop['term_weights'] and term_type in other_shop['term_weights']:
                    similarity = cosine_similarity(primary_shop['term_weights'][term_type], other_shop['term_weights'][term_type])
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
        for term_type in shop['term_frequencies']:
            if term_type in similarity_weights and similarity_weights[term_type] == 0:
                continue
            print " Similarity by " + term_type + ":"
            similar_shops_by_term_type[term_type] = sorted(similar_shops_by_term_type[term_type], key=lambda entry: -1 * entry[1])
            for similar_shop in similar_shops_by_term_type[term_type][1:11]:
                print "  " + str(similar_shop[1]) + " " + similar_shop[0]['shop_name']
    return 0

def get_tag_frequencies(shop):
    term_frequencies = {}
    for listing in shop['listings']:
        term_frequencies = collect_terms(listing['tags'], term_frequencies)
        term_frequencies = collect_terms(listing['materials'], term_frequencies)
        term_frequencies = collect_terms(listing['category_path'], term_frequencies)
        term_frequencies = collect_terms(listing['style'], term_frequencies)
        term_frequencies = collect_terms(listing['title'].split(), term_frequencies)
    if shop['user_profile']['materials']:
        user_materials = shop['user_profile']['materials'].split('.')
        for material in user_materials:
            material = material.replace('_', ' ')
        term_frequencies = collect_terms(user_materials, term_frequencies)
    for team in shop['user_teams']:
        term_frequencies = collect_terms(team['tags'], term_frequencies)
    # treasury tags
    return term_frequencies

# for prose section, we'll make a separate object for each language
def get_prose_frequencies(shop, term_frequencies):
    for listing in shop['listings']:
        # get the language of the listing
        listing_language = "language=" + listing['language']
        if listing_language not in term_frequencies:
            term_frequencies[listing_language] = {}
        term_frequencies[listing_language] = collect_terms(listing['description'].split(), term_frequencies[listing_language])

    # get the first listed language of the shop
    shop_language = "language=" + shop['languages'][0]
    if shop_language not in term_frequencies:   
        term_frequencies[shop_language] = {}     
    if shop['announcement']:
        term_frequencies[shop_language] = collect_terms(shop['announcement'].split(), term_frequencies[shop_language])
    if shop['about']:
        term_frequencies[shop_language] = collect_terms(shop['about']['story_headline'].split(), term_frequencies[shop_language])
        term_frequencies[shop_language] = collect_terms(shop['about']['story_leading_paragraph'].split(), term_frequencies[shop_language])
        term_frequencies[shop_language] = collect_terms(shop['about']['story'].split(), term_frequencies[shop_language])
    return term_frequencies

def get_enum_frequencies(listings):
    term_frequencies = {}
    for listing in listings:
        terms = []
        if listing['who_made']:
            terms.append("who_made=" + listing['who_made'])
        if listing['when_made']:
            terms.append("when_made=" + listing['when_made'])
        if listing['recipient']:
            terms.append("recipient=" + listing['recipient'])
        if listing['occasion']:
            terms.append("occasion=" + listing['occasion'])    
        term_frequencies = collect_terms(terms, term_frequencies, False)    
    return term_frequencies    

def get_location_frequencies(user_profile):
    terms = []
    if user_profile['country_id']:
        terms.append("country_id=" + str(user_profile['country_id']))
    if user_profile['region']:
        terms.append("region=" + user_profile['region'])
    if user_profile['city']:
        terms.append("city=" + user_profile['city'])
    return collect_terms(terms, {}, False)

def get_connection_frequencies(shop):
    user_ids = [str(shop['user_id'])]
    for connection in shop['connected_users']:
        user_ids.append(str(connection['user_id']))
    for team in shop['user_teams']:
        for user in team['users']:
            if user['user_id'] != shop['user_id']:
                user_ids.append(str(user['user_id']))
    return collect_terms(user_ids, {}, False)

def get_group_frequencies(shop):
    team_ids = []
    for team in shop['user_teams']:
        team_ids.append(str(team['group_id']))
    # treasury names
    return collect_terms(team_ids, {}, False)
	
def normalize_frequencies(term_frequencies):   
    max_freq = 1
    for term in term_frequencies:
        max_freq = max(max_freq, term_frequencies[term])
    for term in term_frequencies.keys():
        term_frequencies[term] = 0.5 + 0.5 * term_frequencies[term] / max_freq
    return term_frequencies
	
def collect_terms(terms, term_frequencies, make_stem=True):
    #make_stem = False
    if not terms:
        return term_frequencies
    lmtzr = WordNetLemmatizer()
    for term in terms:
        if make_stem:
            stem = lmtzr.lemmatize(term.lower())
        else:
            stem = term
        if stem in term_frequencies:
            term_frequencies[stem] += 1
        else:
            term_frequencies[stem] = 1
    return term_frequencies

def get_term_weights(term_frequencies, term_shop_frequencies, num_shops):
    weights = {}
    for term in term_frequencies:
        weights[term] = term_frequencies[term] * math.log(float(num_shops) / term_shop_frequencies[term])
    return weights
	
def get_shops_from_file(file_name):
    file = open(file_name)
    shops = json.load(file)
    return shops
    
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








