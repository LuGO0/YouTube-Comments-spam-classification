# -*- coding: utf-8 -*-
"""YouTube Comment Classification .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15owrRrIrn4CHdyrW6Sw8YR3vWXcbJE9U
"""

import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_hub as hub

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt



#read dataset
Psy = pd.read_csv('Youtube01-Psy.csv')
Katy = pd.read_csv('Youtube02-KatyPerry.csv')
Eminem = pd.read_csv('Youtube04-Eminem.csv')
Shakira = pd.read_csv('Youtube05-Shakira.csv')
LMFAO = pd.read_csv('Youtube03-LMFAO.csv')

"""## PREPROCESSING"""

#date insignificant parameter

df = pd.concat([Shakira, Eminem, Katy, Psy, LMFAO])
df.drop('DATE', axis=1, inplace=True)

df.shape

df.head()

#class plot to compare number of data values of each class
df['CLASS'].value_counts().plot(kind='bar')

#balanced data check

classes = df['CLASS']
print(classes.value_counts())

text_messages = df["CONTENT"]

#REGEX TO ENCODE useless data as in emails, numbers etc into useful text features

# Replace email addresses with 'email'
processed = text_messages.str.replace(r'^.+@[^\.].*\.[a-z]{2,}$',
                                 'emailaddress')

# Replace URLs with 'webaddress'
processed = processed.str.replace(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$',
                                  'webaddress')

# Replace money symbols with 'moneysymb' 
processed = processed.str.replace(r'£|\$', 'moneysymb')
    
# Replace 10 digit phone numbers (formats include paranthesis, spaces, no spaces, dashes) with 'phonenumber'
processed = processed.str.replace(r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$',
                                  'phonenumbr')
    
# Replace numbers with 'numbr'
processed = processed.str.replace(r'\d+(\.\d+)?', 'numbr')

print(text_messages[:10])

processed = processed.str.replace(r'[^\w\d\s]', ' ')

# Replace whitespace between terms with a single space
processed = processed.str.replace(r'\s+', ' ')

# Remove leading and trailing whitespace
processed = processed.str.replace(r'^\s+|\s+?$', '')

processed = processed.str.lower()
print(processed)

#nlp


import nltk
nltk.download('punkt')
nltk.download('stopwords')

#stop words removal





from nltk.corpus import stopwords


stop_words = set(stopwords.words('english'))

processed = processed.apply(lambda x: ' '.join(
    term for term in x.split() if term not in stop_words))

#stemming

ps = nltk.PorterStemmer()

processed = processed.apply(lambda x: ' '.join(
    ps.stem(term) for term in x.split()))

#tokenising data helps detect patterns in data

from nltk.tokenize import word_tokenize

all_words = []

for message in processed:
    words = word_tokenize(message)
    for w in words:
        all_words.append(w)
        
all_words = nltk.FreqDist(all_words)

print('Number of words: {}'.format(len(all_words)))
print('Most common words: {}'.format(all_words.most_common(15)))

NO_OF_FEATURES=2000
word_features = list(all_words.keys())[:NO_OF_FEATURES]

#feature extraction based on top 1500 frequently occuring words

def find_features(message):
    words = word_tokenize(message)
    features = {}
    for word in word_features:
        features[word] = (word in words)

    return features

features = find_features(str(processed[0]))
for key, value in features.items():
    if value == True:
        print (key)

messages = list(zip(processed, classes))


#seeding to have similar shuffling for each run and hence prevent overfitting
seed = 1
np.random.seed = seed
np.random.shuffle(messages)

featuresets = [(find_features(text), label) for (text, label) in messages]

#split data into train and test for accuracy check later 

from sklearn import model_selection

training, testing = model_selection.train_test_split(featuresets, test_size = 0.25, random_state=seed)

print(len(training))
print(len(testing))

from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)



"""## MODEL COMPILATION AND CLASSIFYING"""

