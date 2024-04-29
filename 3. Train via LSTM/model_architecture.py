

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy


def basic_lstm(input_data,target)
    model = Sequential([
        LSTM(50, input_shape=(300, 6)),  # Adjust number of units, experiment with return_sequences=True if stacking LSTMs
        Dense(1)                         # Output layer: predicting the p-value as a single scalar
    ])

    model.compile(optimizer='adam', loss='mse')

    # Train the model
    model.fit(input_data, target, epochs=10, batch_size=64, validation_split=0.1)

    return model


def predict_stationarity(input_data, target, num_classes):
    model = Sequential([
        LSTM(100, input_shape=(300, 6), return_sequences=True, kernel_regularizer=l2(0.01)),  # First LSTM layer with L2 regularization
        Dropout(0.3),  
        
        LSTM(100, return_sequences=True),  # Second LSTM layer
        Dropout(0.3), 

        LSTM(50, return_sequences=False),  # Third LSTM layer
        Dropout(0.3),  
        
        Dense(50, activation='relu'),  # First dense layer with ReLU activation
        BatchNormalization(),  # Normalization to maintain stability during training
        Dropout(0.3),  
        
        Dense(num_classes, activation='softmax')  # Output layer: multi-class classification
    ])

    # Compile the model with Adam optimizer and Categorical Cross-Entropy loss for classification
    model.compile(optimizer=Adam(learning_rate=0.001), loss=CategoricalCrossentropy(), metrics=['accuracy'])

    # Train the model with more epochs, larger batch size, and validation split
    model.fit(input_data, target, epochs=50, batch_size=128, validation_split=0.2)

    return model




def hedge_ratio_lstm(input_data, target):
    model = Sequential([
        LSTM(100, input_shape=(300, 6), return_sequences=True, kernel_regularizer=l2(0.01)),  # First LSTM layer with L2 regularization
        Dropout(0.3),  # Dropout to prevent overfitting
        
        LSTM(100, return_sequences=True),  # Second LSTM layer
        Dropout(0.3), 

        LSTM(50, return_sequences=False),  # Third LSTM layer
        Dropout(0.3),  
        
        Dense(50, activation='relu'),  # First dense layer with ReLU activation
        BatchNormalization(),  # Normalization to maintain stability during training
        Dropout(0.3),  

        Dense(1)  # Output layer: predicting the target value
    ])

    # Compile the model with Adam optimizer and Mean Squared Error loss
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    # Train the model with validation split, larger epochs, and increased batch size for robustness
    model.fit(input_data, target, epochs=50, batch_size=128, validation_split=0.2)

    return model
