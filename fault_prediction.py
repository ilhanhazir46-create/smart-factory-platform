import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaultPrediction:
    """
    Predicts machine faults using machine learning models trained on historical data.
    Provides predictive maintenance insights to prevent downtime.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the fault prediction model.
        
        Args:
            model_path: Path to saved model file
        """
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        if model_path:
            self.load_model()
    
    def load_model(self):
        """Load pre-trained fault prediction model."""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
    
    def train_model(self, X_train, y_train):
        """
        Train the fault prediction model on historical data.
        
        Args:
            X_train: Training features (sensor readings, operational parameters)
            y_train: Training labels (0=normal, 1=fault)
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Train Random Forest model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y_train)
            
            logger.info("Model training completed successfully")
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
    
    def predict_fault(self, sensor_data):
        """
        Predict machine fault based on sensor readings.
        
        Args:
            sensor_data: Dictionary or array of sensor readings
            
        Returns:
            Dictionary with fault prediction and confidence
        """
        try:
            # Convert to numpy array if dict
            if isinstance(sensor_data, dict):
                sensor_array = np.array(list(sensor_data.values())).reshape(1, -1)
            else:
                sensor_array = np.array(sensor_data).reshape(1, -1)
            
            # Scale the data
            scaled_data = self.scaler.transform(sensor_array)
            
            # Make prediction
            prediction = self.model.predict(scaled_data)[0]
            probability = self.model.predict_proba(scaled_data)[0]
            
            result = {
                'fault_predicted': bool(prediction),
                'fault_probability': float(probability[1]),
                'normal_probability': float(probability[0]),
                'risk_level': self._calculate_risk_level(probability[1]),
                'timestamp': str(np.datetime64('now'))
            }
            
            return result
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_risk_level(self, probability):
        """
        Calculate risk level based on fault probability.
        
        Args:
            probability: Fault probability (0-1)
            
        Returns:
            Risk level string: low, medium, high, critical
        """
        if probability < 0.3:
            return "low"
        elif probability < 0.6:
            return "medium"
        elif probability < 0.8:
            return "high"
        else:
            return "critical"
    
    def batch_predict(self, sensor_data_list):
        """
        Predict faults for multiple sensor readings.
        
        Args:
            sensor_data_list: List of sensor data
            
        Returns:
            List of prediction results
        """
        results = []
        for data in sensor_data_list:
            result = self.predict_fault(data)
            results.append(result)
        
        return results
    
    def save_model(self, path):
        """Save the trained model to disk."""
        try:
            joblib.dump(self.model, path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")