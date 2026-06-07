import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import router from "./routes/usuarios.routes.js";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/usuarios", router);

app.listen(process.env.PORT, () => {
    console.log("Servidor iniciado");
});