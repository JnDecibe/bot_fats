# -*- coding: utf-8 -*-
import pandas as pd
class PropFirmEvaluator:
    def __init__(self, max_daily_drawdown: float, max_total_drawdown: float,
                 profit_target: float, min_dias_operados: int, capital_inicial: float):
        # parámetros fijos de las reglas de la firm
        '''
        - Drawdown diario máximo:  5% del capital inicial
        - Drawdown total máximo:   10% del capital inicial
        - Profit target:           8% del capital inicial
        - Días mínimos operados:   mínimo 4 días con al menos una operación
        '''
        self.max_daily_drawdown = max_daily_drawdown
        self.max_total_drawdown = max_total_drawdown
        self.profit_target = profit_target
        self.min_dias_operados = min_dias_operados
        self.capital_inicial = capital_inicial
    
    def evaluar(self, df: pd.DataFrame) -> dict:
        # recibe el DataFrame que devuelve LiveSimulator.run()
        # devuelve {"resultado": "PASS"/"FAIL", "motivo": ..., "metricas": ...}
        evaluacion = {
            "Resultado": None,
            "Motivo" : None,
            "Metricas" : None
            }
        #Calculo los valores a evaluar:
        high_water_mark = df["capital"].cummax()
        drawdown = (df["capital"] - high_water_mark) / high_water_mark
        
        por_dia = df.groupby(df["timestamp"].dt.date)["capital"]
        maximo_diario = por_dia.max()
        minimo_diario = por_dia.min()
        drawdown_diario = (minimo_diario - maximo_diario) / maximo_diario
        
        peor_drawdown_total = drawdown.min()
        peor_drawdown_diario = drawdown_diario.min()
        
        capital_final = df["capital"].iloc[-1]
        profit = (capital_final - self.capital_inicial) / self.capital_inicial
        
        dias_operados = df[df["posicion"] != 0]["timestamp"].dt.date.nunique()
        
        if(peor_drawdown_diario >= self.max_daily_drawdown):
            if(peor_drawdown_total >= self.max_total_drawdown):
                if(profit >= self.profit_target):
                    if(dias_operados > self.min_dias_operados):
                        evaluacion["Resultado"] = "PASS"
                    else:
                        evaluacion["Resultado"] = "FAIL"
                        evaluacion["Motivo"] = "Pocos días operados"
                        evaluacion["Metricas"] = dias_operados
                else:
                    evaluacion["Resultado"] = "FAIL"
                    evaluacion["Motivo"] = "Ganancia no alzanzada"
                    evaluacion["Metricas"] = profit
                        
            else:
                evaluacion["Resultado"] = "FAIL"
                evaluacion["Motivo"] = "Drawdown total permitido excedido"
                evaluacion["Metricas"] = peor_drawdown_total
        else:
            evaluacion["Resultado"] = "FAIL"
            evaluacion["Motivo"] = "Drawdown diario permitido excedido"
            evaluacion["Metricas"] = peor_drawdown_diario
        
        return evaluacion