// Base de datos simulada en memoria
let inventario = [
    { id: 1, nombre: "Pan de Ambato", precio: 0.15, categoria: "Sal", stock: 120 },
    { id: 2, nombre: "Croissant de Queso", precio: 0.60, categoria: "Dulce", stock: 45 },
    { id: 3, nombre: "Pan de Yuca", precio: 0.35, categoria: "Especialidad", stock: 80 },
    { id: 4, nombre: "Pastel de Chocolate", precio: 12.00, categoria: "Pastelería", stock: 10 }
];

let proximoId = 5;

export const PanModel = {
    findAll: () => {
        return inventario;
    },

    findById: (id) => {
        return inventario.find(p => p.id === id);
    },

    create: (data) => {
        const nuevoPan = {
            id: proximoId++,
            nombre: data.nombre,
            precio: parseFloat(data.precio),
            categoria: data.categoria,
            stock: parseInt(data.stock)
        };
        inventario.push(nuevoPan);
        return nuevoPan;
    },

    update: (id, data) => {
        const indice = inventario.findIndex(p => p.id === id);
        if (indice === -1) return null;

        inventario[indice] = {
            ...inventario[indice],
            nombre: data.nombre || inventario[indice].nombre,
            precio: data.precio !== undefined ? parseFloat(data.precio) : inventario[indice].precio,
            categoria: data.categoria || inventario[indice].categoria,
            stock: data.stock !== undefined ? parseInt(data.stock) : inventario[indice].stock
        };
        return inventario[indice];
    },

    delete: (id) => {
        const existe = inventario.some(p => p.id === id);
        if (!existe) return false;

        inventario = inventario.filter(p => p.id !== id);
        return true;
    }
};