etsy_similar_shops
=============

Here is some python code for performing similarity tests on Etsy shops. Given a sample of Etsy shops, the goal of this project was to be able to reasonably determine the five most similar shops for each given shop in the sample. This is the sort of feature that would have immediate use on the Etsy site. Users who spend a lot of time looking at certain shops could be shown other similar suggested shops to check out. Owners of similar shops could more easily find each other for forming Teams. The categories within Etsy's shop-by-category system could evolve with changing trends through observation and clustering of shops by similarity. The list goes on!

The data

Etsy's shops are filled with publicly available data, and the meaningful parts of these data are largely text. Each shop can be thought of as a text document comprised of the words found in its listings. A listing has lots of places where meaningful text may reside: tags, titles, descriptions, materials, styles, categories, etc, all can contain useful information for shedding light on the nature of an item and the shop that contains it. But this kind of information is not restricted to a shop's listings. Shops themselves can contain useful descriptions, and shop owners may have meaningful shop-related information in their profiles (such as "favorite materials" or even geographical location). Shop owners may belong to Teams on Etsy, which themselves can contain useful tags. And listings may belong to Treasuries, which have their own sets of tags.

After perusing some Etsy shops it became clear that users place meaningful text in unpredictable places. Lots of folks do use tags to help classify their listings, but many others prefer storing searchable terms in listing titles, or in wordy listing descriptions. Some shops prefer to put their info in their shop and not their listings, and others provide virtually no info at all. A great many shops contain only a single listing. To account for all of this I decided to include text from any part of a shop or its associated objects that might be a place where a user could put meaningful information about the nature of that shop. 

I began by writing the script get_shops.py, which downloads a bunch of shops from the Etsy API, takes a sample of those shops, downloads and attaches various other things related to each of these shops (like listings, shop info, user profiles, and teams), and saves it all to a file in .json format. 

Treasury trouble

I wanted to be able to include tags from treasuries that might contain some of the listings in my sample, but unfortunately there didn't appear to be an API call to fetch treasuries by contained listing. To get around this I wrote the script get_treasuries.py, which downloads the "hottest" 25,000 publicly available treasuries and saves them to a (very large) .json file. I then wrote a script make_treasury_hashes.py that converts the large list of treasuries into two hashes: one for looking up treasury ids by listing id, and a second for looking up tags by treasury id. These hashes are then saved in .json format in two (much smaller) files. Sadly, after repeated attempts I was not able to produce a sample of shops from get_shops.py that contained even a single listing found amongst the ~250,000 treasury listings.

With my data collected I did some research on document similarity and settled on two techniques that seemed like they might be useful for this Etsy shop dataset: tf-idf, and latent semantic analysis.

Tf-idf

The first technique I tried was tf-idf, which stands for "term frequency - inverse document frequency." Tf-idf is a simple way to represent a document as an unordered "bag of words," where each distinct word in the document is weighted based on how important it is. Words that appear a lot in one document get bumped up (like "scarf" in a shop with a bunch of listings for scarves), but words that appear in lots of different documents get bumped down (like "the" and other generic words). Shops are deemed similar if they have lots of highly-weighted words in common. I decided on an "augmented norm" weighting for the tf part, which normalizes term frequencies of a document based on the most frequent term in that document. This was to help account for the great variation in shop document size and content. One drawback to the tf-idf method is that it doesn't respond to synonyms or alternate spellings. One great benefit is that it is easy to implement.

I wrote the script get_similar_shops.py, which reads in my augmented shop data in .json format, and then collects, splits, cleans, and weights the words in each shop according to the tf-idf equations. It then uses cosine similarity to compute the similarity score between each pair of shops. Cosine similarity seems to be the standard measure used in these types of analyses, and it is useful because it does not discriminate based on document size (it merely computes the cosine of the angle between the vector representations of the two documents in question).

Latent semantic analysis

