import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import router from "./routes/usuarios.routes.js";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/usuarios", router);

// Ruta de prueba para verificar que la API está funcionando
app.get("/", (req, res) => {
    res.json({ mensaje: "API funcionando" });
});

export default app;