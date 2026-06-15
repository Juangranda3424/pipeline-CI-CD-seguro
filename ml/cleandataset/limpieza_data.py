import pandas as pd
import re

# 1. Cargar tus datos (asumiendo que se llama dataset.json)
# Si estás en Colab, primero subes el archivo a la barra lateral
df = pd.read_json("function.json")

print(f"Registros iniciales: {len(df)}")

# 2. Eliminar duplicados exactos en el código para evitar fugas (Data Leakage)
df = df.drop_duplicates(subset=["func"])

# 3. Función para limpiar ruido del código C
def limpiar_codigo_c(codigo):
    if not isinstance(codigo, str):
        return ""
    
    # Quitar comentarios de una línea (//...)
    codigo = re.sub(r'//.*', '', codigo)
    # Quitar comentarios de bloque (/*...*/)
    codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
    
    # Normalizar saltos de línea y espacios excesivos
    codigo = re.sub(r'\s+', ' ', codigo)
    
    return codigo.strip()

# Aplicar la limpieza básica
df["func_limpia"] = df["func"].apply(limpiar_codigo_c)

# 4. Filtrar funciones truncadas (como la segunda que me pasaste)
# Una regla simple: si no termina en '}', probablemente quedó cortada
def esta_completo(codigo):
    return codigo.endswith("}")

df = df[df["func_limpia"].apply(esta_completo)]

print(f"Registros después de limpiar y filtrar: {len(df)}")

# 5. Guardar el dataset limpio listo para el modelo
df.to_json("dataset_limpio.json", orient="records", indent=2)