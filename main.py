# -*- coding: utf-8 -*-
from data.data_factory import generar_universo_cripto_sucio
from cleaning.data_cleaner import DataCleaner
from strategy.pairs_zscore import pairsZScore
from strategy.PairsCalibrator import PairsCalibrator
from portfolio.risk_manager import riskManager
from backtester.live_simulator import LiveSimulator
from prop_firm.prop_firm_evaluator import PropFirmEvaluator

if __name__ == "__main__":
    # Parámetros de estrategia
    entry_z = 2.0          # entrar cuando el spread está a 2 desvíos de la media
    exit_z = 0.5           # salir cuando vuelve a 0.5 desvíos
    calibration_window = 1440  # ventana de calibración: 1 día en minutos
    recalibrar_cada = 60       # recalibrar cada hora
    
    # Parámetros de riesgo
    riesgo_max = 0.01      # arriesgar máximo 1% del capital por operación
    capital_inicial = 10000.0
    
    # Parámetros
    max_daily_drawdown = -0.05   # -5%
    max_total_drawdown = -0.10   # -10%
    profit_target = 0.08         # 8%
    min_dias_operados = 4
   
    #Hay que instanciar todas las clases importadas.
    cleaner = DataCleaner(bad_tick_threshold_std = 4.0, vol_lookback = 10)
    estrategia = pairsZScore(entry_z, exit_z)
    calibrator = PairsCalibrator(calibration_window)
    risk = riskManager(riesgo_max)
    simulador = LiveSimulator(cleaner, calibrator, estrategia, risk, calibration_window, recalibrar_cada, capital_inicial)
    evaluador = PropFirmEvaluator(max_daily_drawdown, max_total_drawdown, profit_target, min_dias_operados, capital_inicial)
    
    #Genero los datos
    datos = generar_universo_cripto_sucio()
    
    #Corro la simulación
    registro = simulador.run(datos)
    
    #Hago la evaluación
    resultado = evaluador.evaluar(registro)
    print(resultado)
    
    print(f"Capital inicial: ${capital_inicial:,.2f}")
    print(f"Capital final:   ${registro['capital'].iloc[-1]:,.2f}")
    print(f"Retorno total:   {((registro['capital'].iloc[-1] / capital_inicial) - 1) * 100:.2f}%")
    print(f"Operaciones:     {(registro['posicion'].diff() != 0).sum()}")
    
    # Ver las primeras filas donde hubo cambio de posición
    operaciones = registro[registro['posicion'].diff() != 0].head(20)
    print(operaciones[['timestamp', 'capital', 'posicion', 'z_score']])

    # Ver la distribución de cambios de capital
    cambios = registro['capital'].diff()
    cambios_no_cero = cambios[cambios != 0]
    print("Ganancia promedio por operación:", cambios_no_cero.mean())
    print("Ganancia máxima:", cambios_no_cero.max())
    print("Pérdida máxima:", cambios_no_cero.min())