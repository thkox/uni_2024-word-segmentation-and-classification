import numpy as np
import tensorflow as tf
from classifiers import feature_extraction as fe
import os

OUTPUT_DIR = 'files/output/classifiers'


# TODO: you can remove tensorflow and use keras only
def train(output_dir=OUTPUT_DIR):
    """
    Train RNN classifier on extracted features and save the model.

    Args:
        output_dir (str): Directory to save the trained model.

    Returns:
        Sequential: Trained RNN classifier.
    """

    if fe.load_features() is None:
        return
    else:
        _, features, labels = fe.load_features()

    print("=====================================")
    print("Training RNN classifier")

    # Check if the features array is 2D (samples, features)
    if len(features.shape) == 2:
        features = features.reshape((features.shape[0], features.shape[1], 1))  # Reshape to 3D (samples, features, 1)
        print("Reshaped features to", features.shape)
    elif len(features.shape) != 3:
        raise ValueError("Features array must be 2D or 3D. Current shape: {}".format(features.shape))

    # Initialize RNN model
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Input(shape=(features.shape[1], features.shape[2])))  # Input layer based on features shape
    model.add(tf.keras.layers.SimpleRNN(32, activation='relu', return_sequences=True))
    model.add(tf.keras.layers.Flatten())  # Flatten the 3D output to 1D
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(features, labels, epochs=10, batch_size=32, validation_split=0.2)

    # Save the trained model
    model_filename = os.path.join(output_dir, 'rnn_model.keras')
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    model.save(model_filename)

    print("RNN training completed")
    print("=====================================")
    return model


def load_model(output_dir=OUTPUT_DIR):
    """
    Load the trained RNN model from the given path.

    Returns:
        Sequential: Loaded RNN classifier.
    """
    model_path = os.path.join(output_dir, 'rnn_model.keras')
    if not os.path.isfile(model_path):
        print("The RNN model does not exist. Please train the model first.")
        return
    print("Loading RNN model from", model_path)
    rnn_clf = tf.keras.models.load_model(model_path)
    print("RNN model loaded successfully")
    return rnn_clf


def predict(model, features):
    """
    Predict labels for new data using the trained RNN model.

    Args:
        model (Sequential): Trained RNN classifier.
        features (np.ndarray): New data for prediction.

    Returns:
        np.ndarray: Predicted labels.
    """
    print("Making predictions with RNN model")
    if len(features.shape) == 2:
        features = features.reshape((features.shape[0], features.shape[1], 1))
    elif len(features.shape) != 3:
        raise ValueError("Features array must be 2D or 3D. Current shape: {}".format(features.shape))
    predictions = model.predict(features)
    return predictions.argmax(axis=-1)
