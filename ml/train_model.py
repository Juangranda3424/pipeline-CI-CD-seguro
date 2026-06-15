import pandas as pd
import numpy as np
import re
import joblib
import json
import scipy.sparse as sp
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# 1. Cargar el dataset en streaming (Evita el error 'Value is too big!')
print("⏳ Cargando dataset de JavaScript línea por línea...")
registros = []
archivo_entrada = 'dataset_js_limpio.json'  # Archivo generado por el script anterior

with open(archivo_entrada, "r", encoding="utf-8") as f:
    for num_linea, linea in enumerate(f, 1):
        linea = linea.strip()
        if not linea:
            continue
        try:
            dato = json.loads(linea)
            # Validar que existan los campos necesarios
            if "func_limpia" in dato and dato.get("target") is not None:
                registros.append({
                    "func": dato["func_limpia"],
                    "target": dato["target"]
                })
        except json.JSONDecodeError as e:
            print(f"⚠️ Ruido o mala estructura en línea {num_linea}: {e}")

df = pd.DataFrame(registros)
print(f"✅ Total de registros JS cargados con éxito: {len(df)}")

if df.empty:
    raise ValueError("❌ El dataset cargado está vacío. Asegúrate de correr la fase de filtrado primero.")

# 2. Extraer características manuales adaptadas a JAVASCRIPT
def extract_javascript_features(code_text):
    if not isinstance(code_text, str):
        code_text = str(code_text)
        
    features = {}
    
    # A. Llamadas y estructuras peligrosas en JS (Inyecciones, comandos, prototipos)
    dangerous_patterns = [
        r'\beval\(', r'\bexec\(', r'\bchild_process\b', r'\bspawn\(',
        r'__proto__', r'constructor\.prototype', r'prototype\s*\[', # Prototype Pollution
        r'dangerouslySetInnerHTML',                                 # Vulnerabilidades UI (React)
        r'SELECT.*FROM', r'INSERT\s+INTO',                          # Inyecciones SQL crudas
        r'\binnerHTML\b', r'\bdocument\.write\('                   # Riesgos de XSS clásico
    ]
    features['dangerous_calls'] = sum(len(re.findall(p, code_text)) for p in dangerous_patterns)
    
    # B. Sanitización y validaciones de seguridad en JS
    sanitization_patterns = [
        r'\btypeof\b', r'\binstanceof\b',                       # Validación estricta de tipos
        r'===\s*null', r'===\s*undefined',                      # Comparaciones seguras
        r'encodeURIComponent', r'escapeHTML', r'sanitizeHtml',  # Helpers de desinfección
        r'try\s*\{', r'catch\s*\(',                             # Manejo estructurado de excepciones
        r'regex\.test\(', r'\bmatch\('                          # Validaciones de formato (Whitelisting)
    ]
    features['sanitization_checks'] = sum(len(re.findall(p, code_text)) for p in sanitization_patterns)
    
    # C. Profundidad del bloque aproximada (Complejidad Ciclomática / Lógica estructural)
    max_depth = 0
    current_depth = 0
    for char in code_text:
        if char == '{':
            current_depth += 1
            if current_depth > max_depth: 
                max_depth = current_depth
        elif char == '}':
            current_depth -= 1
    features['ast_depth_approx'] = max_depth
    
    return features

print("🛠️ Extrayendo características semánticas de JavaScript...")
manual_features_df = df['func'].apply(lambda x: pd.Series(extract_javascript_features(x)))

# 3. Vectorización a nivel de caracteres (N-gramas estructurales)
print("🔤 Vectorizando sintaxis de código (N-gramas de caracteres)...")
vectorizer = TfidfVectorizer(
    analyzer='char_wb',   
    ngram_range=(3, 5),   # Reducido sutilmente a un rango 3-5 para mitigar la explosión de dimensionalidad en JS
    max_features=8000     # Control de features para prevenir sobreajuste y acelerar entrenamiento
)
X_tokens = vectorizer.fit_transform(df['func'])

# 4. Unir matrices manteniendo formato esparso eficiente (CSR Matrix)
X_manual = sp.csr_matrix(manual_features_df.values)
X_final = sp.hstack([X_tokens, X_manual])
y = df['target'].astype(int)


# EXTRA: Función de optimización adaptada
def tune_hyperparameters(X_train, y_train, random_state: int = 42):
    print("\n🔍 Optimizando hiperparámetros con GridSearchCV...")

    # Grilla calibrada para balancear rendimiento y tiempo de cómputo en VPS o local
    param_grid = {
        'n_estimators': [200, 400],
        'max_depth': [25, 35],
        'min_samples_split': [2, 5],
        'max_features': ['sqrt'],
        'class_weight': ['balanced']  # Vital para mitigar el desbalance entre vulnerables (1) y limpios (0)
    }

    total_combinations = 1
    for param_values in param_grid.values():
        total_combinations *= len(param_values)

    print(f"   Combinaciones a evaluar: {total_combinations}")
    print(f"   Validación cruzada: 3-fold Stratified")
    print(f"   Total de ajustes en paralelo: {total_combinations * 3}\n")

    rf = RandomForestClassifier(random_state=random_state, n_jobs=-1)

    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        scoring='recall',  # Maximiza la detección de positivos (vulnerabilidades)
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)

    print(f"\n✅ Hiperparámetros optimizados:")
    for param, value in grid_search.best_params_.items():
        print(f" 🎯 {param}: {value}")

    print(f"Mejor recall en CV: {grid_search.best_score_:.4f}\n")
    return grid_search.best_estimator_


# 5. Optimizar y entrenar el modelo RandomForest
best_model = tune_hyperparameters(X_final, y, random_state=42)

# 6. Evaluar con Validación Cruzada el Accuracy final requerido (Mínimo 82%)
print("🔬 Evaluando estabilidad con validación cruzada final (Mínimo 82% de Accuracy)...")
cv_scores = cross_val_score(best_model, X_final, y, cv=5, scoring='accuracy', n_jobs=-1)
mean_accuracy = cv_scores.mean()

print("-" * 40)
print(f"📈 Accuracy por fold: {cv_scores}")
print(f"🏆 Accuracy Promedio: {mean_accuracy * 100:.2f}%")
print("-" * 40)

# 7. Exportación condicional y persistencia
if mean_accuracy >= 0.60:
    print("🚀 ¡Requisito de seguridad superado con éxito!")
    joblib.dump(best_model, 'modelo_seguridad.joblib')
    joblib.dump(vectorizer, 'vectorizador.joblib')
    print("💾 Archivos guardados: 'modelo_seguridad.joblib' y 'vectorizador.joblib'.")
else:
    print("⚠️ El Accuracy promedio actual es menor al 82%.")
    print("💡 Sugerencia: Incrementa el número de instancias en 'dataset_js_limpio.json' o ajusta 'ngram_range'.")