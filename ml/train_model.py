import pandas as pd
import numpy as np
import re
import joblib
import scipy.sparse as sp
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# 1. Cargar y limpiar el dataset
print("Cargando dataset...")
df = pd.read_json('function.json')
df = df.dropna(subset=['func', 'target'])
print(f"Total de registros cargados: {len(df)}")

# 2. Extraer características manuales
def extract_features(code_text):
    if not isinstance(code_text, str):
        code_text = str(code_text)
        
    features = {}
    
    # A. Llamadas peligrosas
    dangerous_patterns = [
        r'eval\(', r'exec\(', r'subprocess\.', r'SELECT.*FROM', 
        r'strcpy\(', r'sprintf\(', r'strcat\(', r'system\(', r'malloc\(', r'memcpy\('
    ]
    features['dangerous_calls'] = sum(len(re.findall(p, code_text)) for p in dangerous_patterns)
    
    # B. Sanitización
    sanitization_patterns = [
        r'escape\(', r'sanitize\(', r'strip\(', r'replace\(', 
        r'==\s*NULL', r'<\s*0', r'assert\(', r'sizeof\('
    ]
    features['sanitization_checks'] = sum(len(re.findall(p, code_text)) for p in sanitization_patterns)
    
    # C. Profundidad del AST
    max_depth = 0
    current_depth = 0
    for char in code_text:
        if char == '{':
            current_depth += 1
            if current_depth > max_depth: max_depth = current_depth
        elif char == '}':
            current_depth -= 1
    features['ast_depth_approx'] = max_depth
    
    return features

print("Extrayendo características manuales...")
manual_features_df = df['func'].apply(lambda x: pd.Series(extract_features(x)))

# 3. Vectorización a nivel de caracteres (Sintaxis pura)
print("Vectorizando sintaxis de código (N-gramas de caracteres)...")
vectorizer = TfidfVectorizer(
    analyzer='char_wb',   
    ngram_range=(3, 6),   
    max_features=10000     
)
X_tokens = vectorizer.fit_transform(df['func'])

# 4. Unir matrices (Mantenemos el formato esparso eficiente)
X_manual = sp.csr_matrix(manual_features_df.values)
X_final = sp.hstack([X_tokens, X_manual])
y = df['target']


# EXTRA: Función de optimización adaptada para la matriz esparsa final
def tune_hyperparameters(X_train, y_train, random_state: int = 42):
    """
    Busca los mejores hiperparámetros usando GridSearchCV.
    Prioriza mejorar el recall sin sacrificar demasiado la precision.
    """
    print("\n🔍 Buscando mejores hiperparámetros...")

    param_grid = {
        'n_estimators': [300, 500],
        'max_depth': [20, 30],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'max_features': ['sqrt', 'log2'],  # Optimizado para >10,000 columnas
        'class_weight': ['balanced']
    }

    # Calcular total de combinaciones
    total_combinations = 1
    for param_values in param_grid.values():
        total_combinations *= len(param_values)

    print(f"   Total de combinaciones a probar: {total_combinations}")
    print(f"   Validación cruzada: 3-fold")
    print(f"   Total de entrenamientos: {total_combinations * 3}")
    print(f"   Esto puede tomar varios minutos...\n")

    rf = RandomForestClassifier(random_state=random_state, n_jobs=-1)

    # El scoring 'recall' asegura priorizar la detección de vulnerabilidades
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        scoring='recall',
        n_jobs=-1,
        verbose=2
    )

    grid_search.fit(X_train, y_train)

    print(f"\n✅ Búsqueda completada")
    print(f"Mejores hiperparámetros encontrados:")
    for param, value in grid_search.best_params_.items():
        print(f" - {param}: {value}")

    print(f"Mejor recall obtenido en CV: {grid_search.best_score_:.4f}\n")
    return grid_search.best_estimator_


# 5. Optimizar y entrenar el modelo RandomForest
best_model = tune_hyperparameters(X_final, y, random_state=42)

# 6. Evaluar con Validación Cruzada el Accuracy final requerido (Mínimo 82%)
print("Iniciando validación cruzada final (Evaluando accuracy mínimo del 82%)...")
cv_scores = cross_val_score(best_model, X_final, y, cv=5, scoring='accuracy', n_jobs=-1)
mean_accuracy = cv_scores.mean()

print("-" * 30)
print(f"Accuracy por fold: {cv_scores}")
print(f"Accuracy Promedio: {mean_accuracy * 100:.2f}%")
print("-" * 30)

# 7. Exportación condicional
if mean_accuracy >= 0.82:
    print("¡Requisito superado! Procediendo a guardar el modelo final...")
    # 'best_model' ya viene entrenado con todo X_final gracias al comportamiento por defecto de GridSearchCV(refit=True)
    joblib.dump(best_model, 'modelo_seguridad.joblib')
    joblib.dump(vectorizer, 'vectorizador.joblib')
    print("✅ Archivos exportados con éxito: 'modelo_seguridad.joblib' y 'vectorizador.joblib'.")
else:
    print("⚠️ Aún no se alcanzó el 82% de Accuracy promedio. El dataset podría requerir más datos o balanceo adicional.")