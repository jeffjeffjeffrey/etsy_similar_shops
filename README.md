# etsy_similar_shops

## Motivation

The goal of this project was to be able to reasonably determine the five most similar shops for each given shop in an Etsy shop sample. This is the sort of feature that would have immediate use on the Etsy site. Users who spend a lot of time looking at certain shops could be shown other similar suggested shops to check out. Owners of similar shops could more easily find each other for forming teams. The categories within Etsy's shop-by-category system could evolve with changing trends through observation and clustering of shops by similarity. The list goes on!

## The data

Due to the variation in how and where shop owners choose to display information about their shops and listings, I chose to incorporate as many concievably relevant fields from the Etsy API as possible into my algorithm. For a given shop, I collected listing tags, title, description, category, style, materials, who-made, when-made, recipient, and occasion. I then went on to collect shop announcement and about information; shop owner profile location information and favorite matierials; tags from teams the shop owner belongs to; and tags from treasuries the shop owner's listings belong to. 

I chose to include lots of term sources for shops knowing that many would likely be irrelevant, with the idea that the algorithm would serve to filter out the meaningful terms from the noise. This is a deliberate strategy to ensure that shops with very little data and few listings could still be included in a similarity search. 

I also found that many shops tended to cram multiple concepts into a single tag, so at the risk of destroying some compound words I decided to tokenize all tag fields as well. It might be interesting to try this problem using n-grams instead of single word tokens, but due to the small sample size in this project I felt that this would just introduce unwanted noise.

To download 5000 active shops and then save relevant data for a sample of 300, in the command line run

    python get_shops.py 5000 300 "shops.json"
    
This will output to a file shops.json.

#### Treasury trouble 

The treasury information was tricky to obtain because there was no direct API for accessing treasuries by a contained listing. To get around this I wrote a script to download all available treasuries and store that information in a convenient hash for look-ups. Unfortunately, even after downloading all 25,000 publicly available treasuries, I was unable to find a random sample of active shops with any listings found in those treasuries.

To download treasuries and refactor them for efficient look-ups, run

    python get_treasuries.py "treasuries.json"
    python make_treasury_hashes.py "treasuries.json" "listing_treasury_hash.json" "treasury_tag_hash.json"

## The algorithm(s)

After cleaning and tokenizing all of this text, I used [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf) to weight each distinct term associated with a shop and form a sparse term-document matrix. Tf-idf normalizes term frequencies so that important words like "scarf" or "silver" get weighted more heavily, while ubiquitous unimportant words like "the" and "for" get weighted much less. 

I then used [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) to measure the distance (similarity) between shops. I chose cosine similarity because, unlike say Euclidian distance, cosine similarity is not affected by the magnitude of the vectors it is comparing. This seemed like the best choice for the Etsy data, as different shops can have drastically sizes based on their number of listings and how wordy the shop owners are in their descriptions.

To display the 5 most similar shops to each shop in a sample, run

    python get_similar_shops.py "shops.json"
    
To run this script with the treasury information included, run

    python get_similar_shops.py "shops.json" "listing_treasury_hash.json" "treasury_tag_hash.json"
    
To display more verbose similarity information, such as similarity score and the highest weighted terms from each shop, run

    python get_similar_shops.py "shops.json" "listing_treasury_hash.json" "treasury_tag_hash.json" "print"