The second technique I investigated is called latent semantic analysis (LSI). This is more sophisticated than tf-idf, and much more powerful. In LSI, documents are first converted to weighted bags of words just as in tf-idf, and this collection of bags is then stored in a term-document matrix. Then singular value decomposition is performed to extract "concepts" from the collection of documents. Finally, each document is then re-written in terms of its underlying concepts instead of merely in terms of the specific words it contains. Under this framework two documents can be recognized as similar even if they share no words in common. This is very useful for the Etsy shop problem. A shop comprised of tags ["sterling", "antique", "jewelry"] would share no similarity to a shop defined by tags ["silver", "vintage", "earrings] under the basic tf-idf model. LSI uses linear algebra and the wisdom of the masses to overcome this limitation. 

Just like in the tf-idf model, these transformed document vectors can be compared using the cosine similarity formula. Unlike the tf-idf model, LSI is hard to implement without the use of statistical packages for performing large sparse matrix operations. I found a python library called Gensim that does this heavy lifting for you. I made a second version of the similarity script called get_similar_shops_lsi.py which uses this package. 

I removed some of the less relevant text sources from my bags of words (such as listing occasion, shop announcement, user location, etc). Then I installed the NLTK WordNet libraries in order to further clean up words by "lemmatizing" them. (This is a process which converts a word to its root, like "sewing" -> "sew.")

Results

I ran both the tf-idf technique and the LSI technique on a sample of 100 shops, and they produced decent results. The similarity scores from LSI were markedly high between shops with obvious similarities, but droped off quickly as you went down the list (see example). This often appeared to correspond conceptually to the drop-off of meaningful similarity between shops on each list. The tf-idf results had much lower, flatter similarity scores. The most similar shop in a list rarely exhibited a similarity score much greater than that of the fifth most similar. The tf-idf was still "correct" quite often, and exhibited top-five shop lists very much in line with those from the LSI results, though the tf-idf lists often would be in the seeming wrong order. Though LSI performed expectedly better overall, it was not without its misses.

I noticed that in tf-idf results, shops with very few listings seemed to show up frequently in unexpected top-five lists. This may have been due to the choice of tf-idf weighting formulas, which may have inadvertently penalized or homogenized weights in longer documents. It may also be that shops with scarse information were more heavily weighted by secondary traits, like location or various listing enums that I included in the bag of words. 

A larger sample size and different choices for some of the parameters along the way might help improve this model. Access to user site usage data could also be greatly helpful toward measuring the "correctness" of these similarity results. 



Tf-Idf

ShortRunShirts  (shirts 3.91)  (gridlock 3.45)  (humor 2.93)  (cooldesign 2.87)  (global 2.87)  (skateboarding 2.87)  (skateboarders 2.87) 
  0.105 Newtank  (2xl 3.07)  (tank 2.99)  (3xl 2.81)  (inchi 2.81)  (29 2.56)  (payments 2.56)  (cart 2.56) 
  0.085 Fourtifor  (shirt 2.37)  (payment 2.35)  (34 2.34)  (paramore 2.33)  (vader 2.33)  (gondor 2.33)  (versace 2.33) 
  0.08 oweeDesign  (mean 2.42)  (flawless 2.37)  (woke 2.36)  (payment 2.35)  (deathly 2.34)  (harry 2.34)  (hallows 2.34) 
  0.066 VictoriaCrocheted  (gloves 4.6)  (winter 3.22)  (fingerless 3.22)  (finger 3.22)  (vc 2.76)  (hands 2.76)  (general 2.76) 
  0.057 Bulgaart  (keychain 3.07)  (kuker 3.07)  (culture 2.91)  (bulgaria 2.76)  (evil 2.76)  (spirits 2.6)  (festivals 2.6) 

SouthernVisionDistr  (phillips 3.13)  (safety 3.03)  (contrast 2.85)  (ace 2.85)  (enhancement 2.85)  (earth 2.67)  (oxides 2.67) 
  0.048 DreadFallCreations  (falls 3.91)  (braided 2.76)  (braids 2.6)  (thinner 2.45)  (human 2.45)  (thicker 2.45)  (multicolor 2.45) 
  0.047 FlashyShades  (sunglasses 4.6)  (eyewear 3.61)  (shades 3.61)  (flashygirls 3.18)  (hollywood 2.65)  (regency 2.65)  (proflin 2.47) 
  0.047 ABitofJewelry  (coordinating 2.89)  (accents 2.74)  (mixture 2.45)  (paisley 2.45)  (ares 2.45)  (amazing 2.45)  (polymer 2.39) 
  0.046 Daveu4u  (witch 3.58)  (wicked 3.04)  (wizard 2.81)  (road 2.81)  (brick 2.81)  (oz 2.72)  (longevity 2.55) 
  0.046 oweeDesign  (mean 2.42)  (flawless 2.37)  (woke 2.36)  (payment 2.35)  (deathly 2.34)  (harry 2.34)  (hallows 2.34)
  
  
LSI

VogueVinyl  (monogram 4.6)  (tile 3.91)  (engagement 3.45)  (housewarming 2.93)  (personalized 2.81)  (housewares 2.11)  (wedding 2.11) 
 0.77718 izniktilesandmore  (iznik 3.91)  (tile 3.91)  (glaze 2.99)  (handicraft 2.76)  (20x20 2.76)  (handcraft 2.76)  (tulip 2.73) 
 0.508964 Amburr90210  (photographer 3.45)  (premade 3.45)  (watermark 2.93)  (logo 2.81)  (personalized 2.81)  (include 2.41)  (else 2.24) 
 0.265345 BeautifulPeoplePhoto  (date 3.91)  (save 3.5)  (private 3.07)  (denise 3.07)  (beautifulpeoplephotos 3.07)  (website 3.07)  (graphic 2.6) 
 0.218975 TyAnthony  (invite 4.6)  (dinosaur 4.14)  (dig 3.22)  (sand 3.22)  (birthday 2.89)  (dino 2.76)  (personalization 2.76) 
 0.161903 GlitzNPrintz  (file 3.49)  (pdf 2.85)  (sparkler 2.81)  (sign 2.8)  (printable 2.77)  (bar 2.64)  (download 2.64) 

SouthernVisionDistr  (phillips 3.07)  (safety 2.98)  (enhancement 2.81)  (contrast 2.81)  (ace 2.81)  (earth 2.64)  (liability 2.64) 
 0.629421 FlashyShades  (sunglass 4.6)  (shade 3.76)  (eyewear 3.61)  (flashygirls 3.18)  (hollywood 2.65)  (regency 2.65)  (proflin 2.47) 
 0.547211 PhotoGemsJewelry  (bronze 3.5)  (attractive 3.16)  (setting 2.93)  (photogems 2.87)  (pendant 2.8)  (cove 2.68)  (mute 2.59) 
 0.250299 CoCosCraftCorner  (belle 3.76)  (silhouette 2.84)  (beast 2.72)  (petal 2.51)  (spelled 2.51)  (adaptation 2.51)  (completed 2.51) 
 0.243226 Bulgaart  (keychain 3.02)  (kuker 3.02)  (culture 2.87)  (something 2.87)  (bulgaria 2.73)  (evil 2.73)  (kukers 2.59) 
 0.232133 vttop  (sending 3.07)  (teenage 2.68)  (poly 2.68)  (next 2.49)  (except 2.49)  (australia 2.49)  (tee 2.49) 
  
BeautifulPeoplePhoto  (date 3.91)  (save 3.5)  (private 3.07)  (denise 3.07)  (beautifulpeoplephotos 3.07)  (website 3.07)  (graphic 2.6) 
 0.502919 GlitzNPrintz  (file 3.49)  (pdf 2.85)  (sparkler 2.81)  (sign 2.8)  (printable 2.77)  (bar 2.64)  (download 2.64) 
 0.50288 PuddlesCards  (recycled 2.59)  (botanical 2.59)  (embellishment 2.59)  (padded 2.45)  (query 2.45)  (somebody 2.45)  (handwritten 2.45) 
 0.496037 StampwithShari  (reclosable 2.53)  (produced 2.53)  (cellophane 2.53)  (often 2.53)  (discount 2.53)  (family 2.53)  (interest 2.53) 
 0.485752 Amburr90210  (photographer 3.45)  (premade 3.45)  (watermark 2.93)  (logo 2.81)  (personalized 2.81)  (include 2.41)  (else 2.24) 
 0.431513 CardsAndTreasures4U  (announcement 2.54)  (father 2.44)  (birthday 2.41)  (thinking 2.37)  (candle 2.37)  (distressed 2.37)  (raised 2.37)
 
Tf-Idf min listings = 2, listings only

CowgirlBroke  (shaped 2.99)  (cap 2.99)  (liqueur 2.76)  (cherry 2.76)  (label 2.53) 
  0.102 blackpearltraveller  (sterling 3.58)  (bead 3.21)  (1st 3.07)  (clay 2.95)  (authentic 2.93) 
  0.086 ABitofJewelry  (coordinating 2.89)  (polymer 2.82)  (paisley 2.45)  (ares 2.45)  (consists 2.37) 
  0.083 JLACreatives  (bracelet 2.81)  (7in 2.73)  (stretch 2.69)  (beadwork 2.57)  (parachord 2.53) 
  0.079 Skwirmmy  (plated 3.5)  (oriental 3.28)  (chinese 2.63)  (zen 2.63)  (japanese 2.63) 
  0.072 OnParkStreet  (birdhouse 3.78)  (maine 3.61)  (cultured 3.45)  (silk 3.12)  (sea 3.0) 

SouthernVisionDistr  (phillips 3.13)  (safety 3.03)  (protection 3.03)  (contrast 2.85)  (ace 2.85) 
  0.053 MikesBazaar  (reel 3.11)  (gay 3.11)  (billy 2.97)  (anatomically 2.97)  (proud 2.84) 
  0.048 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68) 
  0.042 DreadFallCreations  (falls 3.91)  (braided 2.76)  (braids 2.6)  (hair 2.6)  (thinner 2.45) 
  0.042 CraftyKam  (lacy 3.07)  (crocheted 3.07)  (metallic 3.07)  (mauve 2.87)  (crochet 2.87) 
  0.04 ThreeCordsDesigns  (reclaimed 2.87)  (mill 2.49)  (enough 2.49)  (military 2.49)  (smoothed 2.49) 

