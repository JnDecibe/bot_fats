# -*- coding: utf-8 -*-

class riskManager:
    def __init__(self, riesgo_max):
        self.riesgo_max = riesgo_max

    def position_size(self, capital_actual, precio_A_actual, precio_B_actual, beta_calibrado, señal):
        #La respuesta será un diccionario que indique la cantidad de compras y ventas de cada activo.
        res = {"unidades_A": 0, "unidades_B": 0}  # positivo=compra, negativo=venta
        
        #En función de la señal tomo una decisión.
        if(señal == 0): #No hacer nada
            pass
        elif (señal == 1): #Aposté a que sube el spread. Compro A y vendo B
            res["unidades_A"] = (capital_actual * self.riesgo_max)/precio_A_actual
            res["unidades_B"] = -beta_calibrado*res["unidades_A"]
        else: #La señal es -1 entonces aposté a que el baja el spread. Vendo A y compro B
            res["unidades_A"] = -(capital_actual * self.riesgo_max)/precio_A_actual
            res["unidades_B"] = -beta_calibrado*res["unidades_A"]
        
        return res
        