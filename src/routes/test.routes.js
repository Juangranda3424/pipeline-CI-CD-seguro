import express from "express";
import { ejecutarCodigo } from "../controllers/test.controller.js";

const router = express.Router();

router.post("/ejecutar", ejecutarCodigo);

export default router;