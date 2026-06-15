import sys
import re
import joblib
import scipy.sparse as sp
import pandas as pd

def extract_features(code_text):
    # Debe ser EXACTAMENTE la misma función que usaste en el entrenamiento
    features = {}
    dangerous_patterns = [r'eval\(', r'exec\(', r'subprocess\.', r'SELECT.*FROM', r'strcpy\(', r'sprintf\(', r'strcat\(', r'system\(', r'malloc\(']
    sanitization_patterns = [r'escape\(', r'sanitize\(', r'strip\(', r'replace\(', r'if\s*\([^)]*==\s*NULL\)', r'if\s*\([^)]*<\s*0\)', r'assert\(']
    
    features['dangerous_calls'] = sum(len(re.findall(p, code_text)) for p in dangerous_patterns)
    features['sanitization_checks'] = sum(len(re.findall(p, code_text)) for p in sanitization_patterns)
    
    max_depth, current_depth = 0, 0
    for char in code_text:
        if char == '{':
            current_depth += 1
            if current_depth > max_depth: max_depth = current_depth
        elif char == '}':
            current_depth -= 1
    features['ast_depth_approx'] = max_depth
    return features

def main():
    # 1. Recibir el código modificado (el pipeline debe pasarlo como argumento o leerlo de un archivo)
    # Por simplicidad, leeremos un archivo temporal que el pipeline CI/CD genere con el 'diff'
    try:
        with open('codigo_modificado.txt', 'r') as file:
            codigo_nuevo = file.read()
    except FileNotFoundError:
        print("Error: No se encontró el archivo de código a analizar.")
        sys.exit(1)

    # 2. Cargar el modelo y vectorizador previamente exportados
    try:
        model = joblib.load('modelo_seguridad.joblib')
        vectorizer = joblib.load('vectorizador.joblib')
    except Exception as e:
        print(f"Error cargando los modelos: {e}")
        sys.exit(1)

    # 3. Procesar el nuevo código
    manual_features = extract_features(codigo_nuevo)
    X_manual = sp.csr_matrix(pd.Series(manual_features).values)
    
    X_tokens = vectorizer.transform([codigo_nuevo])
    
    X_final = sp.hstack([X_tokens, X_manual])

    # 4. Predecir
    prediccion = model.predict(X_final)[0]
    probabilidades = model.predict_proba(X_final)[0]
    
    prob_vulnerable = probabilidades[1] * 100

    if prediccion == 1:
        print(f"::error::VULNERABILIDAD DETECTADA. Probabilidad: {prob_vulnerable:.2f}%")
        print("El código no cumple con los estándares de seguridad (Shift-Left Security).")
        # El exit(1) hace que el job de GitHub Actions falle, bloqueando el merge automático.
        sys.exit(1) 
    else:
        print(f"CÓDIGO SEGURO. Probabilidad de vulnerabilidad es solo {prob_vulnerable:.2f}%.")
        print("Aprobado para la siguiente fase.")
        sys.exit(0)

if __name__ == "__main__":
    main()