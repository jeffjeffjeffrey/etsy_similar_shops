# etsy_similar_shops


Here is some python code for performing tf-idf and LSI similarity tests on Etsy shops based on words found in shop listings and other related sources through the Etsy API.

## Motivation

The goal of this project was to be able to reasonably determine the five most similar shops for each given shop in a sample of Etsy shops. This is the sort of feature that would have immediate use on the Etsy site. Users who spend a lot of time looking at certain shops could be shown other similar suggested shops to check out. Owners of similar shops could more easily find each other for forming Teams. The categories within Etsy's shop-by-category system could evolve with changing trends through observation and clustering of shops by similarity. The list goes on!

## The data

Etsy's shops are filled with publicly available data, and the meaningful parts of these data are largely text. Each shop can be thought of as a text document comprised of the words found in its listings. A listing has lots of fields where meaningful text may reside: tags, titles, descriptions, materials, styles, categories, etc, all can contain useful information for shedding light on the nature of an item and the shop that contains it. But this kind of information is not restricted to a shop's listings. Shops themselves can contain useful descriptions, and shop owners may have meaningful shop-related information in their profiles (such as "favorite materials" or even geographical location). Shop owners may belong to Teams on Etsy, which themselves can contain useful tags. And listings may belong to Treasuries, which have their own sets of tags.

After perusing some Etsy shops it became clear that users place meaningful text in unpredictable places. Lots of folks do use tags to help classify their listings, but many others prefer storing searchable terms in listing titles, or in wordy listing descriptions, which are sometimes in other languages. Some shops prefer to put their info in their shop and not their listings, and others provide virtually no info at all. A great many shops contain only a single listing. To account for all of this I decided to include text from any part of a shop or its associated objects that might be a place where a user could put meaningful information about the nature of that shop. 

I began by writing the script [get_shops.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_shops.py), which downloads a bunch of shops from the Etsy API, takes a sample of those shops, downloads and attaches various other things related to each of these shops (like listings, shop info, user profiles, and teams), and saves it all to a file in .json format. 

#### Treasury trouble

I wanted to be able to include tags from treasuries that might contain some of the listings in my sample, but unfortunately there didn't appear to be an API call to fetch treasuries by contained listing. To get around this I wrote the script [get_treasuries.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_treasuries.py), which downloads the "hottest" 25,000 publicly available treasuries and saves them to a (very large) .json file. I then wrote a script [make_treasury_hashes.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/make_treasury_hashes.py) that converts the large list of treasuries into two hashes: one for looking up treasury ids by listing id, and a second for looking up tags by treasury id. These hashes are then saved in .json format in two (much smaller) files. Sadly, after repeated attempts I was not able to produce a sample of shops from get_shops.py that contained even a single listing found amongst the ~250,000 treasury listings.

## The analysis

