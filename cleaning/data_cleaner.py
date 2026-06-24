# -*- coding: utf-8 -*-    
from collections import deque
import numpy as np

class DataCleaner:
    def __init__(self, bad_tick_threshold_std: float, vol_lookback: int):
        self.bad_tick_threshold_std = bad_tick_threshold_std
        self.vol_lookback = vol_lookback

        # Memoria por símbolo. 
        self._last_valid = {}      # symbol -> último precio bueno
        self._returns = {}         # symbol -> deque de retornos válidos recientes

    def process(self, symbol: str, raw_price: float) -> float:
        '''
        Recibe algo de esta pinta: 
            (CRIPTO_X_RAW, 50.2)
        '''
        
        # ¿ya existe este symbol en self._last_valid?
        #   Si no existe -> es la primera vez que lo veo.
        if symbol not in self._last_valid:
            if not (np.isnan(raw_price)):
                self._last_valid[symbol] = raw_price    
                self._returns[symbol] = deque(maxlen = self.vol_lookback) #Inicializo estructura vacía.
                return raw_price
            else:
                return np.nan
        else:
            # Caso A: ¿es NaN este dato?
            if np.isnan(raw_price):
                return self._last_valid[symbol] 
            
            # Si llego acá, raw_price NO es NaN. Calculo el retorno candidato.
            #El retorno es (precio actual - precio ayer) / precio ayer.
            retorno = (raw_price - self._last_valid[symbol]) / self._last_valid[symbol]

            # Caso B: ¿hay suficiente historial en el deque para evaluar bad tick?
            if len(self._returns[symbol]) < 10:  # ¿cuántos retornos mínimo te parece razonable?
                # no puedo evaluar bad tick todavía -> lo trato como dato válido
                # (actualizo _last_valid, agrego el retorno al deque, devuelvo raw_price)
                self._last_valid[symbol] = raw_price
                self._returns[symbol].append(retorno)
                return raw_price

            # Caso C: ya hay suficiente historial -> calculo el desvío y comparnetworks
            desvio = np.std(self._returns[symbol])
            if abs(retorno) > self.bad_tick_threshold_std * desvio:
                # print("es bad_tick", retorno, raw_price)
                return self._last_valid[symbol]
            else:
                # dato válido y razonable -> actualizo todo y retorno
                self._last_valid[symbol] = raw_price
                self._returns[symbol].append(retorno)
                return raw_price
    
#Testeo:
'''    
cleaner = DataCleaner(bad_tick_threshold_std=4.0, vol_lookback=50)

precios_de_prueba = [50.0, 50.2, 50.1, 50.4, 50.2, 50.3, 50.0, 50.4, 50.1, 50.2, 50.6, 50.9, 67.0, 54.1]

for p in precios_de_prueba:
    resultado = cleaner.process("TEST", p)
    print(p, "->", resultado)
'''    