MrsJulians  (cake 3.91)  (diapers 3.74)  (diaper 3.3)  (tier 3.02)  (onesies 2.73) 
  0.111 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68) 
  0.094 BabyBearLoveCrafts  (dessert 3.83)  (table 3.21)  (runner 2.81)  (briefly 2.55)  (striped 2.43) 
  0.089 WhiteheadsWonderfuly  (tutu 4.22)  (tulle 3.91)  (customize 3.26)  (door 2.93)  (wreaths 2.87) 
  0.086 Lynniesccreations  (taggies 3.07)  (taggie 3.07)  (lovies 2.81)  (minky 2.55)  (taggy 2.55) 
  0.078 Fourtifor  (customer 2.5)  (delivery 2.5)  (34 2.34)  (paramore 2.33)  (vader 2.33) 

CraftyKam  (lacy 3.07)  (crocheted 3.07)  (metallic 3.07)  (mauve 2.87)  (crochet 2.87) 
  0.114 Vintagelacellc  (chiffon 3.91)  (wool 3.28)  (neckline 3.28)  (flowy 3.28)  (elbow 2.96) 
  0.092 DreadFallCreations  (falls 3.91)  (braided 2.76)  (braids 2.6)  (hair 2.6)  (thinner 2.45) 
  0.082 WindowsAndWings  (linocut 3.22)  (comical 3.1)  (heavy 2.88)  (lino 2.87)  (curiosity 2.87) 
  0.08 CreatedbyKathi  (scarves 3.74)  (scarf 3.21)  (infinity 3.16)  (upcycled 2.93)  (percent 2.59) 
  0.069 AlexandrasAnchor  (cowboy 3.49)  (western 3.45)  (nursery 2.75)  (guaranteed 2.63)  (satisfaction 2.63) 

