import express from "express";
import { ejecutarCodigo, ejecutarCodigoVulnerable, ejecutarCodigoTest } from "../controllers/test.controller.js";

const router = express.Router();

router.post("/ejecutar", ejecutarCodigo);
router.post("/vulnerable", ejecutarCodigoVulnerable);
router.post("/test", ejecutarCodigoTest);
export default router;