#accuracy of various classifiers checked to find the best model


from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

# Define models to train
names = ["K Nearest Neighbors", "Decision Tree", "Random Forest", "Logistic Regression", "SGD Classifier",
         "Naive Bayes", "SVM Linear"]

classifiers = [
    KNeighborsClassifier(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    LogisticRegression(),
    SGDClassifier(max_iter = 100),
    MultinomialNB(),
    SVC(kernel = 'linear')
]

models = zip(names, classifiers)
names1 = []
results = []

#model evaluation
for name, model in models:
    nltk_model = SklearnClassifier(model)
    nltk_model.train(training)
    accuracy = nltk.classify.accuracy(nltk_model, testing)*100
 
        
    print("{} Accuracy: {}".format(name, accuracy))
    names1.append(name)
    results.append(accuracy)

"""## **EVALUATION**"""

values=list(range(0,7))
plt.plot(results,names,'go--')

plt.show()
plt.savefig("2000-features.jpg")

txt_features, labels = zip(*testing)



#max_accurate model
#final results to be obtained with highest accuracy model
index=results.index(max(results))
best_model=classifiers[index]
print(best_model)

nltk_model=SklearnClassifier(best_model)
nltk_model.train(training)
prediction = nltk_model.classify_many(txt_features)
print(nltk_model)

# print a confusion matrix and a classification report
print(classification_report(labels, prediction))

pd.DataFrame(
    confusion_matrix(labels, prediction),
    index = [['actual', 'actual'], ['ham', 'spam']],
    columns = [['predicted', 'predicted'], ['ham', 'spam']])

"""### IMPROVEMENTS

#### 1.DEEP LEARNING FEATURE FUNCTION
####(Count Vectorisation implemented)
"""

#VALIDATION
#DEEP LEARNING MODEL

NO_OF_FEATURES=2250
word_features = list(all_words.keys())[:NO_OF_FEATURES]


def find_features_dl(message):
    words = word_tokenize(message)
    features = []
    for word in word_features:
        features.append(1 if (word in words) else 0)

    return features

features = find_features_dl(str(processed[0]))

messages = list(zip(processed, classes))
print(len(messages))

seed = 1
np.random.seed = seed
np.random.shuffle(messages)

featuresets = [(find_features_dl(text), label) for (text, label) in messages]

from sklearn import model_selection

training, testing = model_selection.train_test_split(featuresets, test_size = 0.25, random_state=seed)
print(len(training))

len_train=len(training)
validation=training[1100:]
training=training[:1100]

print(len(training))
print(len(validation))

X_train=[]
Y_train=[]
for i in training:
    X_train.append(i[0])
    Y_train.append(i[1])



X_test=[]
Y_test=[]
for i in testing:
    X_test.append(i[0])
    Y_test.append(i[1])

"""GETTING VALIDATION DATA FOR TUNING"""

X_validation=[]
Y_validation=[]
for i in validation:
    X_validation.append(i[0])
    Y_validation.append(i[1])

model=tf.keras.Sequential([
    tf.keras.layers.Dense(16,input_dim=NO_OF_FEATURES,activation='relu'),
    tf.keras.layers.Dense(8,activation='relu'),
    tf.keras.layers.Dense(1,activation='sigmoid')
])

model.summary()

#adam optimiser used to handle minima in non convex funtions

model.compile(optimizer='adam',loss=tf.keras.losses.BinaryCrossentropy(),metrics=['accuracy',tf.keras.metrics.Precision(),tf.keras.metrics.Recall()])

print(len(validation))

history=model.fit(X_train,Y_train,epochs=10,validation_data=(X_validation,Y_validation),batch_size=64)

loss,accuracy,precision,recall= model.evaluate(X_test, Y_test, verbose=False)

print("loss: ",loss,"accuracy: ",accuracy,"precision: ",precision,"recall: ",recall)

print(history.history.keys())