CardsAndTreasures4U  (card 2.99)  (blank 2.6)  (write 2.58)  (birthday 2.53)  (fathers 2.47) 
  0.14 BoyHeartsGirl  (neutral 3.68)  (greeting 3.52)  (chlorine 3.22)  (ph 3.22)  (card 2.99) 
  0.118 PuddlesCards  (card 2.99)  (recycled 2.67)  (thoughts 2.62)  (padded 2.48)  (somebody 2.48) 
  0.093 AlexandrasAnchor  (cowboy 3.49)  (western 3.45)  (nursery 2.75)  (guaranteed 2.63)  (satisfaction 2.63) 
  0.088 BabyBearLoveCrafts  (dessert 3.83)  (table 3.21)  (runner 2.81)  (briefly 2.55)  (striped 2.43) 
  0.087 TheoandIvy  (cup 3.91)  (mug 2.8)  (china 2.8)  (scrubbing 2.7)  (refrain 2.7) 

PhotosbySutter  (dandelion 4.6)  (hiking 3.45)  (false 3.45)  (texas 3.45)  (north 3.45) 
  0.069 DanielleArtwork  (photographs 3.68)  (abstract 3.52)  (beach 3.13)  (photography 2.96)  (photoshop 2.76) 
  0.063 VisionsArts  (montana 3.86)  (fog 3.28)  (horse 3.28)  (river 3.12)  (morning 2.93) 
  0.055 AlfredFoxArt  (pixels 2.71)  (posters 2.71)  (download 2.61)  (alfredfox 2.5)  (kb 2.5) 
  0.047 OneStopShopbySophia  (moroccan 4.02)  (morocco 3.02)  (pendant 2.81)  (spice 2.73)  (directly 2.59) 
  0.044 ThreeCordsDesigns  (reclaimed 2.87)  (mill 2.49)  (enough 2.49)  (military 2.49)  (smoothed 2.49) 
  
   
