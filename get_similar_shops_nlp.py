import sys
import json
import math
import re
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora, models, similarities
import logging

def main():

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARN)

    shops = get_object_from_json(sys.argv[1])
    
    texts = []

    # Calculate the term counts in each shop
    all_terms = []

    for shop in shops:
        terms = [] 
        terms += get_listing_terms(shop['listings'])
        terms += get_user_profile_terms(shop['user_profile'])
        terms += get_misc_terms(shop)
        
        shop['terms'] = clean_terms(terms)
        shop['term_counts'] = get_term_counts(clean_terms(terms))
        all_terms += shop['term_counts'].keys()
        texts.append(clean_terms(terms))
    
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once]
        for text in texts]
            
    dictionary = corpora.Dictionary(texts) # creates numerical ids for all tokens in the corpus
    
    corpus = [dictionary.doc2bow(text) for text in texts] # changes the text-based corpus into a bow-based corpus
   
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model    
    corpus_tfidf = tfidf[corpus] # transforms the bow-based corpus into a tf-idf weighted corpus

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)
    corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
    
    index = similarities.MatrixSimilarity(lsi[corpus])
                
    # Calculate the number of shops that use each term      
    term_shop_counts = get_term_counts(all_terms)
                
    # Calculate the tf-idf weight for the terms in each shop
    for shop in shops:
        shop['term_weights'] = get_term_weights(
            shop['term_counts'], 
            term_shop_counts, 
            len(shops)
        )
        
    for i in range(len(shops)):
        print shops[i]['shop_name'],
        print_top_terms(shops[i]['term_weights'])
        vec_lsi = lsi[tfidf[dictionary.doc2bow(shops[i]['terms'])]]
        sims = index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        for sim in sims[1:11]:
            print " " + str(sim[1]) + " " + shops[sim[0]]['shop_name'],
            print_top_terms(shops[sim[0]]['term_weights'])
    
    return
    
def print_top_terms(term_weights):
    pairs = []
    for term in term_weights:
        pairs.append((term, term_weights[term]))
    pairs = sorted(pairs, key=lambda entry: -1 * entry[1])
    for pair in pairs[:7]:
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
    return terms
    
def get_user_profile_terms(user_profile):
    terms = []
    if user_profile['materials']:
        materials = user_profile['materials'].split('.')
        for material in materials:
            terms.append(material.replace('_', ' '))
    return terms

def get_misc_terms(shop):
    terms = []
    for team in shop['user_teams']:
        terms += team['tags']
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
    lmtzr = WordNetLemmatizer()
    for term in terms:
        stems = re.sub('[^0-9a-zA-Z]+', ' ', term.lower()).strip().split()
        for stem in stems:
            stem = lmtzr.lemmatize(stem)
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
        	
def get_object_from_json(file_name):
    file = open(file_name)
    object = json.load(file)
    return object

if __name__ == '__main__':
    main()








