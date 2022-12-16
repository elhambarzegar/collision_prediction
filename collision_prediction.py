import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
import os
from sklearn.metrics import confusion_matrix, classification_report
from sklearn import preprocessing
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
 
collisions = pd.DataFrame([])
for filename in os.scandir('./everyHour'):
    if filename.is_file() and '.csv' in filename.path:
        #print(filename.path)
        file = pd.read_csv(filename.path)
        collisions = pd.concat([collisions,file])

sc = preprocessing.StandardScaler()
le = preprocessing.LabelEncoder()

collisions['ACCLASS'] = collisions['ACCLASS'].fillna(False)
collisions.loc[collisions['ACCLASS'] != False, 'ACCLASS'] = True

collisions = collisions.drop(['VISIBILITY','LIGHT','LONGITUDE','LATITUDE','Unnamed: 0'], axis=1)

# create a Gradient for continuous parameters
collisions.fillna(method="ffill")
collisions.replace([np.inf, -np.inf], np.nan, inplace=True)
collisions = collisions.dropna()

#convert text values to enum
collisions['Weather'] = le.fit_transform(collisions['Weather'])

y = collisions['ACCLASS']
y = y.astype('int')
X = collisions.drop('ACCLASS', axis=1)
#standardize the feature scales
X = sc.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#define the weigh to increase the observation of positive class
weight_array = y_train
weight_array = weight_array *12 +1
gnb = GaussianNB(var_smoothing=0.0001)
gnb.fit(X_train, y_train, sample_weight = weight_array)

y_pred = gnb.predict(X_test)
cf_matrix = confusion_matrix(y_test,y_pred)

print('Classification report:\n',classification_report(y_test,y_pred))
print('Confusion matrix:\n',cf_matrix)
sns.heatmap(cf_matrix, annot=True)
plt.show()