Tf-Idf min listings = 2

CowgirlBroke  (shaped 2.99)  (cap 2.99)  (liqueur 2.76)  (cherry 2.76)  (label 2.53) 
  0.102 blackpearltraveller  (sterling 3.58)  (bead 3.21)  (1st 3.07)  (clay 2.95)  (authentic 2.93) 
  0.087 ABitofJewelry  (coordinating 2.89)  (polymer 2.82)  (paisley 2.45)  (ares 2.45)  (consists 2.37) 
  0.083 JLACreatives  (bracelet 2.81)  (7in 2.73)  (stretch 2.69)  (beadwork 2.57)  (parachord 2.53) 
  0.079 Skwirmmy  (plated 3.5)  (oriental 3.28)  (chinese 2.63)  (zen 2.63)  (japanese 2.63) 
  0.074 OnParkStreet  (birdhouse 3.78)  (maine 3.61)  (cultured 3.45)  (flatware 2.96)  (claw 2.79) 

SouthernVisionDistr  (phillips 3.13)  (safety 3.03)  (protection 3.03)  (contrast 2.85)  (ace 2.85) 
  0.054 MikesBazaar  (reel 3.11)  (gay 3.11)  (billy 2.97)  (anatomically 2.97)  (proud 2.84) 
  0.048 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68) 
  0.044 ThreeCordsDesigns  (reclaimed 2.87)  (mill 2.49)  (enough 2.49)  (military 2.49)  (smoothed 2.49) 
  0.04 oweeDesign  (customer 2.5)  (delivery 2.5)  (woke 2.36)  (expecto 2.33)  (glen 2.33) 
  0.04 FlashyShades  (sunglasses 4.6)  (eyewear 3.23)  (shades 3.23)  (flashygirls 3.18)  (hollywood 2.65)

MrsJulians  (cake 3.91)  (diapers 3.74)  (diaper 3.3)  (tier 3.02)  (onesies 2.73) 
  0.109 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68) 
  0.101 Lynniesccreations  (taggies 3.07)  (taggie 3.07)  (lovies 2.81)  (minky 2.55)  (taggy 2.55) 
  0.093 BabyBearLoveCrafts  (dessert 3.83)  (table 3.21)  (runner 2.81)  (briefly 2.55)  (striped 2.43) 
  0.086 WhiteheadsWonderfuly  (tutu 4.22)  (tulle 3.91)  (customize 3.26)  (door 2.93)  (wreaths 2.87) 
  0.085 AlleyCatShop  (indicate 2.83)  (birth 2.77)  (emailed 2.71)  (bend 2.71)  (christening 2.59) 
  
CraftyKam  (lacy 3.07)  (metallic 3.07)  (crocheted 3.07)  (mauve 2.87)  (crochet 2.87) 
  0.106 CreatedbyKathi  (scarf 3.21)  (scarves 3.17)  (infinity 3.16)  (upcycled 2.93)  (percent 2.59) 
  0.1 Vintagelacellc  (chiffon 3.91)  (neckline 3.28)  (flowy 3.28)  (newbie 2.96)  (supplies 2.96) 
  0.086 DreadFallCreations  (falls 3.91)  (hair 2.86)  (braided 2.76)  (braids 2.6)  (thinner 2.45) 
  0.076 WindowsAndWings  (linocut 3.22)  (comical 3.1)  (heavy 2.88)  (lino 2.87)  (curiosity 2.87) 
  0.069 MomandToby  (jar 3.16)  (mason 2.87)  (spare 2.87)  (trying 2.87)  (expand 2.87) 

PhotosbySutter  (dandelion 4.6)  (hiking 3.45)  (false 3.45)  (texas 3.42)  (photography 3.06) 
  0.066 DanielleArtwork  (photographs 3.68)  (abstract 3.52)  (photography 2.96)  (photoshop 2.76)  (scanned 2.76) 
  0.063 VisionsArts  (montana 3.86)  (fog 3.28)  (horse 3.28)  (river 3.12)  (morning 2.93) 
  0.055 AlfredFoxArt  (pixels 2.71)  (posters 2.71)  (download 2.61)  (alfredfox 2.5)  (kb 2.5) 
  0.051 FiestyAnaconda  (stitch 3.97)  (cm 3.32)  (ct 3.1)  (pdf 2.93)  (cross 2.77) 
  0.049 AlleyCatShop  (indicate 2.83)  (birth 2.77)  (emailed 2.71)  (bend 2.71)  (christening 2.59) 

