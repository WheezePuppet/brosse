#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 16:19:57 2018

@author: bryceanderson
"""

import nltk
from nltk.corpus import stopwords
from nltk.corpus import PlaintextCorpusReader
import operator
import random
#%% Functions
port = nltk.PorterStemmer()
def update_stopwords(aset):
    aset.add("'s")
    aset.add("n't")
    aset.add("'m")
    aset.add("dont")
    aset.add("im")
    return aset
def prettify(strings):
    strings = strings.replace(",","")
    strings = strings.replace("'","")
    strings = strings.replace("."," ")
    strings = strings.replace("!"," ")
    strings = strings.replace("?"," ")
    strings = strings.replace('"',"")
    strings = strings.replace(";","")
    strings = strings.replace(":","")
    strings = strings.replace("\n"," ")
    strings = strings.replace("(","")
    strings = strings.replace(")","")
    strings = strings.replace("`","")
    strings = strings.replace('\'',"")
    strings = strings.replace("/", "")
    strings = strings.lower()
    return strings

def cleanup(Corpus):
    words = []
    text = []
    for file in Corpus.fileids():
        temp = Corpus.raw(file)
        temp = prettify(temp)
        words.append(temp)
        text.append(nltk.Text(nltk.word_tokenize(temp)))
    return words, text

def portStem(listofStrings):
    for i in range(len(listofStrings)):
        temp = ""
        for word in listofStrings[i].split(" "):
            temp += port.stem(word) + " "
        listofStrings[i] = temp
    return listofStrings
def noHandles(string):
    tm = ""
    text = string
    words = [word for word in text.split(" ") if "@" not in word]
    for word in words:
        tm += word + " "
    return tm
def noStopWords(string):
    tm = ""
    text = string
    words = [word for word in text.split(" ") if word not in stopwords.words('english')]
    for word in words:
        tm += word + " "
    return tm
#%%
corpus_root = "/Users/bryceanderson/Desktop/brosse/TwitterStuff"
DemCorpus = PlaintextCorpusReader("./Democrat",".*\.txt")
RepCorpus = PlaintextCorpusReader("./Republican",".*\.txt")
print("cleaning up dems...")
demWords, demText = cleanup(DemCorpus)
print("cleaning up reps...")
repWords, repText = cleanup(RepCorpus)
#%%
print("getting dem words...")
for i in range(len(demWords)):
    demWords[i] = noHandles(demWords[i])
    demWords[i] = noStopWords(demWords[i])
print("getting rep words...")
for i in range(len(repWords)):
    repWords[i] = noHandles(repWords[i])
    repWords[i] = noStopWords(repWords[i])
print("stemming dems...")
demWords = portStem(demWords)
print("stemming reps...")
repWords = portStem(repWords)
print("building freqdist...")
totVocab = nltk.FreqDist(nltk.word_tokenize(" ".join(demWords))) + nltk.FreqDist(nltk.word_tokenize(" ".join(repWords)))

#%%
sortedVocab = sorted(totVocab.items(), reverse=True, key=operator.itemgetter(1))
print("building word features...")
word_features = list(sortedVocab)[:int(len(totVocab)*.01)]
def getFeatures(text):
    words = set(text)
    features = {}
    for word in word_features:
        features["has({})".format(word[0])] = (word[0] in words)
    return features
featureset = [(getFeatures(t), 'D') for t in demText]
featureset += [(getFeatures(t), 'R') for t in repText]
random.shuffle(featureset)
ntrain = int(len(featureset))
trainset = featureset[:ntrain]
k = 100
subSize = int(len(trainset)/k)
perc = []
# if len(trainset) = 500, k = 10, subSize = 50
for j in range(10):
    for i in range(k):
        print("Testing slice " + str(i) + "...")
        correct = 0
        test = trainset[i*subSize:][:subSize]
        train = trainset[:i*subSize] + trainset[(i+1)*subSize:]
        classifier = nltk.NaiveBayesClassifier.train(train)
        for item in test:
            choice = ""
            probD = classifier.prob_classify(item[0]).prob('D')
            probR = classifier.prob_classify(item[0]).prob('R')
            if probD > probR:
                choice = 'D'
            else:
                choice = 'R'
            if choice == item[1]:
                correct+=1
        perc.append((correct/len(test))*100)
print(perc)
classifier.show_most_informative_features(50)
