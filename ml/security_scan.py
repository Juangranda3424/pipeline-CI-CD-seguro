import os
import re
import joblib
import pandas as pd
import scipy.sparse as sp
import warnings

# Silenciar advertencias de versión para limpiar la salida del pipeline
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ==========================
# CARGAR MODELO
# ==========================
model = joblib.load("ml/modelo_seguridad.joblib")
vectorizer = joblib.load("ml/vectorizador.joblib")

# ==========================
# PROCESAR EL DIFF LÍNEA POR LÍNEA
# ==========================
with open("changed_code.txt", "r", encoding="utf-8") as f:
    raw_diff = f.read()

dangerous_patterns = [
    r'eval\(', r'exec\(', r'subprocess\.', r'SELECT.*FROM',
    r'strcpy\(', r'sprintf\(', r'strcat\(', r'system\(',
    r'malloc\(', r'memcpy\('
]

current_file = "Desconocido"
current_line_in_file = 0
vulnerabilities_found = []
cleaned_lines = []

# Analizar la estructura del diff para capturar metadatos reales de Git
for line in raw_diff.splitlines():
    # Detectar el archivo actual en el diff de git
    if line.startswith('+++ b/'):
        current_file = line[6:]
        continue
    
    # Rastrear los bloques de líneas (Hunk headers) de git @@ -input,len +output,len @@
    if line.startswith('@@'):
        match = re.search(r'\+(\d+)', line)
        if match:
            current_line_in_file = int(match.group(1)) - 1
        continue

    # Solo nos interesan las líneas agregadas o el contexto secuencial para el conteo
    if line.startswith('+'):
        current_line_in_file += 1
        actual_code = line[1:]
        cleaned_lines.append(actual_code)
        
        # Evaluar patrones peligrosos estrictos en la línea agregada
        for pattern in dangerous_patterns:
            if re.search(pattern, actual_code):
                vulnerabilities_found.append({
                    "file": current_file,
                    "line": current_line_in_file,
                    "code": actual_code.strip(),
                    "pattern": pattern.replace(r'\(', '()')
                })
    elif not line.startswith('-'):
        current_line_in_file += 1
        cleaned_lines.append(line)

code_to_analyze = "\n".join(cleaned_lines)

# ==========================
# EXTRAER FEATURES PARA LA IA
# ==========================
def extract_features_ia(code_text):
    features = {}
    sanitization_patterns = [
        r'escape\(', r'sanitize\(', r'strip\(', r'replace\(',
        r'==\s*NULL', r'<\s*0', r'assert\(', r'sizeof\('
    ]
    
    features['dangerous_calls'] = sum(len(re.findall(p, code_text)) for p in dangerous_patterns)
    features['sanitization_checks'] = sum(len(re.findall(p, code_text)) for p in sanitization_patterns)

    max_depth, current_depth = 0, 0
    for char in code_text:
        if char == "{":
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == "}":
            current_depth -= 1
            
    features["ast_depth_approx"] = max_depth
    return features

features_dict = extract_features_ia(code_to_analyze)
manual = pd.DataFrame([features_dict])

X_tokens = vectorizer.transform([code_to_analyze])
X_manual = sp.csr_matrix(manual.values)
X = sp.hstack([X_tokens, X_manual])

# ==========================
# EVALUAR VEREDICTOS Y EXPORTAR
# ==========================
is_vulnerable = False
reason_msg = ""
details_msg = ""

# 1. Validación estricta por Failsafe (Buscamos si hay eval o exec explícitos capturados)
critical_triggers = [v for v in vulnerabilities_found if 'eval' in v['pattern'] or 'exec' in v['pattern']]

if critical_triggers:
    is_vulnerable = True
    reason_msg = "CRITICAL FAILSAFE: Inyección directa mediante eval() o exec()."
    details_lines = [f"- 📁 *Archivo:* `{v['file']}` | 🔢 *Línea:* `{v['line']}`\\n  💻 `code: {v['code']}`" for v in critical_triggers]
    details_msg = "\\n".join(details_lines)
else:
    # 2. Si pasa las reglas duras, evalúa la Inteligencia Artificial
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0]
    
    if prediction == 1:
        is_vulnerable = True
        reason_msg = f"Clasificación por IA (Random Forest) con probabilidad {max(probability):.4f}."
        # Si la IA asume riesgo y hay vulnerabilidades genéricas registradas, las muestra
        if vulnerabilities_found:
            details_lines = [f"- 📁 *Archivo:* `{v['file']}` | 🔢 *Línea:* `{v['line']}`\\n  💻 `code: {v['code']}`" for v in vulnerabilities_found]
            details_msg = "\\n".join(details_lines)
        else:
            details_msg = "- Detectados patrones de estructura anómalos o de alto riesgo en los archivos modificados."

# Exportar datos al entorno de GitHub Actions si está disponible
if "GITHUB_ENV" in os.environ:
    with open(os.environ["GITHUB_ENV"], "a") as env_file:
        if is_vulnerable:
            env_file.write(f"SECURITY_STATUS=VULNERABLE\n")
            env_file.write(f"SECURITY_REASON={reason_msg}\n")
            env_file.write(f"SECURITY_DETAILS={details_msg}\n")
        else:
            env_file.write("SECURITY_STATUS=SEGURO\n")

# Salida para consola e interrupción del Pipeline
if is_vulnerable:
    print(f"🚨 CLASIFICACIÓN: VULNERABLE")
    print(f"Motivo: {reason_msg}")
    print("Detalles de las líneas afectadas:")
    for v in vulnerabilities_found:
        print(f"  - Archivo: {v['file']} | Línea: {v['line']} | Código: {v['code']}")
    exit(1)

print("✅ CLASIFICACIÓN: SEGURO")
exit(0)