CardsAndTreasures4U  (card 2.99)  (blank 2.6)  (write 2.58)  (fathers 2.47)  (reads 2.47) 
  0.133 BoyHeartsGirl  (neutral 3.63)  (greeting 3.53)  (chlorine 3.18)  (ph 3.18)  (account 3.01) 
  0.117 PuddlesCards  (card 2.99)  (recycled 2.67)  (thoughts 2.62)  (padded 2.48)  (somebody 2.48) 
  0.093 AlexandrasAnchor  (cowboy 3.49)  (western 3.45)  (nursery 2.75)  (guaranteed 2.63)  (satisfaction 2.63) 
  0.089 AlleyCatShop  (indicate 2.83)  (birth 2.77)  (emailed 2.71)  (bend 2.71)  (christening 2.59) 
  0.087 BabyBearLoveCrafts  (dessert 3.83)  (table 3.21)  (runner 2.81)  (briefly 2.55)  (striped 2.43) 

SweetDreamGirlz  (sugar 3.55)  (scrub 3.13)  (skincare 2.72)  (tween 2.72)  (teen 2.72) 
  0.097 TheLifeofaDoll  (makeup 4.12)  (extract 3.51)  (grape 3.45)  (jojoba 3.39)  (aloha 3.09) 
  0.091 ScentStop  (balm 3.92)  (castor 3.58)  (wax 3.32)  (beeswax 3.07)  (candelilla 2.81) 
  0.036 Vintagelacellc  (chiffon 3.91)  (neckline 3.28)  (flowy 3.28)  (newbie 2.96)  (supplies 2.96) 
  0.035 VeronicaAngelPoetry  (poem 4.6)  (veronica 3.83)  (poems 3.35)  (angel 2.92)  (poetry 2.87) 
  0.03 Lynniesccreations  (taggies 3.07)  (taggie 3.07)  (lovies 2.81)  (minky 2.55)  (taggy 2.55) 
  
TombstoneGameCalls  (call 4.6)  (calls 4.6)  (turkey 3.91)  (hunter 3.01)  (tombstone 3.01) 
  0.077 BAGSnBLESSINGS  (clutch 4.32)  (duck 3.36)  (ducktape 3.26)  (tape 3.21)  (petal 2.85) 
  0.064 CraftyKam  (lacy 3.07)  (metallic 3.07)  (crocheted 3.07)  (mauve 2.87)  (crochet 2.87) 
  0.063 allwoodenwalldecor  (palette 3.22)  (planks 3.22)  (customizable 2.99)  (templates 2.76)  (x20 2.76) 
  0.059 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68) 
  0.058 BrooklandHandmade  (stain 3.32)  (dc 3.32)  (table 3.21)  (pallet 2.81)  (ne 2.81) 
    
LSI min listings = 2

CowgirlBroke  (shaped 2.99)  (cap 2.99)  (liqueur 2.76)  (cherry 2.76)  (label 2.53)  (necklace 2.2)  (diamond 2.09) 
 0.703609 TotemWerks  (brooch 2.76)  (bell 2.6)  (nib 2.6)  (disk 2.53)  (surrounded 2.53)  (washer 2.53)  (statement 2.53) 
 0.62054 ABitofJewelry  (coordinating 2.89)  (polymer 2.82)  (paisley 2.45)  (consists 2.37)  (tri 2.37)  (accemts 2.37)  (dusty 2.37) 
 0.573942 blackpearltraveller  (sterling 3.17)  (1st 2.87)  (authentic 2.68)  (brass 2.68)  (bronze 2.62)  (clay 2.61)  (acessories 2.59) 
 0.545132 Zzebrarose  (czech 2.91)  (toggle 2.91)  (keepsake 2.91)  (millefiori 2.91)  (cabochon 2.76)  (woodland 2.68)  (decoupaged 2.68) 
 0.539125 TheeHotPinkBoutique  (bodycon 2.68)  (bamboo 2.57)  (spandex 2.57)  (hoop 2.52)  (jumpsuit 2.46)  (bad 2.46)  (bitchz 2.46) 
 
