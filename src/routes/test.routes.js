import express from "express";
import { ejecutarCodigo, ejecutarCodigoVulnerable } from "../controllers/test.controller.js";

const router = express.Router();

router.post("/ejecutar", ejecutarCodigo);
router.post("/vulnerable", ejecutarCodigoVulnerable);

export default router;