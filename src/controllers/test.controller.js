export const ejecutarCodigo = (req, res) => {

    const { codigo } = req.body;

    const resultado = eval(codigo);

    res.json({
        resultado
    });
};