SouthernVisionDistr  (phillips 3.07)  (safety 2.98)  (protection 2.98)  (enhancement 2.81)  (contrast 2.81)  (ace 2.81)  (earth 2.64) 
 0.440521 FlashyShades  (sunglass 4.6)  (eyewear 3.23)  (flashygirls 3.18)  (shade 3.09)  (hollywood 2.65)  (regency 2.65)  (proflin 2.47) 
 0.417315 AppliedMachiningTech  (wine 3.91)  (machined 3.32)  (aluminum 3.32)  (holder 3.26)  (6061 2.81)  (candle 2.6)  (fixture 2.55) 
 0.39269 OnParkStreet  (birdhouse 3.78)  (maine 3.61)  (cultured 3.45)  (flatware 2.96)  (claw 2.79)  (sea 2.75)  (silk 2.65) 
 0.385615 PhotoGemsJewelry  (bronze 3.5)  (attractive 3.16)  (setting 2.93)  (packaged 2.87)  (photogems 2.87)  (cove 2.68)  (pendant 2.63) 
 0.251568 FoxGloveFlower  (sketchbook 2.94)  (colour 2.85)  (trade 2.67)  (fair 2.67)  (journal 2.57)  (alignment 2.48)  (scrapbook 2.48) 
 
MrsJulians  (diaper 3.91)  (cake 3.44)  (tier 2.85)  (onesies 2.63)  (environment 2.52)  (potentially 2.52)  (usable 2.52) 
 0.744557 Lynniesccreations  (taggies 2.93)  (taggie 2.93)  (lovies 2.72)  (minky 2.51)  (taggy 2.51)  (baby 2.2)  (washable 2.13) 
 0.687379 CherryTreeMonograms  (monogrammed 3.34)  (seersucker 2.87)  (serve 2.87)  (opportunity 2.78)  (diaper 2.68)  (ruffled 2.68)  (backpack 2.6) 
 0.376343 AlexandrasAnchor  (cowboy 3.49)  (western 3.45)  (nursery 2.75)  (guaranteed 2.63)  (satisfaction 2.63)  (biblical 2.63)  (teaching 2.46) 
 0.268279 BabyBearLoveCrafts  (dessert 3.83)  (table 3.21)  (runner 2.81)  (briefly 2.55)  (striped 2.43)  (complement 2.43)  (papermaking 2.43) 
 0.231675 groogrux41  (price 2.8)  (firedancers 2.76)  (giver 2.76)  (possibility 2.76)  (hemp 2.76)  (endless 2.76)  (myself 2.76) 

CraftyKam  (lacy 3.07)  (crocheted 3.07)  (metallic 3.07)  (ruffle 2.92)  (mauve 2.87)  (crochet 2.87)  (scarf 2.81) 
 0.806789 CreatedbyKathi  (scarf 3.21)  (infinity 2.83)  (upcycled 2.55)  (percent 2.47)  (twisting 2.47)  (stretchy 1.88)  (stylish 1.88) 
 0.378412 Vintagelacellc  (chiffon 3.91)  (neckline 3.28)  (flowy 3.28)  (newbie 2.96)  (success 2.96)  (elbow 2.96)  (cowl 2.96) 
 0.223842 BelleandBuck  (flannel 3.5)  (curved 3.07)  (attachment 3.07)  (soother 3.07)  (infant 2.68)  (enclosure 2.68)  (tail 2.68) 
 0.223081 DreadFallCreations  (hair 2.86)  (fall 2.81)  (braided 2.76)  (braid 2.6)  (thinner 2.45)  (human 2.45)  (thicker 2.45) 
 0.186522 TheeHotPinkBoutique  (bodycon 2.68)  (bamboo 2.57)  (spandex 2.57)  (hoop 2.52)  (jumpsuit 2.46)  (bad 2.46)  (bitchz 2.46) 
 
