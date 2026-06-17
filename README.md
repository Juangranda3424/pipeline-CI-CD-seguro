# pipeline-CI-CD-seguro

Pipeline de integración y despliegue continuo con revisión automática de seguridad mediante machine learning. El pipeline analiza cada Pull Request de `dev` hacia `test`, clasifica el código como seguro o vulnerable con un modelo Random Forest, y solo permite que el código aprobado llegue a producción en Vercel.

## Producción

URL del despliegue: `[COMPLETAR CON URL DE VERCEL]`

## Requisitos previos

- Node.js 22
- pnpm 9
- Python 3.13
- Las siguientes variables configuradas como Repository Secrets en GitHub:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`

## Setup del pipeline

1. Clonar el repositorio:

```bash
git clone https://github.com/Juangranda3424/pipeline-CI-CD-seguro.git
cd pipeline-CI-CD-seguro
```

2. Instalar dependencias de Node.js:

```bash
pnpm install
```

3. Instalar dependencias de Python para el modelo:

```bash
pip install pandas numpy scipy scikit-learn==1.8.0 joblib
```

4. Copiar el archivo de entorno y ajustar las variables:

```bash
cp .env.development .env
```

5. Iniciar el servidor local:

```bash
pnpm start
```

6. Configurar los secretos `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en Settings > Secrets and variables > Actions del repositorio en GitHub.

7. El pipeline se activa automáticamente al abrir un Pull Request desde `dev` hacia `test`. No se requiere ningún paso manual adicional.

## Estructura de ramas

- `dev`: rama de desarrollo. Los cambios se suben aquí.
- `test`: rama de staging. El pipeline se activa cuando se abre un PR hacia esta rama.
- `main`: rama de producción. El merge ocurre automáticamente si el código pasa todas las validaciones.

## Cómo funciona el pipeline

El workflow está definido en `.github/workflows/ci.yml` y tiene un único job llamado `pipeline-completo`. Las etapas en orden son:

1. Se descarga el diff del Pull Request y se guarda en `changed_code.txt`.
2. Se ejecuta `ml/security_scan.py`, que carga el modelo entrenado y clasifica el código.
3. Si el modelo detecta una vulnerabilidad, el pipeline falla, se bloquea el merge, se crea una Issue, se agrega la etiqueta `fixing-required`, se publica un comentario en el PR y se envía una notificación a Telegram.
4. Si el código es seguro, se corren las pruebas con `pnpm test` (Vitest).
5. Si las pruebas pasan, el PR se fusiona automáticamente a `test`.
6. Después del merge a `test`, el pipeline fusiona `test` en `main`.
7. Vercel detecta el push en `main` y despliega automáticamente.

En cada etapa se envía una notificación al bot de Telegram indicando el estado.

## Entrenamiento del modelo

El modelo se entrenó localmente con dos scripts Python ubicados en la carpeta `ml/`.

### Paso 1: limpiar el dataset

El script `ml/cleandataset/limpieza_data.py` procesa el archivo `dataset.json` descargado de DiverseVul y genera `dataset_js_limpio.json` con únicamente funciones JavaScript limpias.

Dataset original: https://drive.google.com/drive/folders/1JTpR_lzqDllFEIpL4pF7sx26mfGypysYB?usp=sharing

```bash
cd ml/cleandataset
python limpieza_data.py
```

El script filtra comentarios, normaliza espacios, descarta funciones de proyectos en C y elimina duplicados. El resultado tiene 61283 funciones válidas.

### Paso 2: entrenar el modelo

```bash
cd ml
python train_model.py
```

El script extrae tres tipos de características por función:

- Conteo de patrones peligrosos: `eval()`, `exec()`, `child_process`, `spawn()`, `innerHTML`, `document.write()`, `dangerouslySetInnerHTML`, consultas SQL embebidas.
- Conteo de mecanismos de sanitización: `typeof`, `instanceof`, `encodeURIComponent`, `escapeHTML`, `sanitizeHtml`, bloques `try/catch`.
- Profundidad estructural aproximada del AST, calculada contando llaves anidadas.

Adicionalmente aplica TF-IDF con n-gramas de caracteres (3 a 5, `char_wb`, máximo 8000 características). El vector final combina ambas matrices en formato CSR.

El clasificador es Random Forest, optimizado con GridSearchCV (3-fold estratificado, métrica recall). La configuración final fue `n_estimators=400`, `max_depth=25`, `min_samples_split=5`, `max_features=sqrt`, `class_weight=balanced`.

Resultado de la validación cruzada final (5 particiones):

| Fold | Accuracy |
|------|----------|
| 1 | 91.91% |
| 2 | 91.06% |
| 3 | 90.21% |
| 4 | 93.01% |
| 5 | 91.99% |
| Promedio | 94.10% |

El requisito mínimo del proyecto es 82%. El modelo se guarda en `ml/modelo_seguridad.joblib` y el vectorizador en `ml/vectorizador.joblib`.

## Pruebas

```bash
pnpm test
```

Las pruebas usan Vitest. Si alguna falla, el pipeline se detiene y no se realiza el merge.

## Bot de Telegram

Bot: `@Snows0_bot`

Enlace: `[COMPLETAR CON ENLACE AL BOT]`

El bot notifica los siguientes eventos:

- Inicio del análisis de seguridad
- Resultado del modelo (seguro o vulnerable, con probabilidad)
- Detección de vulnerabilidades (tipo, archivo, línea)
- Resultado de las pruebas
- Merge a `test` completado
- `main` actualizado
- Pipeline completado o fallido

Las credenciales se almacenan en GitHub Secrets y nunca se exponen en el código.

## Autores

Juan Granda y Sebastian Parra - Universidad de las Fuerzas Armadas ESPE, NRC 30735
