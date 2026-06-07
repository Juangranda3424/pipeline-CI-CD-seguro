import express from "express";

const router = express.Router();

router.get("/", (req, res) => {
    res.json([
        {
            id: 1,
            nombre: "Juan"
        },
        {
            id: 2,
            nombre: "Pedro"
        }
    ]);
});

export default router;