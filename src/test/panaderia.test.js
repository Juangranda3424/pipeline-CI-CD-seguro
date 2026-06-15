import { describe, it, expect } from "vitest";
import request from "supertest";
import express from "express";
import routerPanaderia from "../routes/panaderia.routes.js";

// Creamos una instancia de Express aislada dedicada exclusivamente a testear las rutas
const app = express();
app.use(express.json());
app.use("/api/panaderia", routerPanaderia);

describe("SUITE DE PRUEBAS - API PANADERÍA MODULAR", () => {
    
    // ==========================================
    // PRUEBAS DE LECTURA (GET)
    // ==========================================
    describe("GET /api/panaderia", () => {
        it("Debería retornar el catálogo inicial completo con estado 200", async () => {
            const res = await request(app).get("/api/panaderia");
            
            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);
            expect(Array.isArray(res.body.data)).toBe(true);
            expect(res.body.data.length).toBeGreaterThan(0);
        });

        it("Debería obtener un producto específico si el ID existe", async () => {
            const res = await request(app).get("/api/panaderia/2");
            
            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data.nombre).toBe("Croissant de Queso");
        });

        it("Debería responder 404 si el producto consultado no existe", async () => {
            const res = await request(app).get("/api/panaderia/999");
            
            expect(res.statusCode).toBe(404);
            expect(res.body.success).toBe(false);
            expect(res.body.message).toContain("No se encontró el producto");
        });
    });

    // ==========================================
    // PRUEBAS DE CREACIÓN (POST) & MIDDLEWARE
    // ==========================================
    describe("POST /api/panaderia", () => {
        it("Debería agregar exitosamente un nuevo ítem si el body es correcto", async () => {
            const nuevoPan = {
                nombre: "Pan de Pinllo",
                precio: 0.25,
                categoria: "Sal",
                stock: 90
            };

            const res = await request(app)
                .post("/api/panaderia")
                .send(nuevoPan);

            expect(res.statusCode).toBe(201);
            expect(res.body.success).toBe(true);
            expect(res.body.data).toHaveProperty("id");
            expect(res.body.data.nombre).toBe("Pan de Pinllo");
        });

        it("Debería ser rechazado por el Middleware (400) si faltan parámetros requeridos", async () => {
            const panInvalido = {
                nombre: "Pan Fallido Sin Precio",
                categoria: "Sal"
                // precio y stock faltantes
            };

            const res = await request(app)
                .post("/api/panaderia")
                .send(panInvalido);

            expect(res.statusCode).toBe(400);
            expect(res.body.success).toBe(false);
            expect(res.body.message).toContain("Faltan campos obligatorios");
        });
    });

    // ==========================================
    // PRUEBAS DE ACTUALIZACIÓN (PUT)
    // ==========================================
    describe("PUT /api/panaderia/:id", () => {
        it("Debería modificar parcialmente un campo de forma correcta", async () => {
            const actualizacion = { stock: 150 };

            const res = await request(app)
                .put("/api/panaderia/1")
                .send(actualizacion);

            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data.stock).toBe(150);
            expect(res.body.data.nombre).toBe("Pan de Ambato"); // Conserva sus datos anteriores
        });

        it("Debería retornar 404 si intenta actualizar un ID inexistente", async () => {
            const res = await request(app)
                .put("/api/panaderia/456")
                .send({ stock: 10 });

            expect(res.statusCode).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });

    // ==========================================
    // PRUEBAS DE ELIMINACIÓN (DELETE)
    // ==========================================
    describe("DELETE /api/panaderia/:id", () => {
        it("Debería eliminar un elemento del inventario en memoria", async () => {
            const res = await request(app).delete("/api/panaderia/3");

            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.message).toContain("retirado del inventario");
        });

        it("Debería retornar 404 al intentar borrar un ID que ya no existe", async () => {
            const res = await request(app).delete("/api/panaderia/3"); // Segunda llamada al mismo ID

            expect(res.statusCode).toBe(404);
            expect(res.body.success).toBe(false);
        });
    });
});