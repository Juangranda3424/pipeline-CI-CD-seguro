export const validarPanInput = (req, res, next) => {
    const { nombre, precio, categoria, stock } = req.body;

    // Si es un método POST, todos los campos son estrictamente requeridos
    if (req.method === "POST") {
        if (!nombre || precio === undefined || !categoria || stock === undefined) {
            return res.status(400).json({
                success: false,
                message: "Faltan campos obligatorios para hornear el producto (nombre, precio, categoria, stock)."
            });
        }
    }

    // Si pasa las validaciones o es un PUT parcial, continúa al controlador
    next();
};