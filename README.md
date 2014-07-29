# etsy_similar_shops

## Motivation

The goal of this project was to be able to reasonably determine the five most similar shops for each given shop in an Etsy shop sample. This sort of tool could have immediate application on the Etsy site. Users who spend a lot of time looking at certain shops could be shown other similar suggested shops to check out. Owners of similar shops could more easily find each other for forming Etsy teams. The categories within Etsy's shop-by-category system could evolve with changing trends through observation and clustering of shops by similarity. The similarity engine could be incorporated into search to help return shops similar to users' search queries. The list goes on!

## The data

Due to the variation in how and where shop owners choose to display information about their shops and listings, I chose to incorporate as many conceivably relevant fields from the Etsy API as possible into my similarity algorithm. From each shop's listings I collected tags, title, description, category, style, materials, who-made, when-made, recipient, and occasion fields. I then went on to collect shop announcements and "about" information; shop owner profile location information and favorite materials lists; tags from teams the shop owner belongs to; and tags from treasuries the shop owner's listings belong to. 

I chose to include lots of term sources for shops, even though many collected terms would likely often be irrelevant. This was done with the faith that the similarity algorithm would serve to filter out the meaningful terms from the noise. This is a deliberate strategy to ensure that shops with very little data and few listings could still be included in a similarity search. Indeed, many of the shops in my samples had only one listing, and several were deactivated even during the process of downloading their information.

I also found that many shops tended to cram multiple concepts into a single tag, so at the risk of destroying some compound words I decided to tokenize the text of all tag fields as well. It might be interesting to try this problem using n-grams instead of single word tokens, but due to the small sample size in this project I felt that this would just introduce unwanted noise.

To download 5000 active shops and then save relevant data for a sample of 300, on the command line run [get_shops.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_shops.py):

    python get_shops.py 5000 300 "shops.json"
    
This will output to a file shops.json.

Note: make sure to insert your own API key in the top of this script.

#### Treasury trouble 

Treasury information was tricky to obtain because there was no direct API for accessing treasuries by a contained listing. To get around this I wrote scripts to download all available treasuries and store that information in two hashes for quick look-ups. Unfortunately, even after downloading all 25,000 publicly available treasuries, I was unable to find a random sample of active shops with any listings found in those treasuries.

To try anyway and download treasuries and refactor them for efficient look-ups (takes about an hour or two), run [get_treasuries.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_treasuries.py) and [make_treasury_hashes.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/make_treasury_hashes.py):

    python get_treasuries.py 25000 "treasuries.json"
    python make_treasury_hashes.py "treasuries.json" "listing_treasury_hash.json" "treasury_tag_hash.json"

Output from a sample run of make_treasury_hashes.py is available in this repo: [listing_treasury_hash.json](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/listing_treasury_hash.json) / [treasury_tag_hash.json](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/treasury_tag_hash.json).

## The algorithm(s)

After cleaning and tokenizing all of the text I collected, I used [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf) to weight each distinct term associated with a shop and form a sparse term-document matrix. Tf-idf normalizes term frequencies so that important words like "scarf" or "silver" get weighted more heavily, while ubiquitous unimportant words like "the" and "for" get weighted much less. 

I then used [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) to measure the distance (similarity) between shops. I chose cosine similarity because unlike, say, Euclidian distance, cosine similarity is not affected by the magnitude of the vectors it is comparing. This seemed like the best choice for the Etsy data, as different shops can have drastically different sizes based on listing count and how wordy the shop owners are in their descriptions.

To display the 5 most similar shops to each shop in the sample file shops.json, run [get_similar_shops.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops.py):

    python get_similar_shops.py "shops.json"
    
To run this script with the treasury information included, run with these extra arguments (see sample tf-idf output [here](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_tfidf.txt)):

    python get_similar_shops.py "shops.json" "listing_treasury_hash.json" "treasury_tag_hash.json"

    
To display more verbose similarity information, such as similarity score and the highest weighted terms from each shop, run with "details" as the fourth argument (see sample detailed td-idf output [here](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_tfidf.txt)):

    python get_similar_shops.py "shops.json" "listing_treasury_hash.json" "treasury_tag_hash.json" "details"

