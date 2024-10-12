# -*- coding: utf-8 -*-
"""Copy of GST.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DAqk9x4G9QmMw4SMoOxeS-T8x9QQl7ju
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

X_train=pd.read_csv("/content/X_Train_Data_Input.csv")
Y_train=pd.read_csv("/content/Y_Train_Data_Target.csv")
X_test=pd.read_csv("/content/X_Test_Data_Input.csv")
Y_test=pd.read_csv("/content/Y_Test_Data_Target.csv")

"""# Initial Data Exploration

"""

X_train.head(10)

Y_train.head(10)

print("\nShape of the X_train")
print(X_train.shape)

print("\nShape of the Y_train")
print(Y_train.shape)

print("\nSummary statistics of numerical columns:")
X_train.describe().T

"""#Data Preprocessing and  Exploratory Data Analysis (EDA)"""

# Check for Missing Values
X_train.isnull().sum()/X_train.shape[0]*100

Y_train.isnull().sum()/Y_train.shape[0]*100

# Visualize Missing Data
plt.figure(figsize=(10, 8))
sns.heatmap(X_train.isnull(),cbar=False, cmap="Blues" )
plt.title("Missing Data Heatmap")
plt.show()

#Dropping Unecessary Columns From X_train
X_train_new = X_train.drop(columns=['Column9', 'Column14','ID'])

X_train_new.columns

#Classify columns with small unique counts as categorical
unique_values = X_train_new.nunique()
categorical_col = unique_values[unique_values <= 12].index.tolist()  # Threshold of 12 is arbitrary
numerical_col = unique_values[unique_values > 12].index.tolist()
print(f"Categorical Columns: {categorical_col}")
print(f"Numerical Columns: {numerical_col}")

# Filling null values in the dataset by mean value
X_train_new[numerical_col] = X_train_new[numerical_col].fillna(X_train_new[numerical_col].mean())
X_train_new[categorical_col]=X_train_new[categorical_col].fillna(X_train_new[categorical_col].mode().iloc[0])

# Checking out the null values after replacing them
X_train_new.isnull().sum()/X_train.shape[0]*100

# plotinng box plot for numerical column
n_cols = 3  # Number of columns in the grid (you can adjust this)
n_rows = (len(numerical_col) + n_cols - 1) // n_cols  # Number of rows needed

# Create subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 5))

# Flatten axes array in case of more than 1 row and column
axes = axes.flatten()

# Plot each box plot in the corresponding subplot
for i, col in enumerate(numerical_col):
    sns.boxplot(x=X_train[col], palette="mako", ax=axes[i])
    axes[i].set_title(f'Box Plot of {col}')

# Remove any empty subplots
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# Removing Outliers from Numerical Columns (IQR method)

for column in numerical_col:
  # Calculate the IQR
  Q1 = X_train_new[column].quantile(0.25)
  Q3 = X_train_new[column].quantile(0.75)
  IQR = Q3 - Q1

  # Define the outlier boundaries
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR

  # Replace outliers with the mean
  X_train_new[column] = np.where(X_train_new[column] < lower_bound, X_train_new[column].mean(), X_train_new[column])
  X_train_new[column] = np.where(X_train_new[column] > upper_bound, X_train_new[column].mean(), X_train_new[column])

# plotinng box plot for numerical column after removing outliers

n_cols = 3  # Number of columns in the grid (you can adjust this)
n_rows = (len(numerical_col) + n_cols - 1) // n_cols  # Number of rows needed

# Create subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 5))

# Flatten axes array in case of more than 1 row and column
axes = axes.flatten()

# Plot each box plot in the corresponding subplot
for i, col in enumerate(numerical_col):
    sns.boxplot(x=X_train[col], palette="mako", ax=axes[i])
    axes[i].set_title(f'Box Plot of {col}')

# Remove any empty subplots
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# Generate histograms for numeric data

axes = X_train_new[numerical_col].hist(bins=20, figsize=(15, 10), color='skyblue', edgecolor='white', alpha=0.7)
plt.suptitle("Histograms of Numerical Columns")

# Disable the grid for each subplot
for ax in axes.flatten():
    ax.grid(False)

plt.show()

#Distribution of Categorical Variables

n_cols = 3  # Number of columns in the grid (adjustable)
n_rows = (len(categorical_col) + n_cols - 1) // n_cols  # Number of rows needed

# Create subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 5))

# Flatten axes array in case of more than 1 row and column
axes = axes.flatten()

# Plot each count plot in the corresponding subplot
for i, col in enumerate(categorical_col):
    sns.countplot(x=col, data=X_train, palette="mako", ax=axes[i])
    axes[i].set_title(f'Distribution of {col}')

# Remove any empty subplots
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

fig.suptitle('Distribution of Categorical Variables',fontsize=16, y=1.02)

plt.tight_layout()
plt.show()

# Target Variable Distribution
plt.figure(figsize=(6, 4))
sns.countplot(x='target', data=Y_train, palette='mako')
plt.title('Target Variable Distribution')
plt.show()

"""Data Highly Imbalanced

"""

# Combine the datasets for easier analysis
X_train_new = X_train_new.reset_index(drop=True)
Y_train = Y_train.reset_index(drop=True)
XY_train = pd.concat([X_train, Y_train.drop(columns=['ID'])], axis=1)
XY_train.head()

XY_train.columns

