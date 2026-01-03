from sklearn.linear_model import LinearRegression
import numpy as np

class BatteryPredictionAi:
    def __init__(self):
        self._model = LinearRegression()
        self._train_model()

    def _train_model(self):
        # x [wind_kmh, temperature, raining]
        X_train = [
            [0, 20, 0],
            [0, 10, 1],
            [0, 0, 0],
            [0, -10, 0],
            [10, 7, 1],
            [10, 18, 0],
            [30, 5, 0]
        ]
        y_train = [1.0, 1.1, 1.2, 1.5, 1.3, 1.1, 1.6]
        self._model.fit(X_train, y_train)
        
    def predict_drain_multiplier(self, wind_speed, temperature, is_raining):
        prediction = self._model.predict([[wind_speed, temperature, is_raining]])
        return max(1.0, prediction[0])
    



