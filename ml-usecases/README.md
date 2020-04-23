# Machine Learning, Case Studies

Throughout this course, we’ll be focusing on deployment tools and the machine learning workflow; answering a few big questions along the way:

1. How do you decide on the correct machine learning algorithm for a given task?
2. How can we utilize cloud ML services in SageMaker to work with interesting datasets or improve our algorithms?

To approach these questions, we’ll go over a number of real-world case studies, and go from task and problem formulation to deploying models in SageMaker. We’ll also utilize a number of SageMaker’s built-in algorithms.

## Population Segmentation

> Train and deploy unsupervised models(PCA and k-means clustering) to group US countries by similarities and differences. Visualize the trained model attributes and interpret the results

You’ll look at a portion of US census data and, using a combination of unsupervised learning methods, extract meaningful components from that data and group regions by similar census-recorded characteristics. This case study will be a deep dive into Principal Components Analysis (PCA) and K-Means clustering methods, and the end result will be groupings that are used to inform things like localized marketing campaigns and voter campaign strategies.

## Payment Fraud Detection

> Train a linear model to do credit card fraud detection. Improve the model by accounting for class imbalance in the training data and tuning for a specific perrformance metric

This case will demonstrate how to use supervised learning techniques, specifically SageMaker’s LinearLearner, for fraud detection. The payment transaction dataset we'll work with is unbalanced, with many more examples of valid transactions vs. fraudulent, and so you will investigate methods for compensating for this imbalance and tuning your model to improve its performance according to a specific product goal.

## Deploying Custom Models

> Design and train a custom PyTorch classifier by writing a training script. This is an especially useful skill for tasks that cannot be easily solved by built-in algorithms

Adding on to what you have learned in the credit card fraud case study, you will learn how to manage cases where classes of data are not separable by a linear line. You'll train and deploy a custom, PyTorch neural network for classifying data.

## Time-Series Forecasting

> Learn how to format time series data into context(input) and prediction(output) data, and train the built-in algorithm, DeepAR; this uses an RNN to find recurring patterns in time series data

This case demonstrates how to train SageMaker's DeepAR model for forecasting predictions over time. Time-series forecasting is an active area of research because a good forecasting algorithm often takes in a number of different features and accounts for seasonal or repetitive patterns. In this study, you will learn a bit about creating features out of time series data and formatting it for training.