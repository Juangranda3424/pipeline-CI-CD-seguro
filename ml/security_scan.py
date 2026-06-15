import os
import re
import joblib
import pandas as pd
import scipy.sparse as sp
from sklearn.ensemble import RandomForestClassifier

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

    features['dangerous_calls'] = sum(
        len(re.findall(p, code_text))
        for p in dangerous_patterns
    )

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

    return features

# ==========================
# LEER ARCHIVO MODIFICADO
# ==========================

with open("changed_code.txt", "r", encoding="utf-8") as f:
    code = f.read()

manual = pd.DataFrame([extract_features(code)])

X_tokens = vectorizer.transform([code])
X_manual = sp.csr_matrix(manual.values)

X = sp.hstack([X_tokens, X_manual])

# ==========================
# PREDICCION
# ==========================

prediction = model.predict(X)[0]
probability = model.predict_proba(X)[0]

print(f"Predicción: {prediction}")

if prediction == 1:
    print("VULNERABLE")
    print(f"Probabilidad: {max(probability):.4f}")
    exit(1)

print("SEGURO")
exit(0)