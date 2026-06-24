# -*- coding: utf-8 -*-
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=np.RankWarning)

class PairsCalibrator:
    def __init__(self, calibration_window: int):
        self.calibration_window = calibration_window

    def fit(self, prices_A_window, prices_B_window) -> dict:
        """
        Recibe DOS listas/arrays de precios YA LIMPIOS, correspondientes
        a la MISMA ventana de tiempo pasada (ej: los últimos N minutos),
        para los activos A y B respectivamente.

        Devuelve un diccionario con los parámetros calibrados:
            {"beta": ..., "spread_mean": ..., "spread_std": ...}
        """
        prices_A_window = np.array(prices_A_window)
        prices_B_window = np.array(prices_B_window)
        
        if len(prices_A_window) != self.calibration_window or len(prices_B_window) != self.calibration_window:
            raise ValueError("La ventana recibida no tiene el tamaño esperado")
        
        beta = np.polyfit(prices_B_window, prices_A_window, 1)[0] #Me quedo con la pendiente calculada
        spread = prices_A_window - beta*prices_B_window
        spread_mean = np.mean(spread)
        spread_std = np.std(spread)
        parametros_calibrados = {"beta" : beta, "spread_mean" : spread_mean, "spread_std" : spread_std}
        return parametros_calibrados
    
#Test:
'''
calibrador = PairsCalibrator(calibration_window=14)
prices_B_window = np.array([50.0, 50.2, 50.1, 50.4, 50.2, 50.3, 50.0, 50.4, 50.1, 50.2, 50.6, 50.9, 67.0, 54.1])
ruido = np.random.rand(len(prices_B_window))
prices_A_window = 1.8 * prices_B_window + ruido
resultados = calibrador.fit(prices_A_window, prices_B_window)
print(resultados["beta"]) #Es lo esperado, 1.8145133788973888 ~ 1.8
'''

