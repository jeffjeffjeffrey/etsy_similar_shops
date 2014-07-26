import sys
import json
import math
import re
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora, models, similarities
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

def main():

    # Command line arguments (4): 
    #         1. the name of a shops .json file,
    #         2. (optional) the name of a listing-treasury hash .json file,
    #         3. (optional) the name of a treasury tag hash .json file,
    #         4. (optional) the string "details" to turn on more verbose output
    # Output: prints the name of each input shop followed by its five most similar shops.
    # Algorithm: Latent semantic indexing based on tf-idf term weighting 
    #            with cosine similarity measure (Gensim package)

    # Check command line arguments and load input files
    try:       
        shops = get_object_from_json(sys.argv[1])
        logging.info("Shop list found with " + str(len(shops)) + " shops.")
        if len(sys.argv) > 3:
            listing_treasury_hash = get_object_from_json(sys.argv[2])
            treasury_tag_hash = get_object_from_json(sys.argv[3])
            logging.info("Treasury tag hash found with " + str(len(treasury_tag_hash)) + " treasuries.")
            logging.info("Listing treasury hash found with " + str(len(listing_treasury_hash)) + " listings.")
        else:
            listing_treasury_hash = {}
            treasury_tag_hash = {}            
        if len(sys.argv) == 5 and sys.argv[4] == "details":            
            print_details = True
        else:
            print_details = False
    except:
        e = sys.exc_info()[0]
        logging.error("We had an error with command line args: " + str(e)) 
        return
    
    # Collect the terms from each shop and its related objects
    texts = []
    all_terms = []
    for shop in shops:
        terms = [] 
        terms += get_listing_terms(shop['listings'])
        terms += get_user_profile_terms(shop['user_profile'])
        terms += get_misc_terms(shop)
        terms += get_treasury_terms(shop['listings'], listing_treasury_hash, treasury_tag_hash)

        # Store the term-count hash in the shop object        
        shop['terms'] = clean_terms(terms)
        shop['term_counts'] = get_term_counts(clean_terms(terms))
        all_terms += shop['term_counts'].keys()
        texts.append(clean_terms(terms))
        
    # Calculate the number of shops that use each term (just used for verbose output)    
    term_shop_counts = get_term_counts(all_terms)
                
    # Calculate the tf-idf weight for the terms in each shop (just for verbose output)
    for shop in shops:
        shop['term_weights'] = get_term_weights(
            shop['term_counts'], 
            term_shop_counts, 
            len(shops)
        )
    
    # Remove any tokens that only appear once in the whole corpus of shops
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
        for text in texts]
    
    # Create a Gensim dictionary to house all the words in the corpus  
    dictionary = corpora.Dictionary(texts)    
    
    # Convert the collection of shop term lists into a Gensim document corpus
    corpus = [dictionary.doc2bow(text) for text in texts]   
    
    # Convert the document corpus into a tf-idf weighted corpus
    tfidf = models.TfidfModel(corpus)    
    corpus_tfidf = tfidf[corpus]

    # Convert the tf-idf corpus into a LSI-based corpus of 100 topics
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100)
    corpus_lsi = lsi[corpus_tfidf]
    
    # Compute the similarities between all pairs of shops
    index = similarities.MatrixSimilarity(lsi[corpus])
        
    # Print the the five most similar shops to each shop
    for i in range(len(shops)):
        if len(shops[i]['terms']) == 0:
            print shops[i]['shop_name'] + " has no terms!"
            continue
            
        # Convert the current shop's term list to the LSI basis 
        # and find its similar shops from the LSI corpus
        vec_lsi = lsi[tfidf[dictionary.doc2bow(shops[i]['terms'])]]
        sims = index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        sims = [sim for sim in sims if sim[1] > 0]
        if print_details:
            print_similar_shop_details(shops[i], shops, sims[1:6])
        else:
            print_similar_shops(shops[i], shops, sims[1:6])
    
    return

def print_similar_shop_details(primary_shop, all_shops, sims):  

    # Input: a shop object along with a list of (shop, similarity score) pairs
    # Output: prints the primary and similar shops' names,
    #         along with similarity score and highest weighted terms
    
    print primary_shop['shop_name'],
    print_top_terms(primary_shop['term_weights'])
    if len(sims) <= 1:
        print " No similar shops were found!"
    else:
        i = 1 
        for sim in sims:
            print str(i) + ". " + str(sim[1]) + " " + all_shops[sim[0]]['shop_name'],
            print_top_terms(all_shops[sim[0]]['term_weights'])
            i += 1   
    
def print_similar_shops(primary_shop, all_shops, sims):

    # Input: a shop object along with a list of (shop, similarity score) pairs
    # Output: prints the primary and similar shops' names

    print primary_shop['shop_name'] + ":",
    if len(sims) <= 1:
        print " No similar shops were found!"
    else:
        for sim in sims[:-1]:
            print all_shops[sim[0]]['shop_name'] + ",",
        print all_shops[sims[-1][0]]['shop_name']
                
def print_top_terms(term_weights):

    # Input: a hash of term to weight
    # Output: prints the top five weighted terms and their weights

    pairs = []
    for term in term_weights:
        pairs.append((term, term_weights[term]))
    pairs = sorted(pairs, key=lambda entry: -1 * entry[1])
    for pair in pairs[:7]:
        print " (" + pair[0] + " " + str(math.trunc(pair[1]*100)/100.0) + ")",
    print ""

def get_listing_terms(listings):

    # Input: a list of Etsy Listing objects
    # Output: a list of terms found in various fields in these listings
    
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

    # Input: an Etsy UserProfile object
    # Output: a list of terms found in this profile
    
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

    # Input: an Etsy Shop object
    # Output: a list of terms found in this shop
    
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

    # Input: a list of Etsy Listing objects, 
    #        a hash from listing id to the ids of treasuries containing that listing,
    #        a hash from treasury id to the tags of that treasury
    # Output: a list of terms found in the tags of the treasuries containing
    #         the input listings
    
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

    # Input: a list of terms
    # Output: a hash from term to term count
    
    term_counts = {}
    if not terms:
        return term_counts
    for term in terms:
        if term not in term_counts:
            term_counts[term] = 0
        term_counts[term] += 1
    return term_counts

def clean_terms(terms):

    # Input: a list of terms
    # Output: a list of these terms with non-alphanumeric characters removed, 
    #         converted to lowercase, tokenized, 
    #         and lemmatized (using NLTK WordNet package)
    
    cleaned = []
    lmtzr = WordNetLemmatizer()
    for term in terms:
        stems = re.sub('[^0-9a-zA-Z]+', ' ', term.lower()).strip().split()
        for stem in stems:
            stem = lmtzr.lemmatize(stem)
            cleaned.append(stem)
    return cleaned

def get_term_weights(term_counts, term_shop_counts, num_shops):

    # Input: a hash of term to term count, 
    #        a hash of term to the number of documents which contain that term,
    #        the total number of shops
    # Output: a hash of terms to the tf-idf weighting of each term,
    #         using the augmented norm for term frequency
    
    weights = {}
    max_count = 1
    for term in term_counts:
        max_count = max(max_count, term_counts[term])
    for term in term_counts:
        normalized_count = 0.5 + 0.5 * term_counts[term] / max_count
        weights[term] = normalized_count * math.log(float(num_shops) / term_shop_counts[term])
    return weights
        	
def get_object_from_json(file_name):

    # Input: the name of a known .json file
    # Output: a python object made from that file's contents
    
    file = open(file_name)
    object = json.load(file)
    return object

if __name__ == '__main__':
    main()








