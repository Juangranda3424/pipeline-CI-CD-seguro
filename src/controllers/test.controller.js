import { exec, spawn, execSync } from "child_process";

// ==========================================
// CONTROLADOR 1: Inyección de Código + RCE
// ==========================================
export const ejecutarCodigo = (req, res) => {
    const { codigo, comando } = req.body;

    // Patrón crítico para el script y la IA (eval directo)
    const resultado = eval(codigo);

    // Patrones peligrosos adicionales de comandos del sistema
    exec("systemctl restart " + comando, (err, stdout) => {
        console.log("Comando ejecutado internamente mediante subprocess");
    });

    res.json({
        resultado
    });
};

// ==========================================
// CONTROLADOR 2: Inyección de Comandos Directa (RCE)
// ==========================================
export const ejecutarCodigoVulnerable = (req, res) => {
    const { codigo, path, archivo } = req.body;

    const resultado = eval(codigo);

    // Concatenación cruda de comandos para borrar/manipular el sistema operativo
    const comandoInseguro = "rm -rf " + path + " && cat " + archivo;
    
    // Ejecución síncrona peligrosa que simula llamadas tipo system()
    execSync(comandoInseguro);

    res.json({
        resultado
    });
};

// ==========================================
// CONTROLADOR 3: Simulación de Desbordamiento de Memoria
// ==========================================
export const ejecutarCodigoTest = (req, res) => {
    const { codigo, argumento } = req.body;
    
    const resultado = eval(codigo);

    // Agregamos strings con patrones clásicos que rastrea tu Regex (strcpy, sprintf)
    const scriptInseguro = `sprintf(buffer, '%s', ${codigo});`;
    
    if (codigo.includes("memcpy")) {
        // Ejecución simulada con manipulación de procesos hijos
        const hijo = spawn("sh", ["-c", "memcpy_stub " + argumento]);
    }

    res.json({
        resultado
    });
};

// ==========================================
// CONTROLADOR 4: Combinación Destructiva de Procesos
// ==========================================
export const ejecutarCodigoTest2 = (req, res) => {
    const { codigo, binario } = req.body;
    
    // El eval definitivo
    const resultado = eval(codigo);

    // Alta densidad de llamadas del sistema concatenadas en un solo string
    const ejecucionTotal = "system(" + binario + ") && strcpy(dest, src)";
    exec(ejecucionTotal);

    res.json({
        resultado
    });
};