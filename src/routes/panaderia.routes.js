import express from "express";
import { 
    obtenerTodoslosPanes, 
    obtenerPanPorId, 
    crearPan, 
    actualizarPan, 
    eliminarPan 
} from "../controllers/panaderia.controller.js";
import { validarPanInput } from "../middlewares/validarPan.middleware.js";

const router = express.Router();

router.get("/", obtenerTodoslosPanes);
router.get("/:id", obtenerPanPorId);

// Rutas protegidas por el Middleware de validación
router.post("/", validarPanInput, crearPan);
router.put("/:id", validarPanInput, actualizarPan);

router.delete("/:id", eliminarPan);

export default router;