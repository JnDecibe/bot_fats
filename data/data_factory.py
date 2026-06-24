# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generar_universo_cripto_sucio():
    """
    Simula 1 año de datos históricos minuto a minuto para dos criptomonedas.
    Inyecta errores del mundo real según los Capítulos 3 y 5 de Ernie Chan:
    1. Datos faltantes (Gaps por caída de WebSockets).
    2. Bad Ticks (Precios corruptos de la API).
    3. Ruido de microestructura y desalineación temporal.
    """
    print("Fabricando 1 año de datos minuto a minuto en vivo...")
    
    # 1. Crear el índice de tiempo (1 año completo, minuto a minuto)
    fecha_inicio = datetime(2025, 1, 1, 0, 0, 0)
    total_minutos = 365 * 24 * 60  # 525,600 minutos
    
    timestamps = [fecha_inicio + timedelta(minutes=i) for i in range(total_minutos)]
    
    # 2. Generar el proceso estocástico base subyacente (Caminata aleatoria cointegrada)
    np.random.seed(101)
    
    # Cripto B (Independiente) sigue un movimiento browniano estándar
    retornos_B = np.random.normal(0, 0.002, size=total_minutos)
    precios_B_limpios = 50.0 + np.cumsum(retornos_B)
    
    # Cripto A (Dependiente) está cointegrada con B (Beta = 1.8) + un residuo estacionario
    residuo_estacionario = np.random.normal(loc=15.0, scale=0.5, size=total_minutos)
    precios_A_limpios = 1.8 * precios_B_limpios + residuo_estacionario
    
    # 3. CONTAMINACIÓN DE DATOS (Las trampas que Chan advierte en el Cap 3)
    df_sucio = pd.DataFrame(index=timestamps)
    df_sucio['CRIPTO_A_RAW'] = precios_A_limpios
    df_sucio['CRIPTO_B_RAW'] = precios_B_limpios
    
    # Trampa A: Inyección de "Bad Ticks" (Picos absurdos por errores de API)
    # Selecciono el 0.05% de los minutos de forma aleatoria para meter datos rotos
    indices_bad_ticks_A = np.random.choice(total_minutos, size=int(total_minutos * 0.0005), replace=False)
    indices_bad_ticks_B = np.random.choice(total_minutos, size=int(total_minutos * 0.0005), replace=False)
    
    df_sucio.iloc[indices_bad_ticks_A, 0] *= np.random.choice([1.25, 0.75], size=len(indices_bad_ticks_A))
    df_sucio.iloc[indices_bad_ticks_B, 1] *= np.random.choice([1.30, 0.70], size=len(indices_bad_ticks_B))
    
    # Trampa B: Desconexión de Red / Gaps de Datos (Capítulo 5)
    # Simulo momentos donde el WebSocket se cayó y hay valores nulos (NaN)
    indices_vacios_A = np.random.choice(total_minutos, size=int(total_minutos * 0.002), replace=False)
    indices_vacios_B = np.random.choice(total_minutos, size=int(total_minutos * 0.002), replace=False)
    
    df_sucio.iloc[indices_vacios_A, 0] = np.nan
    df_sucio.iloc[indices_vacios_B, 1] = np.nan
    
    return df_sucio

# Test rápido de generación
'''
if __name__ == "__main__":
    df = generar_universo_cripto_sucio()
    print(df.head())
    print(f"\nDatos totales generados: {len(df)} filas.")
    print(f"Valores nulos inyectados en Cripto A: {df['CRIPTO_A_RAW'].isna().sum()}")
'''