# -*- coding: utf-8 -*-
import pandas as pd

class LiveSimulator:
        def __init__(self, cleaner, calibrador, estrategia, risk_manager, 
             calibration_window, recalibrar_cada, capital_actual):
            # guardo los colaboradorees como atributos
            self.cleaner = cleaner
            self.calibrador = calibrador
            self.estrategia = estrategia
            self.risk_manager = risk_manager
            self.calibration_window = calibration_window
            self.recalibrar_cada = recalibrar_cada
            self.capital_actual = capital_actual
            self.precio_entrada_A = None
            self.precio_entrada_B = None
            self.operaciones = {"unidades_A": 0, "unidades_B": 0}
            self.ultima_operacion_A = 0
            self.ultima_operacion_B = 0
            
            # inicializo el historial vacío
            self.historial_A = []
            self.historial_B = []
            # inicializo el estado: posición actual
            self.posicion_actual = 0
            
        def run(self, datos: pd.DataFrame):                
            registro = []
            params = None
            z = None
            minutos_transcurridos = 0
    
            for timestamp, fila in datos.iterrows():
                # Paso 1: limpio precios.
                precios_limpios_A = self.cleaner.process("CRIPTO_A_RAW", fila["CRIPTO_A_RAW"])
                precios_limpios_B = self.cleaner.process("CRIPTO_B_RAW", fila["CRIPTO_B_RAW"])
                # Paso 2: agregar al historial
                self.historial_A.append(precios_limpios_A)
                self.historial_B.append(precios_limpios_B)
                
                # Paso 3: ¿hay suficiente historial?
                if(len(self.historial_A) < self.calibration_window):
                    continue
                
                # Paso 4: ¿corresponde recalibrar?
                #   uso un contador de minutos transcurridos y chequeo si es múltiplo de self.recalibrar_cada
                if(minutos_transcurridos % self.recalibrar_cada == 0):
                    #Tengo que recalibrar:
                    params = self.calibrador.fit(self.historial_A[-self.calibration_window:], self.historial_B[-self.calibration_window:])
                
                minutos_transcurridos += 1
                # Paso 5: calcular señal
                if(params != None):
                    signal,z = self.estrategia.generate_signal(precios_limpios_A, precios_limpios_B, 
                                                             params, self.posicion_actual)
                    
                    # Paso 6: ¿cambió la señal?
                    if(signal == self.posicion_actual):
                        #Si la posición es la misma no hago nada:
                        pass
                    else:
                        #Proceso la señal con el risk manager:
                        self.operaciones = self.risk_manager.position_size(capital_actual = self.capital_actual, 
                                                                              precio_A_actual = precios_limpios_A, 
                                                                              precio_B_actual = precios_limpios_B,
                                                                              beta_calibrado = params["beta"],
                                                                              señal = signal)
                        unidades_A = self.operaciones["unidades_A"]
                        unidades_B = self.operaciones["unidades_B"]
                    
                    if(signal != 0): #Abro
                        self.ultima_operacion_A = unidades_A  # guardo las unidades abiertas
                        self.ultima_operacion_B = unidades_B
                        self.precio_entrada_A = precios_limpios_A
                        self.precio_entrada_B = precios_limpios_B
                        
                    if(signal == 0 and signal != self.posicion_actual): #Cierro
                        pnl = self.ultima_operacion_A * (precios_limpios_A - self.precio_entrada_A) + self.ultima_operacion_B * (precios_limpios_B - self.precio_entrada_B)
                        self.capital_actual += pnl
                        
                    self.posicion_actual = signal
                    
                # Paso 7: registro resultado
                registro.append({
                    "timestamp": timestamp,
                    "capital": self.capital_actual,
                    "posicion": self.posicion_actual,
                    "z_score": z,         # para graficar cuándo entró y salió
                    "precio_A": precios_limpios_A,
                    "precio_B": precios_limpios_B,
                    })  
            
            return pd.DataFrame(registro)