XY_train=XY_train.drop(columns=['ID'])

XY_train.shape

# Correlation Matrix and Heatmap
correlation_matrix = XY_train.corr()

# Plotting the heatmap for correlations
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='Blues', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()

"""# Preparing Target Variable

"""

Y_train_new = Y_train.drop(columns=['ID'])
print(f"Shape of X_train_new: {X_train_new.shape}")
print(f"Shape of Y_train_new: {Y_train_new.shape}")

X_train_new

"""#Splitting the Data into Train and Test

"""

X_new_train, X_new_test, Y_new_train, Y_new_test = train_test_split(X_train_new, Y_train_new, test_size=0.2, random_state=42)

"""#Resampling Using SMOTE"""

# Initialize the SMOTE object for oversampling
smote = SMOTE()

# Apply SMOTE only on the training data
X_train_resampled, y_train_resampled = smote.fit_resample(X_new_train, Y_new_train)

# Check the class distribution before and after
print("Before resampling:")
print(Y_new_train.value_counts())  # Original class distribution
y_train_resampled =np.array (y_train_resampled)
y_train_resampled=y_train_resampled.reshape(-1)


print("After resampling:")
print(pd.Series(y_train_resampled).value_counts())  # Resampled class distribution

# Train a model (e.g., Random Forest)
# model = RandomForestClassifier()
# model.fit(X_train_resampled, y_train_resampled)

"""#Training the data and finding the accuracy, Precison, Recall, F1 Score and Confusion Matrix"""

from sklearn.metrics import accuracy_score, classification_report, roc_curve, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_classifiers(models, X_train, y_train, X_test, y_test, plot_roc=True):
    results = {}
    plt.figure(figsize=(10, 8))

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate accuracy
        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy of {model_name}: {acc:.2f}")

        # Print classification report
        print(f"Classification Report for {model_name}:")
        print(classification_report(y_test, y_pred))

        # Calculate and display confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix for {model_name}:")
        print(cm)

        # Plot confusion matrix
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
        plt.title(f"Confusion Matrix for {model_name}")
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()

        # Store the results
        results[model_name] = {
            "Accuracy": acc,
            "Classification Report": classification_report(y_test, y_pred, output_dict=True),
            "Confusion Matrix": cm
        }

        # Plot ROC curve if the model supports probability estimates and plot_roc is True
        if hasattr(model, "predict_proba") and plot_roc:
            y_prob = model.predict_proba(X_test)[:, 1]
            fpr, tpr, thresholds = roc_curve(y_test, y_prob)
            auc_score = roc_auc_score(y_test, y_prob)
            print(f"AUC Score for {model_name}: {auc_score:.2f}")

            # Plot ROC curve
            plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc_score:.2f})')

    if plot_roc:
        # Plot settings
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Random model
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.show()

    return results

models = {
    "Random Forest": RandomForestClassifier()
    "SVM": SVC(probability=True),  # Use probability=True for SVM to enable ROC/AUC
    "K-Nearest Neighbors": KNeighborsClassifier()
}

results = evaluate_classifiers(models, X_train_resampled, y_train_resampled, X_new_test, Y_new_test)

"""#Prediction on testing data"""

# Make predictions on the test data
y_pred = model.predict(X_new_test)
print(classification_report(Y_new_test, y_pred))

X_test

X_test=pd.read_csv("/content/X_Test_Data_Input.csv")

X_test=X_test.drop(columns=['ID','Column9','Column14'])

#Classify columns with small unique counts as categorical
unique_values = X_test.nunique()
categorical_col = unique_values[unique_values <= 12].index.tolist()
numerical_col = unique_values[unique_values > 12].index.tolist()

# Filling null values in the dataset by mean value
X_test[numerical_col] = X_test[numerical_col].fillna(X_test[numerical_col].mean())
X_test[categorical_col]=X_test[categorical_col].fillna(X_test[categorical_col].mode().iloc[0])

X_test

"""#Testing model performance on Validation Data"""

from sklearn.metrics import accuracy_score, classification_report, roc_curve, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_classifiers(models, X_test, y_test, plot_roc=True):
    results = {}
    plt.figure(figsize=(10, 8))

    for model_name, model in models.items():
        # print(f"\nTraining {model_name}...")

        # Train the model
        # model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate accuracy
        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy of {model_name}: {acc:.2f}")

        # Print classification report
        print(f"Classification Report for {model_name}:")
        print(classification_report(y_test, y_pred))

        # Calculate and display confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"Confusion Matrix for {model_name}:")
        print(cm)

        # Plot confusion matrix
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
        plt.title(f"Confusion Matrix for {model_name}")
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()

        # Store the results
        results[model_name] = {
            "Accuracy": acc,
            "Classification Report": classification_report(y_test, y_pred, output_dict=True),
            "Confusion Matrix": cm
        }

        # Plot ROC curve if the model supports probability estimates and plot_roc is True
        if hasattr(model, "predict_proba") and plot_roc:
            y_prob = model.predict_proba(X_test)[:, 1]
            fpr, tpr, thresholds = roc_curve(y_test, y_prob)
            auc_score = roc_auc_score(y_test, y_prob)
            print(f"AUC Score for {model_name}: {auc_score:.2f}")

            # Plot ROC curve
            plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc_score:.2f})')

    if plot_roc:
        # Plot settings
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Random model
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.show()

    return results