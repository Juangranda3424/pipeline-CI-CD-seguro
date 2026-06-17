import pandas as pd
import re
import json

# 1. Función para limpiar ruido enfocado en JavaScript
def limpiar_codigo_js(codigo):
    if not isinstance(codigo, str):
        return ""
    
    # CORREGIDO: quitamos el argumento inválido 'code='
    # Quitar comentarios de una línea (//...)
    codigo = re.sub(r'//.*', '', codigo)
    
    # Quitar comentarios de bloque (/*...*/)
    codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
    
    # Reemplazar espacios duros comunes en datasets de web scraping (\xa0)
    codigo = codigo.replace('\xa0', ' ')
    
    # Normalizar saltos de línea y espacios excesivos
    codigo = re.sub(r'\s+', ' ', codigo)
    
    return codigo.strip()

# Heurística para clasificar si el string limpio tiene estructura de JavaScript
def es_javascript(codigo):
    patrones_js = [
        r'\b(const|let|var)\b',                        # Variables JS
        r'\bfunction\b\s*\w*\s*\(',                    # Definición clásica: function miFunc()
        r'\)\s*=>\s*\{',                               # Funciones flecha: (...) => {
        r'\b(console\.log|require|import\s+.*from)\b', # Métodos globales comunes de Node/JS
        r'\b(async|await)\b',                          # Código asíncrono
        r'\bmodule\.exports\b'                         # Exportaciones CommonJS
    ]
    
    if any(re.search(patron, codigo) for patron in patrones_js):
        patrones_exclusivos_c = [
            r'^(static\s+)?(void|int|char|uint\d+_t|unsigned|struct|glue)\b'
        ]
        if any(re.search(patron_c, codigo) for patron_c in patrones_exclusivos_c):
            return False
            
        return True
    return False

# 2. Leer y filtrar línea por línea de forma nativa en streaming
registros_javascript = []
archivo_entrada = "dataset.json"

print("⏳ Filtrando y limpiando funciones de JavaScript en streaming...")

with open(archivo_entrada, "r", encoding="utf-8") as f:
    for num_linea, linea in enumerate(f, 1):
        linea = linea.strip()
        if not linea:
            continue
            
        try:
            dato = json.loads(linea)
            codigo_original = dato.get("func", "")
            
            # Bypass rápido por metadatos de proyectos C conocidos en tu dataset
            if any(p in dato.get("project", "").lower() for p in ["gnutls", "php-src", "busybox", "qemu"]):
                continue
                
            codigo_limpio = limpiar_codigo_js(codigo_original)
            
            # Validar que la función termine correctamente y sea JS legítimo
            if codigo_limpio.endswith("}") and es_javascript(codigo_limpio):
                dato["func_limpia"] = codigo_limpio
                registros_javascript.append(dato)
                
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Error de parseo en línea {num_linea}: {e}")
        except Exception as e:
            print(f"⚠️ Error inesperado en línea {num_linea}: {e}")

print(f"✅ Filtrado inicial completado. Candidatos JS encontrados: {len(registros_javascript)}")

# 3. Convertir a DataFrame solo los registros JS válidos
df = pd.DataFrame(registros_javascript)

# 4. Eliminar duplicados en el código JavaScript
if not df.empty:
    print("🔄 Eliminando duplicados redundantes...")
    conteo_antes = len(df)
    df = df.drop_duplicates(subset=["func_limpia"])
    print(f"📊 Registros JS eliminados por duplicidad: {conteo_antes - len(df)}")
    print(f"📊 Total de funciones JavaScript listas para el modelo: {len(df)}")

    # 5. Guardar el subconjunto JS en formato JSON Lines
    archivo_salida = "dataset_js_limpio.json"
    df.to_json(archivo_salida, orient="records", lines=True)
    print(f"💾 ¡Dataset exclusivo de JavaScript guardado en '{archivo_salida}'!")
else:
    print("❌ No se encontraron funciones que cumplan con los patrones heurísticos de JavaScript.")