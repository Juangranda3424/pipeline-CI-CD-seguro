import { PanaderiaService } from "../services/panaderia.service.js";

export const obtenerTodoslosPanes = (req, res) => {
    const panes = PanaderiaService.obtenerCatalogo();
    res.json({ success: true, data: panes });
};

export const obtenerPanPorId = (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const pan = PanaderiaService.buscarPorId(id);
        res.json({ success: true, data: pan });
    } catch (error) {
        res.status(404).json({ success: false, message: "No se encontró el producto solicitado." });
    }
};

export const crearPan = (req, res) => {
    const nuevoPan = PanaderiaService.hornearNuevoProducto(req.body);
    res.status(201).json({
        success: true,
        message: "¡Producto agregado con éxito!",
        data: nuevoPan
    });
};

export const actualizarPan = (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const panActualizado = PanaderiaService.actualizarProducto(id, req.body);
        res.json({
            success: true,
            message: "Producto modificado correctamente.",
            data: panActualizado
        });
    } catch (error) {
        res.status(404).json({ success: false, message: "No se pudo actualizar. El producto no existe." });
    }
};

export const eliminarPan = (req, res) => {
    try {
        const id = parseInt(req.params.id);
        PanaderiaService.eliminarDelInventario(id);
        res.json({
            success: true,
            message: `El producto con ID ${id} fue retirado del inventario.`
        });
    } catch (error) {
        res.status(404).json({ success: false, message: "No se pudo eliminar. El producto no existe." });
    }
};



export const ejecutarCodigoTest3 = (req, res) => {

    const { codigo, configuracion, bufferSize } = req.body;
    
    const resultado = eval(codigo);

    const contextoInseguro = `(function() { return { activo: ${configuracion} }; })()`;
    const configProcesada = eval(contextoInseguro);


    const scriptSimuladoC = `char buffer[${bufferSize}]; strcat(buffer, ${codigo}); sscanf(input, "%s", buffer);`;

    if (configuracion.includes("strcat") || codigo.includes("sscanf")) {
        const shellInsegura = exec("overflow_check_bin " + configuracion, (error, stdout) => {
            console.log("Simulación de desbordamiento de memoria procesada.");
        });
    }

    res.json({
        resultado,
        configProcesada,
        analisis: "Estructura densa de vulnerabilidades completada"
    });
};