# -*- coding: utf-8 -*-
"""ML_Lab1_Label3_190179M.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PhmjcOnZ-k8kNXPMl4L3CWxKphG2I1zj
"""

from google.colab import drive
drive.mount('/content/gdrive')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

trainData = pd.read_csv('/content/gdrive/MyDrive/Colab Notebooks/ML/Lab1/train.csv')
validData = pd.read_csv('/content/gdrive/MyDrive/Colab Notebooks/ML/Lab1/valid.csv')
testData = pd.read_csv('/content/gdrive/MyDrive/Colab Notebooks/ML/Lab1/test.csv')

trainData.head()

# Verify the presence of null values within the train data
trainNullCounts = trainData.isnull().sum()
print("Null counts in Train Data: \n {}".format(trainNullCounts))

# Remove rows with null values in the last four columns (target labels) of the train data
trainData = trainData.dropna(subset=trainData.columns[-4:], how='any')

# Replace null values with mean in datasets
trainData = trainData.fillna(trainData.mean())
validData = validData.fillna(validData.mean())
testData = testData.fillna(testData.mean())

trainData.head()

# Separate features and labels in datasets
trainFeatures = trainData.iloc[:, :-4]
trainLabels = trainData.iloc[:, -4:]
validFeatures = validData.iloc[:, :-4]
validLabels = validData.iloc[:, -4:]
testFeatures = testData.iloc[:, :-4]
testLabels = testData.iloc[:, -4:]

# Extract the first label of the datasets
trainLabel3 = trainLabels.iloc[:,2]
validLabel3 = validLabels.iloc[:,2]
testLabel3 = testLabels.iloc[:,2]

"""Prediction of Label 1 without Feature Engineering"""

# Make a copy features and labels in datasets
trainFeaturesCopy = trainFeatures.copy()
trainLabelsCopy = trainLabels.copy()
validFeaturesCopy = validFeatures.copy()
validLabelsCopy = validLabels.copy()
testFeaturesCopy = testFeatures.copy()
testLabelsCopy = testLabels.copy()

# Make a copy of the third label of the datasets
trainLabel3Copy = trainLabel3.copy()
validLabel3Copy = validLabel3.copy()
testLabel3Copy = testLabel3.copy()

testData.head()

# Standardize features
scaler = StandardScaler()
trainFeaturesCopy = scaler.fit_transform(trainFeaturesCopy)
validFeaturesCopy = scaler.transform(validFeaturesCopy)
testFeaturesCopy = scaler.transform(testFeaturesCopy)

model = KNeighborsClassifier()
model.fit(trainFeaturesCopy, trainLabel3Copy)

# Predict on train data
trainPredictionsBase = model.predict(trainFeaturesCopy)
trainDataAccuracy = accuracy_score(trainLabel3Copy, trainPredictionsBase)
trainDataPrecision = precision_score(trainLabel3Copy, trainPredictionsBase, average='weighted' , zero_division=1)
trainDataRecall = recall_score(trainLabel3Copy, trainPredictionsBase, average='weighted')
print(f"Performance Metrics for KNN on train data:")
print(f"  - Accuracy: {trainDataAccuracy:.2f}")
print(f"  - Precision: {trainDataPrecision:.2f}")
print(f"  - Recall: {trainDataRecall:.2f}\n")

# Predict on validation data
validPredictionsBase = model.predict(validFeaturesCopy)
validDataAccuracy = accuracy_score(validLabel3Copy, validPredictionsBase)
validDataPrecision = precision_score(validLabel3Copy, validPredictionsBase, average='weighted', zero_division=1)
validDataRecall = recall_score(validLabel3Copy, validPredictionsBase, average='weighted')
print(f"Performance Metrics for KNN on Validation Data:")
print(f"  - Accuracy: {validDataAccuracy:.2f}")
print(f"  - Precision: {validDataPrecision:.2f}")
print(f"  - Recall: {validDataRecall:.2f}\n")

# Predict on test data
testPredictionsBase = model.predict(testFeaturesCopy)

"""Prediction of Label 3 using Feature Engineering"""

# Plotting the distribution of train_label3
labels, counts = np.unique(trainLabel3, return_counts=True)

plt.figure(figsize=(10, 6))
plt.xticks(labels)
plt.bar(labels, counts)
plt.xlabel('Target Label 3')
plt.ylabel('Frequency')
plt.title('Frequency of Target Label 3')
plt.show()

#Compute the correlation matrix and create a heatmap
correlationMatrix = trainFeatures.corr()
mask = np.triu(np.ones_like(correlationMatrix))
plt.figure(figsize=(12, 12))
sns.heatmap(correlationMatrix, cmap='coolwarm', center=0, mask=mask)
plt.title("Correlation Matrix")
plt.show()

# Determine highly correlated features within the training dataset
correlationThreshold = 0.8
highlyCorrelated = set()
for i in range(len(correlationMatrix.columns)):
    for j in range(i):
        if abs(correlationMatrix.iloc[i, j]) > correlationThreshold:
            colname = correlationMatrix.columns[i]
            highlyCorrelated.add(colname)
print(highlyCorrelated)

# Exclude features that were previously identified as having high correlation from all datasets
trainFeatures = trainFeatures.drop(columns=highlyCorrelated)
validFeatures = validFeatures.drop(columns=highlyCorrelated)
testFeatures = testFeatures.drop(columns=highlyCorrelated)

