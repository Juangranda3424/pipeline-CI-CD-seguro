import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import routerPanaderia from "./routes/panaderia.routes.js";

dotenv.config();

const app = express();

// Middleware para habilitar CORS y parsear JSON en las solicitudes entrantes
app.use(cors());
app.use(express.json());

// Inyección de rutas modulares
app.use("/api/panaderia", routerPanaderia);

// Ruta de prueba para verificar que la API está funcionando correctamente
app.get("/", (req, res) => {
    res.json({ mensaje: "API funcionando" });
});

export default app;