The simple approach of tf-idf has its limitations. In particular, it is not good at detecting synonyms or alternate spellings of terms. To get around this I wrote an alternate script [get_similar_shops_lsi.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops_lsi.py) that [lemmatizes](http://en.wikipedia.org/wiki/Lemmatisation) terms using [NLTK](http://www.nltk.org/) and performs [latent semantic indexing](http://en.wikipedia.org/wiki/Latent_semantic_indexing) using the [Gensim](http://radimrehurek.com/gensim/index.html) package. Latent semantic indexing (also known as latent semantic analysis) applies [singular value decomposition](http://en.wikipedia.org/wiki/Singular_value_decomposition) to the term-document matrix to extract meaningful "concepts" (read: eigenvectors), and then redefines each document in terms of those concepts. This is much stronger than simple tf-idf, as it leverages the covariance between terms to detect document similarity even when explicit term overlap is low. 

To display the 5 most similar shops based on LSI, first install the [NLTK](http://www.nltk.org/) and [Gensim](http://radimrehurek.com/gensim/index.html) Python libraries, and then run [get_similar_shops_lsi.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops_lsi.py) (see sample LSI output [here](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_lsi.txt)):

    python get_similar_shops_lsi.py "shops.json"
    
This script also accepts additional treasury and "details" arguments just like [get_similar_shops.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops.py) does (see sample detailed LSI output [here](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_lsi_details.txt)).

## Results

I ran both the tf-idf technique and the LSI technique on a sample of 300 shops, and they produced positive results. The similarity scores from LSI were markedly high between shops with obvious similarities, and scores dropped off quickly as the list went down. This often appeared to correspond conceptually to the drop-off of meaningful similarity between shops on each list. 

For example, the shop LittleFuzzyBaby (which sells baby blankets) scored a 91.6% similarity with SweetMinkyBaby, which also sells baby blankets. The next 4 shops in the top five sell other baby-oriented things, though not blankets specifically. Accordingly, these shops scored in the 47%-66% similarity range. This seems to make sense.

_LSI example result, showing 4 highest weighted terms for each shop (full results: [concise](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_lsi.txt) / [detailed](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_lsi_details.txt)):_

    LittleFuzzyBaby  (blanket 3.49)  (minky 3.24)  (hooded 3.09)  (camel 3.01)
    1. 0.916 SweetMinkyBaby  (minky 4.15)  (blanket 4.09)  (butler 3.42)  (amy 3.42)
    2. 0.661 MoniKnitsThings  (booty 3.6)  (knitting 3.27)  (therandomact 3.0)  (sylmar 3.0)
    3. 0.653 MJCLKraft  (mop 4.27)  (tied 4.17)  (santa 4.17)  (blanket 4.09)
    4. 0.513 Baugher17  (bottle 3.61)  (automotive 3.11)  (cleaned 3.11)  (lid 3.11)
    5. 0.478 OnesieGang  (goofy 3.66)  (onesie 3.57)  (punk 3.57)  (toddler 2.96)

The tf-idf results had much lower, flatter similarity scores. The most similar shop in a list rarely exhibited a similarity score much greater than that of the fifth most similar shop. The tf-idf results were still "correct" quite often, and exhibited top-five shop lists very much in line with those from the LSI results, though the tf-idf lists often would seemingly be in the wrong order, and with more apparent misses included. 

In the example below we see a similar result for LittleFuzzyBaby as in the LSI example, however the similarity scores here are much lower, with less of a gap between the winner (SweetMinkyBaby) and the rest. Also, a felt monster keychain shop called VsLittleMonsters somehow appeared as the second most similar shop to SweetMinkyBaby.

_Tf-idf example result, showing 4 highest weighted terms for each shop (full results: [concise](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_tfidf.txt) / [detailed](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/sample_output_tfidf_details.txt)):_

    LittleFuzzyBaby  (blanket 3.7)  (minky 3.4)  (hooded 3.22)  (camel 3.05)
    1. 0.127 SweetMinkyBaby  (minky 4.81)  (blankets 4.51)  (ruffle 3.87)  (butler 3.65)
    2. 0.111 VsLittleMonsters  (keychain 4.19)  (felt 4.09)  (monsters 3.46)  (exactly 3.46)
    3. 0.098 OnesieGang  (goofy 3.8)  (onesie 3.75)  (punk 3.75)  (skull 3.23)
    4. 0.091 MINICROP  (pom 3.35)  (pull 3.18)  (wristlet 3.1)  (braided 3.1)
    5. 0.088 MoreThanSprinkles  (burp 4.99)  (cloth 3.75)  (absorption 3.56)  (6ply 3.56)

When testing the tf-idf method with smaller sample sizes (like 100) I noticed that shops with very few listings seemed to show up frequently in unexpected top-five lists. This may have been due to the choice of tf-idf weighting formulas, which may have inadvertently penalized or homogenized weights in longer documents. It may also be that shops with scant information were more heavily weighted by secondary traits, like location or various listing enums that I included in the bag of words. 

A larger sample size and different choices for some of the parameters along the way might help improve this model. Access to user site-usage data could also be helpful toward measuring the "correctness" of these similarity results. 

Overall, the bag-of-words tf-idf cosine model performed decently for its simplicity, but the beautiful LSI algorithm stole the show with its consistently sensible, almost intuitive results.
