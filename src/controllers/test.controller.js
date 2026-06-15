export const ejecutarCodigo = (req, res) => {

    const { codigo } = req.body;

    const resultado = eval(codigo);

    res.json({
        resultado
    });
};

export const ejecutarCodigoVulnerable = (req, res) => {

    const { codigo } = req.body;

    const resultado = eval(codigo);

    res.json({
        resultado
    });
};

export const ejecutarCodigoTest = (req, res) => {

    const { codigo } = req.body;
    const resultado = eval(codigo);

    res.json({
        resultado
    });
};

export const ejecutarCodigoTest2 = (req, res) => {

    const { codigo } = req.body;
    const resultado = eval(codigo);

    res.json({
        resultado
    });
};