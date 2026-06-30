# =========================
# EXAMEN OPTIMIZADO ESO
# DIAGNÓSTICO INICIAL REAL
# =========================

EXAMEN = {
    "2ESO": {

        # =====================
        # COMPRENSIÓN LECTORA
        # =====================
        "comprension": {
            "texto": """El tren de madrugada recorría lentamente la línea hacia la ciudad. La niebla cubría los campos y apenas dejaba ver el paisaje. En cada estación, el convoy se detenía unos segundos y volvía a avanzar.""",

            "preguntas": [
                {
                    "id": "CL1",
                    "enunciado": "Indica el lugar, tiempo y ambiente del texto",
                    "competencia": "comprension",
                    "tipo": "abierta_corta",
                    "keywords": ["tren", "madrugada", "niebla", "campo", "estación", "ciudad", "silencio", "oscuro"],
                    "errores_tipicos": ["confunde tiempo y lugar", "no identifica ambiente", "respuesta incompleta"]
                },

                {
                    "id": "CL2",
                    "enunciado": "Escribe tres acciones que ocurren en el texto",
                    "competencia": "comprension",
                    "tipo": "lista",
                    "keywords": ["recorría", "detenía", "avanzaba", "cubría", "dejaba ver"],
                    "errores_tipicos": ["inventa acciones", "no usa el texto", "menos de 3 acciones"]
                },

                {
                    "id": "CL3",
                    "enunciado": "Resume el texto con tus palabras",
                    "competencia": "comprension",
                    "tipo": "resumen",
                    "keywords": ["tren", "viaje", "noche", "llegada", "viajero", "paisaje"],
                    "errores_tipicos": ["copia literal", "no resume", "omite idea principal"]
                }
            ]
        },

        # =====================
        # MORFOLOGÍA
        # =====================
        "morfologia": [
            {
                "id": "M1",
                "enunciado": "Analiza la palabra 'silencio'",
                "competencia": "morfologia",
                "keywords": ["sustantivo", "común", "abstracto", "lexema", "morfema"],
                "errores_tipicos": ["confunde verbo", "no separa morfemas"]
            },

            {
                "id": "M2",
                "enunciado": "Clasifica: determinante o pronombre",
                "competencia": "morfologia",
                "keywords": ["determinante", "posesivo", "pronombre", "aquellos", "mi"],
                "errores_tipicos": ["confunde función", "no identifica categoría"]
            }
        ],

        # =====================
        # SEMÁNTICA
        # =====================
        "semantica": [
            {
                "id": "S1",
                "enunciado": "Define polisemia y homonimia con ejemplo",
                "competencia": "semantica",
                "keywords": ["polisemia", "homonimia", "significado", "varios", "palabra"],
                "errores_tipicos": ["mezcla conceptos", "no pone ejemplos"]
            },

            {
                "id": "S2",
                "enunciado": "Relaciones semánticas (hiperónimo / campo semántico)",
                "competencia": "semantica",
                "keywords": ["hiperónimo", "campo semántico", "categoría", "conjunto"],
                "errores_tipicos": ["define sin ejemplos", "confunde términos"]
            }
        ],

        # =====================
        # TEXTOS
        # =====================
        "textos": [
            {
                "id": "T1",
                "enunciado": "Identifica tipo de texto (instructivo, expositivo, argumentativo)",
                "competencia": "textos",
                "keywords": ["instructivo", "expositivo", "argumentativo", "informar", "instrucciones"],
                "errores_tipicos": ["confunde tipos", "no justifica"]
            }
        ],

        # =====================
        # LITERATURA
        # =====================
        "literatura": [
            {
                "id": "L1",
                "enunciado": "Analiza rima, verso y una figura literaria",
                "competencia": "literatura",
                "keywords": ["rima", "verso", "sinalefa", "personificación", "metáfora"],
                "errores_tipicos": ["solo identifica sin explicar", "confunde figuras"]
            }
        ],

        # =====================
        # SINTAXIS
        # =====================
        "sintaxis": [
            {
                "id": "SY1",
                "enunciado": "Indica si es frase u oración",
                "competencia": "sintaxis",
                "keywords": ["oración", "verbo", "sujeto", "frase", "sin verbo"],
                "errores_tipicos": ["confunde oración con frase"]
            }
        ]
    }
}
