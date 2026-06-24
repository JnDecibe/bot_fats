# -*- coding: utf-8 -*-

class pairsZScore:
    
    def __init__(self, entry_z, exit_z):
        self.entry_z = entry_z
        self.exit_z = exit_z

    def generate_signal(self, price_A: float, price_B: float,
                        params: dict, current_position: int) -> int:

        #En el diccionario tengo: parametros_calibrados = {"beta" : beta, "spread_mean" : spread_mean, "spread_std" : spread_std}
        # 1. Calculo el spread actual con los params calibrados
        beta_actual = params["beta"]
        spread_mean = params["spread_mean"]
        spread_std = params["spread_std"]
        spread_actual = price_A - (beta_actual * price_B)

        # 2. Calculo el z-score
        z = (spread_actual - spread_mean)/spread_std

        # 3. Máquina de estados
        if current_position == 0:  # estoy flat
            if z > self.entry_z: 
                return -1,z   #Si el spread está muy alto vendo A y compro B. (apuesto a que baja)
            elif z < -self.entry_z:
                return 1,z   #Si está muy bajo compro A y vendo B (apuesto a que sube)
            else:
                return 0,z

        elif current_position == -1:  # estoy short. Apuesto a que el spread va a subir.
            if abs(z) < self.exit_z:
                return 0,z   # El spread volvió a la media entonces cierro la operación.
            else:
                return -1,z   # Si todavía no volvió me mantengo igual.
            
        elif current_position == 1:  # Estoy long. Apuesto a que el spread va a bajar.
            if abs(z) < self.exit_z:
                return 0,z   # El spread volvió a la media entonces cierro la operación
            else:
                return 1,z   # Si todavía no volvió me mantengo igual