With my data collected I did some research on document similarity and settled on two techniques that seemed like they might be useful for this Etsy shop dataset: [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf), and [latent semantic analysis](http://en.wikipedia.org/wiki/Latent_semantic_indexing).

#### Tf-idf

The first technique I tried was [tf-idf](http://en.wikipedia.org/wiki/Tf%E2%80%93idf), which stands for "term frequency - inverse document frequency." Tf-idf is a simple way to represent a document as an unordered "bag of words," where each distinct word in the document is weighted based on how important it is. Words that appear a lot in one document get bumped up (like "scarf" in a shop with a bunch of listings for scarves), but words that appear in lots of different documents get bumped down (like "the" and other generic words). Shops are deemed similar if they have lots of highly-weighted words in common. I decided on an "augmented norm" weighting for the tf part, which normalizes term frequencies of a document based on the most frequent term in that document. This was to help account for the great variation in shop document size and content. One drawback to the tf-idf method is that it doesn't respond to synonyms or alternate spellings. One great benefit is that it is easy to implement.

I wrote the script [get_similar_shops.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops.py), which reads in my augmented shop data in .json format and then collects, tokenizes, cleans, and weights the words in each shop according to the tf-idf equations. I found that many shops tended to cram multiple concepts into a single tag, so at the risk of destroying some compound words I decided to tokenize all tag fields as well. It might be interesting to try this problem using n-grams instead of single word tokens, but due to the small sample size in this project I felt that this would just introduce unwanted noise.

#### Distance measures

I then used [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) to compute the similarity score between each pair of shops. Cosine similarity seems to be the standard measure used in these types of analyses, and it is useful because it does not discriminate based on document size (it merely computes the cosine of the angle between the vector representations of the two documents in question). This seemed like the best choice for the Etsy data, as different shops have drastically different sizes based on listing quantity and wordiness of shop owners. 

I first tried other, more complicated distance measures. I split up each document's bag of words into multiple bags of words from separate sources (words from important fields like tags, categories, and listing titles went into one bag; less important fields like geographic location, user info, and listing enums went into a second bag; and "prose" fields like listing descriptions went into a third bag, labeled by the indicated language of the listing). I computed cosine similarity on each bag type separately, and then combined these similarities by a global weight of my subjective choosing. 

In addition to this I tried adding in a shop-size factor that boosted the similarity score of shops with a similar quantity of listings. 

In the end I didn't see much improvement over the single bag of words model, and I didn't feel comfortable introducing arbitrary weightings to things without first performing a deeper empirical investigation about what these weightings ought to be. I decided to trust in the canonical word weightings of tf-idf, though I would be open to blending multiple models in the future given adequate and sensible testing.

#### Latent semantic indexing

The second technique I investigated is called [latent semantic indexing](http://en.wikipedia.org/wiki/Latent_semantic_indexing) (LSI). This is more sophisticated than tf-idf, and much more powerful. In LSI, documents are first converted to weighted bags of words, just as in tf-idf. This collection of bags is then stored in a term-document matrix. Then, [singular value decomposition](http://en.wikipedia.org/wiki/Singular_value_decomposition) is performed to extract "concepts" (read: eigenvectors) from the collection of documents. Finally, each document is then re-written in terms of its underlying concepts (read: change of basis) instead of merely in terms of the specific words it contains. Under this framework two documents can be recognized as similar even if they share no words in common. This is very useful for the Etsy shop problem. A shop comprised of tags ["sterling", "antique", "jewelry"] would share no similarity to a shop defined by tags ["silver", "vintage", "earrings"] under the basic tf-idf model. LSI uses linear algebra and the wisdom of the masses (read: the covariance between words in the document corpus) to overcome this limitation. 

Just like in the tf-idf model, these transformed document vectors can be compared using the [cosine similarity](http://en.wikipedia.org/wiki/Cosine_similarity) formula. Unlike the tf-idf model, LSI is hard to implement without the use of statistical packages for performing large sparse matrix operations. I found a python library called [Gensim](http://radimrehurek.com/gensim/index.html) that does this heavy lifting for you. I made a second version of the similarity script called [get_similar_shops_lsi.py](https://github.com/jeffjeffjeffrey/etsy_similar_shops/blob/master/get_similar_shops_lsi.py) which uses this package. 

I chose a sample of 300 shops, which amounted to a total of  Then I installed the [WordNet](http://wordnet.princeton.edu/) libraries from the [Natural Language Toolkit](http://www.nltk.org/) in order to further clean up words by [lemmatizing](http://en.wikipedia.org/wiki/Lemmatisation) them. (This is a process which converts a word to its root, like "sewing" -> "sew.")

## Results

I ran both the tf-idf technique and the LSI technique on a sample of 300 shops, and they produced positive results. The similarity scores from LSI were markedly high between shops with obvious similarities, but droped off quickly as you went down the list. This often appeared to correspond conceptually to the drop-off of meaningful similarity between shops on each list. 

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




  


  