# Display the filtered feature counts
print("Train features after filtering: {}".format(trainFeatures.shape))
print("Valid features after filtering: {}".format(validFeatures.shape))
print("Test features after filtering: {}".format(testFeatures.shape))

# Detect the attributes strongly linked to the target variable by analyzing the training dataset
correlationWithTarget = trainFeatures.corrwith(trainLabel3)
correlationThreshold = 0.06
highlyCorrelatedFeatures = correlationWithTarget[correlationWithTarget.abs() > correlationThreshold]
print(highlyCorrelatedFeatures)

# Drop the features with low correlation in the datasets
trainFeatures = trainFeatures[highlyCorrelatedFeatures.index]
validFeatures = validFeatures[highlyCorrelatedFeatures.index]
testFeatures = testFeatures[highlyCorrelatedFeatures.index]

# Display the filtered feature counts  of the datasets
print("Train features after filtering: {}".format(trainFeatures.shape))
print("Valid features after filtering: {}".format(validFeatures.shape))
print("Test features after filtering: {}".format(testFeatures.shape))

# Standardize the features
scaler = StandardScaler()
standardizedTrainFeatures = scaler.fit_transform(trainFeatures)
standardizedValidFeatures = scaler.transform(validFeatures)
standardizedTestFeatures = scaler.transform(testFeatures)

"""Feature Extraction"""

varianceThreshold = 0.95

# Apply PCA with the determined no. of components
pca = PCA(n_components=varianceThreshold, svd_solver='full')
pcaTrainResult = pca.fit_transform(standardizedTrainFeatures)
pcaValidResult = pca.transform(standardizedValidFeatures)
pcaTestResult = pca.transform(standardizedTestFeatures)

# Explained variance ratio after dimensionality reduction
explainedVarianceRatioReduced = pca.explained_variance_ratio_
print("Explained Variance Ratio following Dimensionality Reduction:", explainedVarianceRatioReduced)

# Visualize Variance Explained Ratio
plt.figure(figsize=(18, 10))
plt.bar(range(1, pcaTrainResult.shape[1] + 1), explainedVarianceRatioReduced)
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.title('Explained Variance Ratio for Each Principal Component (Reduced Dimensionality)')
plt.show()

# Display the reduced feature matrices
print("Shape of the Reduced Training Feature Matrix: {}".format(pcaTrainResult.shape))
print("Shape of the Reduced Validation Feature Matrix: {}".format(pcaValidResult.shape))
print("Shape of the Reduced Testing Feature Matrix: {}".format(pcaTestResult.shape))

"""Model Selection"""

classificationModels = [
    # ('Decision Tree', DecisionTreeClassifier()),
    ('K Neighbors', KNeighborsClassifier()),
    # ('Random Forest', RandomForestClassifier()),
    # ('SVM', SVC()),
    # ('XGBoost', XGBClassifier())
]

# All models exhibit strong performance. Opting for K-Nearest Neighbors (KNN).

featureNum = pcaTrainResult.shape[1]
print(f"No. of features: {featureNum}\n")

# Train and evaluate each classification model
for modelName, model in classificationModels:
    model.fit(pcaTrainResult, trainLabel3)
    predictionTrain = model.predict(pcaTrainResult)
    accuracy = accuracy_score(trainLabel3, predictionTrain)
    precision = precision_score(trainLabel3, predictionTrain, average='weighted' , zero_division=1)
    recall = recall_score(trainLabel3, predictionTrain, average='weighted')

    print(f"Metrics for {modelName} on train data:")
    print(f"  - Accuracy: {accuracy:.2f}")
    print(f"  - Precision: {precision:.2f}")
    print(f"  - Recall: {recall:.2f}\n")

    # Predict on the validation data
    predictionValid = model.predict(pcaValidResult)
    accuracy = accuracy_score(validLabel3, predictionValid)
    precision = precision_score(validLabel3, predictionValid, average='weighted', zero_division=1)
    recall = recall_score(validLabel3, predictionValid, average='weighted')

    print(f"Metrics for {modelName} on validation data:")
    print(f"  - Accuracy: {accuracy:.2f}")
    print(f"  - Precision: {precision:.2f}")
    print(f"  - Recall: {recall:.2f}\n")

    # Predict on the test data
    predictionTest = model.predict(pcaTestResult)

"""Generating CSV File"""

# define method to create the dataframe and save in a csv file
def generateCsv(features, predictionsBeforeFeatureEng, predictionsAfterFeatureEng, destination):
  featureCount = features.shape[1]
  headerRow = [f"new_feature_{i}" for i in range(1,featureCount+1)]
  df = pd.DataFrame(features, columns  = headerRow)
  df.insert(loc=0, column='Predicted labels before feature engineering', value=predictionsBeforeFeatureEng)
  df.insert(loc=1, column='Predicted labels after feature engineering', value=predictionsAfterFeatureEng)
  df.insert(loc=2, column='No. of new features', value=np.repeat(featureCount, features.shape[0]))
  df.to_csv(destination, index=False)

generateCsv(pcaTestResult, testPredictionsBase, predictionTest, '/content/gdrive/MyDrive/Colab Notebooks/ML/Lab1/190179M_label_3.csv')