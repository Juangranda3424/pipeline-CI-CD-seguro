import express from "express";
import { ejecutarCodigo, ejecutarCodigoVulnerable, ejecutarCodigoTest, ejecutarCodigoTest2 } from "../controllers/test.controller.js";

const router = express.Router();

router.post("/ejecutar", ejecutarCodigo);
router.post("/vulnerable", ejecutarCodigoVulnerable);
router.post("/test", ejecutarCodigoTest);
router.post("/test2", ejecutarCodigoTest2);
export default router;