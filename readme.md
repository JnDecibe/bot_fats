# bot_fats

Bot de trading algorítmico que implementa una estrategia de **pares cointegrados** (mean reversion) sobre criptomonedas, construido desde cero en Python siguiendo los principios del libro *Quantitative Trading* de Ernest Chan.

> **Estado actual:** backtesting sobre datos sintéticos ✅ | Paper trading con datos reales: en desarrollo 🔄

---

## ¿Qué hace este bot?

Opera el spread entre dos criptomonedas cointegradas (BTC/ETH) apostando a que, cuando el spread se aleja de su media histórica, va a volver a ella. Esta idea se conoce como **mean reversion** y es uno de los principios más estudiados en finanzas cuantitativas.

En términos concretos:
- Si el spread está **muy por encima** de su media → vende A y compra B (apuesta a que baja)
- Si el spread está **muy por debajo** de su media → compra A y vende B (apuesta a que sube)
- Si el spread **volvió a la media** → cierra la posición y registra la ganancia/pérdida

---

## Arquitectura del sistema

El proyecto está diseñado con una separación estricta de responsabilidades. Cada módulo hace **una sola cosa** y no sabe nada del resto, lo que permite reemplazar cualquier pieza sin tocar las demás (por ejemplo, reemplazar los datos simulados por una API real sin modificar la estrategia).

```
bot_fats/
│
├── data/
│   └── data_factory.py          # Generador de datos sintéticos con errores reales
│                                 # (NaN, bad ticks, gaps) según Cap. 3 y 5 de Chan
│
├── cleaning/
│   └── data_cleaner.py          # Limpieza minuto a minuto con memoria persistente
│                                 # Forward fill + detección de bad ticks por z-score
│
├── strategy/
│   ├── calibration.py           # Estimación de beta (OLS), spread_mean y spread_std
│   │                             # sobre ventana móvil (evita look-ahead bias)
│   └── pairs_zscore.py          # Máquina de estados: flat / long / short
│                                 # según umbrales de entrada y salida del z-score
│
├── portfolio/
│   └── risk_manager.py          # Position sizing: cuántas unidades de A y B operar
│                                 # respetando el % máximo de riesgo por operación
│
├── backtester/
│   └── live_simulator.py        # Motor de simulación minuto a minuto
│                                 # Emula el comportamiento de un sistema en vivo
│                                 # sobre datos históricos, sin mirar el futuro
│
├── prop_firm/
│   └── prop_firm_evaluator.py   # Evaluador de reglas de prop firms 
│                                 # Drawdown diario, drawdown total, profit target
│
└── main.py                      # Punto de entrada: instancia y conecta todos los módulos
```

---

## Flujo de datos (minuto a minuto)

```
[Dato crudo: precio A y precio B]
            │
            ▼
[1. DataCleaner]
    ¿Es NaN?         → forward fill con último precio válido
    ¿Es bad tick?    → detectado por z-score de retornos recientes → forward fill
    ¿Es válido?      → actualiza memoria y continúa
            │
            ▼
[2. PairsCalibrator] (ventana móvil, solo datos pasados)
    Estima beta via OLS: precio_A ≈ beta * precio_B
    Calcula spread_mean y spread_std sobre la ventana
            │
            ▼
[3. PairsZScoreStrategy]
    spread = precio_A - beta * precio_B
    z = (spread - spread_mean) / spread_std
    Máquina de estados: devuelve -1, 0 o 1
            │
            ▼
[4. RiskManager]
    unidades_A = (capital * riesgo_max) / precio_A
    unidades_B = beta * unidades_A  (hedge ratio)
            │
            ▼
[5. Registro + PropFirmEvaluator]
    Actualiza equity, registra timestamp, z-score, posición
    Evalúa drawdown diario/total, profit target, días operados
```

---

## Decisiones de diseño importantes

### Ventana móvil para calibración (sin look-ahead bias)
El beta y los parámetros del spread se estiman **únicamente con datos anteriores** al momento actual. En el minuto `t`, el calibrador solo ve los últimos `N` minutos previos a `t`. Esto es crítico: calibrar con datos futuros produce estrategias que funcionan en backtest pero fallan en producción.

### Separación entre señal y dimensionamiento
La estrategia solo decide la **dirección** (-1, 0, 1). El tamaño de la posición es responsabilidad exclusiva del `RiskManager`. Mezclar ambas responsabilidades en un mismo módulo es uno de los errores más comunes en sistemas de trading amateur.

### Detección de bad ticks por volatilidad reciente
Un precio corrupto no es un NaN — es un número válido pero absurdo. El `DataCleaner` lo detecta comparando el retorno candidato contra el desvío estándar de los últimos `N` retornos válidos. Si supera `K` desvíos, se descarta y se aplica forward fill, igual que con los NaN.

### Estado persistente entre minutos
El `DataCleaner` recuerda el último precio válido por activo usando un diccionario interno. El `LiveSimulator` mantiene la posición actual, el capital y el historial. Esto garantiza que cada decisión del sistema usa exactamente la información disponible en ese momento, no más.

---

## Resultados en datos sintéticos

Los datos sintéticos simulan 1 año de precios minuto a minuto con:
- Cointegración real entre A y B (beta = 1.8)
- Inyección de NaN (0.2% de los datos) simulando caídas de WebSocket
- Inyección de bad ticks (0.05% de los datos) simulando errores de API
- Régimen cambiante (bull / bear / choppy) según cadena de Markov

| Métrica | Valor |
|---------|-------|
| Capital inicial | $10.000 |
| Capital final | $27.864 |
| Retorno total | +178% |
| Drawdown máximo | < 10% |
| Resultado challenge | ✅ PASS |

> ⚠️ Estos resultados corresponden a datos **sintéticos** con cointegración casi perfecta. El rendimiento en datos reales será diferente y está siendo evaluado en la siguiente etapa del proyecto.

---

## Cómo correrlo

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/pairs-trading-bot.git
cd bot_fats

# Instalar dependencias
pip install -r requirements.txt

# Correr el backtest completo
python main.py
```

Los parámetros configurables están al principio de `main.py`:

```python
entry_z = 2.0          # Umbral de entrada (desvíos del spread para operar)
exit_z = 0.5           # Umbral de salida (volver a la media)
calibration_window = 1440  # Ventana de calibración (1 día en minutos)
recalibrar_cada = 60       # Frecuencia de recalibración (1 hora)
riesgo_max = 0.01          # Riesgo máximo por operación (1% del capital)
capital_inicial = 10000.0  # Capital inicial de la simulación
```

---

## Próximos pasos

- [ ] Conectar a datos reales via API (Binance / Kraken usando `ccxt`)
- [ ] Paper trading con datos en tiempo real
- [ ] Agregar métricas de performance: Sharpe ratio, CAGR, equity curve
- [ ] Evaluar cointegración real BTC/ETH con test de Engle-Granger
- [ ] Optimización de parámetros out-of-sample

---

## Stack tecnológico

- **Python 3.x**
- **NumPy** — cálculos numéricos y regresión OLS
- **Pandas** — manejo de series temporales y DataFrames

---

## Bibliografía

- Chan, E. (2008). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley.
- Chan, E. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. *(lectura pendiente)*

---

## Autor

**Juan Decibe** — Estudiante de Ciencias de Datos, UBA  
Proyecto desarrollado como parte del aprendizaje de trading cuantitativo aplicado a criptomonedas.
