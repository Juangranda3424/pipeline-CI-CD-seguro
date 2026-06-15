import os
import re
import joblib
import pandas as pd
import scipy.sparse as sp
import warnings
from sklearn.ensemble import RandomForestClassifier

# Silenciar advertencias de versión para limpiar la salida del pipeline
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ==========================
# CARGAR MODELO
# ==========================
model = joblib.load("ml/modelo_seguridad.joblib")
vectorizer = joblib.load("ml/vectorizador.joblib")

# ==========================
# EXTRAER FEATURES
# ==========================
def extract_features(code_text):
    features = {}

    dangerous_patterns = [
        r'eval\(',
        r'exec\(',
        r'subprocess\.',
        r'SELECT.*FROM',
        r'strcpy\(',
        r'sprintf\(',
        r'strcat\(',
        r'system\(',
        r'malloc\(',
        r'memcpy\('
    ]

    sanitization_patterns = [
        r'escape\(',
        r'sanitize\(',
        r'strip\(',
        r'replace\(',
        r'==\s*NULL',
        r'<\s*0',
        r'assert\(',
        r'sizeof\('
    ]

    # Guardamos los conteos individuales mapeando exactamente los mismos patrones de la lista
    dangerous_matches = {p: len(re.findall(p, code_text)) for p in dangerous_patterns}
    
    features['dangerous_calls'] = sum(dangerous_matches.values())

    features['sanitization_checks'] = sum(
        len(re.findall(p, code_text))
        for p in sanitization_patterns
    )

    max_depth = 0
    current_depth = 0

    for char in code_text:
        if char == "{":
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == "}":
            current_depth -= 1

    features["ast_depth_approx"] = max_depth

    return features, dangerous_matches

# ==========================
# LEER ARCHIVO MODIFICADO
# ==========================
with open("changed_code.txt", "r", encoding="utf-8") as f:
    raw_diff = f.read()

# OPTIMIZACIÓN: Limpiar el formato Diff de Git para la IA
# Quitamos los indicadores de líneas añadidas '+' al inicio de la línea para dejar el código limpio
cleaned_lines = []
for line in raw_diff.splitlines():
    if line.startswith('+'):
        cleaned_lines.append(line[1:])  # Quita el primer carácter '+'
    elif not line.startswith('-'):      # Ignora líneas eliminadas, conserva el contexto
        cleaned_lines.append(line)

code_to_analyze = "\n".join(cleaned_lines)

# Extraer métricas y el diccionario de coincidencias críticas utilizando el código limpio
features_dict, dangerous_matches = extract_features(code_to_analyze)
manual = pd.DataFrame([features_dict])

X_tokens = vectorizer.transform([code_to_analyze])
X_manual = sp.csr_matrix(manual.values)
X = sp.hstack([X_tokens, X_manual])

# ==========================
# REGLETA DE SEGURIDAD (CRITICAL FAILSAFE)
# ==========================
# CORREGIDO: Buscamos exactamente las llaves r'eval\(' y r'exec\(' sin caracteres corruptos
if dangerous_matches.get(r'eval\(', 0) > 0 or dangerous_matches.get(r'exec\(', 0) > 0:
    print("🚨 [CRITICAL FAILSAFE] Se detectó una llamada directa a eval() o exec()!")
    print(f"Detalle de hallazgos: {dangerous_matches}")
    print("Resultado: VULNERABLE (Bloqueo preventivo por regla estricta)")
    exit(1)

# ==========================
# PREDICCIÓN CON MACHINE LEARNING
# ==========================
prediction = model.predict(X)[0]
probability = model.predict_proba(X)[0]

print(f"Predicción del Modelo: {prediction}")

if prediction == 1:
    print("VULNERABLE")
    print(f"Probabilidad: {max(probability):.4f}")
    exit(1)

print("SEGURO")
exit(0)