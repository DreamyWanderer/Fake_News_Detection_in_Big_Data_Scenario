from os import pipe
import pip
import pymongo

import nltk
import re
# from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from pyvi import ViTokenizer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

uri = "mongodb://dreamywanderer:fIheB7sQzEsjH3U6WXmOXoVP1Hj79V4Xom1pNV0uHNbNBal0Lx75X6fwSovFOxXFftvFAMsf5SGoACDboPqXRA==@dreamywanderer.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@dreamywanderer@"

client = pymongo.MongoClient(uri)
NewsDataset = client['NewsDataset']

# Get name of all existing collections in the NewsDataset
print(NewsDataset.list_collection_names())

exist_collection = NewsDataset.list_collection_names()
VNFD = NewsDataset['VNFD']


VNFDPreprocessed = NewsDataset['VNFDPreprocessed']
# Remove stop words vietnamese using vietnamese-stopwords.txt
stopwords_filepath = './Preprocessing/vietnamese-stopwords.txt'

# # Preprocessing text content(`content`) in the collection VNFD using tokenization, lemmatization, and stopword removal
# Define preprocessing steps as functions

# Lowercasing
def lowercase(text):
    return text.lower()

# Tokenization
def tokenize(text):
    return word_tokenize(ViTokenizer.tokenize(text))

# Remove stop words
def remove_stopwords(text):
    stop_words = set(line.strip() for line in open(stopwords_filepath, encoding="utf8"))
    return [w for w in text if not w in stop_words]

# Remove punctuation
def remove_punctuation(text):
    return [re.sub(r'[^\w\s]', '', word) for word in text if not re.sub(r'[^\w\s]', '', word) == '']

# Lemmatization
def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in text]

# Stemming
def stemming(text):
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in text]

# Define preprocessing pipeline function

def preprocess_text(text, steps):
    for step in steps:
        text = step(text)
    return text



# Fine-tune preprocessing pipeline here 
pipeline_steps = [lowercase, tokenize, remove_stopwords, remove_punctuation, lemmatize, stemming]
# pipeline_steps = [lowercase, tokenize]



for collection in exist_collection:
    if (collection == 'VNFDPreprocessed'):
        continue
    print(collection)
    try:
        for doc in NewsDataset[collection].find():
            if (doc['content'] == None):
                continue
            doc['content'] = preprocess_text(doc['content'], pipeline_steps)
            # print(doc)
            # Insert or update one document in the collection VNFDPreprocessed
            VNFDPreprocessed.update_one({'_id': doc['_id']}, {"$set": doc}, upsert=True)
    except:
        print("Error when preprocessing collection", collection)
        continue

    