PhotosbySutter  (dandelion 4.6)  (hiking 3.45)  (false 3.45)  (texas 3.45)  (north 3.45)  (photography 3.06)  (watermark 2.93) 
 0.62294 VisionsArts  (montana 3.86)  (fog 3.28)  (horse 3.28)  (river 3.12)  (morning 2.93)  (sunrise 2.87)  (camera 2.79) 
 0.570169 DanielleArtwork  (abstract 3.52)  (photograph 3.52)  (beach 3.13)  (photography 2.96)  (photoshop 2.76)  (scanned 2.76)  (a4 2.76) 
 0.301802 AlfredFoxArt  (pixel 2.71)  (download 2.61)  (alfredfox 2.5)  (leisure 2.5)  (3949 2.5)  (licensed 2.5)  (colourful 2.5) 
 0.281179 ThreeCordsDesigns  (reclaimed 2.87)  (mill 2.49)  (enough 2.49)  (splinter 2.49)  (soldier 2.49)  (military 2.49)  (smoothed 2.49) 
 0.236458 LisaReneeArt  (soldering 3.07)  (woodart 2.87)  (vibe 2.87)  (rasta 2.87)  (burning 2.6)  (iron 2.6)  (woodburning 2.49) 

CardsAndTreasures4U  (card 2.65)  (write 2.47)  (father 2.44)  (thinking 2.37)  (raised 2.37)  (ringtones 2.33)  (wishing 2.33) 
 0.929913 BoyHeartsGirl  (neutral 2.99)  (chlorine 2.76)  (ph 2.76)  (greeting 2.73)  (card 2.65)  (account 2.62)  (fade 2.53) 
 0.909228 PuddlesCards  (card 2.65)  (recycled 2.59)  (embellishment 2.59)  (padded 2.45)  (somebody 2.45)  (handwritten 2.45)  (completely 2.45) 
 0.216329 Lynniesccreations  (taggies 2.93)  (taggie 2.93)  (lovies 2.72)  (minky 2.51)  (taggy 2.51)  (baby 2.2)  (washable 2.13) 
 0.19612 MrsJulians  (diaper 3.91)  (cake 3.44)  (tier 2.85)  (onesies 2.63)  (environment 2.52)  (potentially 2.52)  (usable 2.52) 
 0.189772 FoxGloveFlower  (sketchbook 2.94)  (colour 2.85)  (trade 2.67)  (fair 2.67)  (journal 2.57)  (alignment 2.48)  (scrapbook 2.48) 

SweetDreamGirlz  (sugar 3.55)  (scrub 3.13)  (skincare 2.72)  (tween 2.72)  (teen 2.72)  (safflower 2.51)  (ceteth 2.51) 
 0.718202 TheLifeofaDoll  (makeup 3.77)  (extract 3.28)  (grape 3.23)  (jojoba 3.18)  (aloha 2.93)  (lacquer 2.89)  (oil 2.81) 
 0.620402 ScentStop  (balm 3.83)  (castor 3.58)  (wax 3.32)  (beeswax 3.07)  (candelilla 2.81)  (flavor 2.81)  (lipid 2.81) 
 0.225151 WindowsAndWings  (linocut 3.17)  (comical 3.07)  (ostrich 2.85)  (lino 2.85)  (curiosity 2.85)  (heavy 2.84)  (flamingo 2.63) 
 0.181511 Vintagelacellc  (chiffon 3.91)  (neckline 3.28)  (flowy 3.28)  (newbie 2.96)  (success 2.96)  (elbow 2.96)  (cowl 2.96) 
 0.173878 VisionsArts  (montana 3.86)  (fog 3.28)  (horse 3.28)  (river 3.12)  (morning 2.93)  (sunrise 2.87)  (camera 2.79) 

TombstoneGameCalls  (call 4.6)  (turkey 2.93)  (hunter 2.65)  (tombstone 2.65)  (reed 2.56)  (trumpet 2.56)  (combo 2.47) 
 0.306544 BAGSnBLESSINGS  (clutch 4.32)  (duck 3.36)  (ducktape 3.26)  (tape 3.21)  (petal 2.9)  (purse 2.7)  (school 2.67) 
 0.166799 TheeHotPinkBoutique  (bodycon 2.68)  (bamboo 2.57)  (spandex 2.57)  (hoop 2.52)  (jumpsuit 2.46)  (bad 2.46)  (bitchz 2.46) 
 0.155574 kozysac  (throw 4.27)  (pillow 3.63)  (warm 3.07)  (attached 3.0)  (kosysacs 2.96)  (kozysac 2.96)  (sleeping 2.96) 
 0.149302 groogrux41  (price 2.8)  (firedancers 2.76)  (giver 2.76)  (possibility 2.76)  (hemp 2.76)  (endless 2.76)  (myself 2.76) 
 0.133157 vttop  (sending 3.07)  (teenage 2.68)  (poly 2.68)  (next 2.49)  (except 2.49)  (australia 2.49)  (tee 2.49) 
