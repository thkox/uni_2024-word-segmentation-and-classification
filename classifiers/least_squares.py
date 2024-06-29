import tensorflow as tf
from sklearn.model_selection import train_test_split
from classifiers import feature_extraction as fe
import joblib
import os
import numpy as np

OUTPUT_DIR = 'files/output/classifiers'


def train(output_dir=OUTPUT_DIR):
    """
    Train Least Squares classifier on extracted features and save the model.
    """

    if fe.load_features() is None:
        return
    else:
        _, features, labels = fe.load_features()

    if features is None or labels is None:
        print("Error loading features. Aborting training.")
        return

    # Convert labels to -1 and 1
    labels = np.where(labels == 0, -1, 1)

    print("=====================================")
    print("Training Least Squares classifier")

    # Ensure features and labels are 2D tensors
    features_train = tf.constant(features, dtype=tf.float32)
    if features_train.shape.rank == 1:
        features_train = tf.expand_dims(features_train, axis=-1)  # Make it a column vector
    labels_train = tf.constant(labels, dtype=tf.float32)
    if labels_train.shape.rank == 1:
        labels_train = tf.expand_dims(labels_train, axis=-1)  # Make it a column vector

    # Add bias term to features
    features_train = tf.concat([tf.ones((features_train.shape[0], 1), dtype=tf.float32), features_train], axis=1)

    # Use tf.linalg.lstsq to solve for weights
    weights = tf.linalg.lstsq(features_train, labels_train, fast=False)

    # Save the trained weights
    model_filename = os.path.join(output_dir, 'ls_model.pkl')
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    joblib.dump(weights.numpy(), model_filename)

    print("Least Squares training completed")
    print("=====================================")

    return weights.numpy()


def load_model(output_dir=OUTPUT_DIR):
    """
    Load the trained Least Squares model from the given path.

    Returns:
        np.ndarray: Loaded Least Squares weights.
    """
    model_path = os.path.join(output_dir, 'ls_model.pkl')
    if not os.path.isfile(model_path):
        print("The Least Squares model does not exist. Please train the model first.")
        return
    print("Loading Least Squares model from", model_path)
    weights = joblib.load(model_path)
    print("Least Squares model loaded successfully")
    return weights


def predict(features):
    """
    Predict the labels of given features using the trained Least Squares model.

    Args:
        model (np.ndarray): Trained Least Squares weights.
        features (np.ndarray): Features to predict the labels.

    Returns:
        np.ndarray: Predicted labels.
    """

    # Add bias term
    features = np.column_stack([np.ones(len(features)), features])

    # Compute predictions
    predictions = np.sign(features @ load_model())  # Matrix multiplication and sign function

    # Convert predictions to 0 and 1
    binary_predictions = np.where(predictions == -1, 0, 1)

    # Reshape the predictions to (number of labels,)
    binary_predictions = binary_predictions.ravel()

    return binary_predictions

