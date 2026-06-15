import { PanModel } from "../models/pan.model.js";

export const PanaderiaService = {
    obtenerCatalogo: () => {
        return PanModel.findAll();
    },

    buscarPorId: (id) => {
        const producto = PanModel.findById(id);
        if (!producto) throw new Error("PRODUCTO_NO_ENCONTRADO");
        return producto;
    },

    hornearNuevoProducto: (datos) => {
        return PanModel.create(datos);
    },

    actualizarProducto: (id, datos) => {
        const actualizado = PanModel.update(id, datos);
        if (!actualizado) throw new Error("PRODUCTO_NO_EXISTE_UPDATE");
        return actualizado;
    },

    eliminarDelInventario: (id) => {
        const eliminado = PanModel.delete(id);
        if (!eliminado) throw new Error("PRODUCTO_NO_EXISTE_DELETE");
        return true;
    }
};