The simple approach of tf-idf has its limitations. In particular, it is no good at detecting synonyms or alternate spellings of terms. To get around this I wrote an alternate script [get_similar_shops_lsi.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops_lsi.py) that [lemmatizes](http://en.wikipedia.org/wiki/Lemmatisation) terms using [NLTK](http://www.nltk.org/) and performs [latent semantic indexing](http://en.wikipedia.org/wiki/Latent_semantic_indexing) using the [Gensim](http://radimrehurek.com/gensim/index.html) package. Latent symantic indexing (also known as latent symantic analysis) performs [singular value decomposition](http://en.wikipedia.org/wiki/Singular_value_decomposition) on the term-document matrix to extract meaningful "concepts" (read: eigenvectors), and re-defines each document in terms of these concepts. This is much stronger than simple tf-idf, as it leverages the covariance between terms to detect document similarity even when explicit term overlap is low. 

To display the 5 most similar shops based on LSI, first install NLTK and Gensim libraries, and then run

    python get_similar_shops_lsi.py "shops.json"

## Results

I ran both the tf-idf technique and the LSI technique on a sample of 300 shops, and they produced positive results. The similarity scores from LSI were markedly high between shops with obvious similarities, but dropped off quickly as you went down the list. This often appeared to correspond conceptually to the drop-off of meaningful similarity between shops on each list. 

For example, the shop LittleFuzzyBaby (which sells baby blankets) scored a 91.6% similarity with SweetMinkyBaby, which also sells baby blankets. The next 4 shops in the top five sell other baby-oriented things, though not blankets specifically. Accordingly, these shops scored in the 47%-66% similarity range. This seems to make sense.

_LSI example result, showing 4 highest weighted terms for each shop:_

    LittleFuzzyBaby  (blanket 3.49)  (minky 3.24)  (hooded 3.09)  (camel 3.01)
    1. 0.916 SweetMinkyBaby  (minky 4.15)  (blanket 4.09)  (butler 3.42)  (amy 3.42)
    2. 0.661 MoniKnitsThings  (booty 3.6)  (knitting 3.27)  (therandomact 3.0)  (sylmar 3.0)
    3. 0.653 MJCLKraft  (mop 4.27)  (tied 4.17)  (santa 4.17)  (blanket 4.09)
    4. 0.513 Baugher17  (bottle 3.61)  (automotive 3.11)  (cleaned 3.11)  (lid 3.11)
    5. 0.478 OnesieGang  (goofy 3.66)  (onesie 3.57)  (punk 3.57)  (toddler 2.96)

The tf-idf results had much lower, flatter similarity scores. The most similar shop in a list rarely exhibited a similarity score much greater than that of the fifth most similar. The tf-idf was still "correct" quite often, and exhibited top-five shop lists very much in line with those from the LSI results, though the tf-idf lists often would seemingly be in the wrong order, and with more apparent misses included. In the example below we see a similar result for LittleFuzzyBaby as in the LSI example, however the similarity scores here are much lower, with less of a gap between the winner (SweetMinkyBaby) and the rest. Also, a felt monster keychain shop called VsLittleMonsters somehow appeared as the second most similar shop to SweetMinkyBaby.

_tf-idf example result, showing 4 highest weighted terms for each shop:_

    LittleFuzzyBaby  (blanket 3.7)  (minky 3.4)  (hooded 3.22)  (camel 3.05)
    1. 0.127 SweetMinkyBaby  (minky 4.81)  (blankets 4.51)  (ruffle 3.87)  (butler 3.65)
    2. 0.111 VsLittleMonsters  (keychain 4.19)  (felt 4.09)  (monsters 3.46)  (exactly 3.46)
    3. 0.098 OnesieGang  (goofy 3.8)  (onesie 3.75)  (punk 3.75)  (skull 3.23)
    4. 0.091 MINICROP  (pom 3.35)  (pull 3.18)  (wristlet 3.1)  (braided 3.1)
    5. 0.088 MoreThanSprinkles  (burp 4.99)  (cloth 3.75)  (absorption 3.56)  (6ply 3.56)

When testing the tf-idf method with smaller sample sizes (like 100) I noticed that shops with very few listings seemed to show up frequently in unexpected top-five lists. This may have been due to the choice of tf-idf weighting formulas, which may have inadvertently penalized or homogenized weights in longer documents. It may also be that shops with scarse information were more heavily weighted by secondary traits, like location or various listing enums that I included in the bag of words. 

A larger sample size and different choices for some of the parameters along the way might help improve this model. Access to user site usage data could also be greatly helpful toward measuring the "correctness" of these similarity results. 
