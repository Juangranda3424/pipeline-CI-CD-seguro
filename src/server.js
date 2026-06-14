import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import router from "./routes/usuarios.routes.js";

dotenv.config();

const app = express();

// Middleware para habilitar CORS y parsear JSON en las solicitudes entrantes
app.use(cors());
app.use(express.json());

// Rutas de la API
app.use("/api/usuarios", router);

// Ruta de prueba para verificar que la API está funcionando correctamente
app.get("/", (req, res) => {
    res.json({ mensaje: "API funcionando" });
});

export default app;