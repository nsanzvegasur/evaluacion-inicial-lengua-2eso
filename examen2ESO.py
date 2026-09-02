EXAMEN = {
    "2ESO": {

        # ==========================================================
        # 1. COMPRENSIÓN LECTORA
        # ==========================================================
        "comprension": {
            "texto": """El tren de madrugada recorría lentamente la línea hacia la ciudad. La niebla cubría los campos y apenas dejaba ver el paisaje. En cada estación, el convoy se detenía unos segundos y volvía a avanzar con un chirrido metálico.

En uno de los vagones, un hombre joven miraba por la ventana sin hablar. Sujetaba una mochila y parecía cansado. A su lado, una anciana dormía profundamente. El silencio dentro del vagón era extraño, como si todos evitaran mirarse.

Cuando el tren llegó a la estación final, la luz del amanecer comenzó a aparecer entre los edificios. El viajero bajó lentamente, respiró hondo y caminó sin prisa hacia la salida.""",

            "preguntas": [
                {
                    "id": "c1_lugar",
                    "enunciado": "1.1. Lugar",
                    "ayuda": "Indica dónde ocurre la historia.",
                    "tipo": "texto",
                    "puntos": 0.30,
                    "criterios": [
                        "tren",
                        "vagón",
                        "vagones",
                        "estación",
                        "estaciones",
                        "ciudad"
                    ]
                },
                {
                    "id": "c1_personajes",
                    "enunciado": "1.1. Escribe los dos personajes que aparecen. Sepáralos por comas o escribe uno en cada línea.",
                    "ayuda": "Escribe los dos personajes que aparecen. Sepáralos por comas o escribe uno en cada línea.",
                    "tipo": "lista",
                    "puntos": 0.40,
                    "criterios": [
                        "hombre joven",
                        "anciana"
                    ]
                },
                {
                    "id": "c1_tiempo",
                    "enunciado": "1.1. Tiempo",
                    "ayuda": "Indica cuándo ocurre la historia.",
                    "tipo": "texto",
                    "puntos": 0.30,
                    "criterios": [
                        "madrugada",
                        "amanecer"
                    ]
                },
                {
                    "id": "c2_accion1",
                    "enunciado": "1.2. Acción 1",
                    "ayuda": "Localiza una acción que ocurra en el texto y escríbela en infinitivo.",
                    "tipo": "accion",
                    "puntos": 0.50,
                    "criterios": [
                        "recorrer",
                        "detenerse",
                        "avanzar",
                        "mirar",
                        "sujetar",
                        "dormir",
                        "llegar",
                        "bajar",
                        "respirar",
                        "caminar"
                    ]
                },
                {
                    "id": "c2_accion2",
                    "enunciado": "1.2. Acción 2",
                    "ayuda": "Localiza una acción que ocurra en el texto y escríbela en infinitivo.",
                    "tipo": "accion",
                    "puntos": 0.50,
                    "criterios": [
                        "recorrer",
                        "detenerse",
                        "avanzar",
                        "mirar",
                        "sujetar",
                        "dormir",
                        "llegar",
                        "bajar",
                        "respirar",
                        "caminar"
                    ]
                },
                {
                    "id": "c2_accion3",
                    "enunciado": "1.2. Acción 3",
                    "ayuda": "Localiza una acción que ocurra en el texto y escríbela en infinitivo.",
                    "tipo": "accion",
                    "puntos": 0.50,
                    "criterios": [
                        "recorrer",
                        "detenerse",
                        "avanzar",
                        "mirar",
                        "sujetar",
                        "dormir",
                        "llegar",
                        "bajar",
                        "respirar",
                        "caminar"
                    ]
                }
            ]
        },

        # ==========================================================
        # 2. MORFOLOGÍA
        # ==========================================================
        "morfologia": [
            {
                "id": "m1",
                "palabra": "silencio",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Estructura de la palabra",
                    "Categoría gramatical completa",
                    "V / I"
                ],
                "respuestas": {
                    "Lexema": ["silenci"],
                    "Morfemas": ["o"],
                    "Estructura de la palabra": ["simple"],
                    "Categoría gramatical completa": [
                        "sustantivo",
                        "común",
                        "abstracto",
                        "masculino",
                        "singular"
                    ],
                    "V / I": ["variable"]
                }
            },
            {
                "id": "m2",
                "palabra": "lentamente",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Estructura de la palabra",
                    "Categoría gramatical completa",
                    "V / I"
                ],
                "respuestas": {
                    "Lexema": ["lent"],
                    "Morfemas": ["a", "mente"],
                    "Estructura de la palabra": ["derivada"],
                    "Categoría gramatical completa": [
                        "adverbio",
                        "modo"
                    ],
                    "V / I": ["invariable"]
                }
            },
            {
                "id": "m3",
                "palabra": "desconocido",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Estructura de la palabra",
                    "Categoría gramatical completa",
                    "V / I"
                ],
                "respuestas": {
                    "Lexema": ["conoc"],
                    "Morfemas": ["des", "id", "o"],
                    "Estructura de la palabra": ["derivada"],
                    "Categoría gramatical completa": [
                        "adjetivo",
                        "calificativo",
                        "masculino",
                        "singular"
                    ],
                    "V / I": ["variable"]
                }
            },
            {
                "id": "m4",
                "palabra": "mochilas",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Estructura de la palabra",
                    "Categoría gramatical completa",
                    "V / I"
                ],
                "respuestas": {
                    "Lexema": ["mochil"],
                    "Morfemas": ["a", "s"],
                    "Estructura de la palabra": ["simple"],
                    "Categoría gramatical completa": [
                        "sustantivo",
                        "común",
                        "concreto",
                        "femenino",
                        "plural"
                    ],
                    "V / I": ["variable"]
                }
            }
        ],

        # ==========================================================
        # 3. DETERMINANTES Y PRONOMBRES
        # ==========================================================
        "determinantes_pronombres": [
            {
                "id": "dp1",
                "frase": "Aquellos estudiantes llegaron tarde.",
                "palabra": "Aquellos",
                "enunciado": "Indica si «Aquellos» es DETERMINANTE o PRONOMBRE.",
                "respuesta": "determinante",
                "puntos": 0.1667
            },
            {
                "id": "dp2",
                "frase": "Mi cuaderno está en la mesa.",
                "palabra": "Mi",
                "enunciado": "Indica si «Mi» es DETERMINANTE o PRONOMBRE.",
                "respuesta": "determinante",
                "puntos": 0.1667
            },
            {
                "id": "dp3",
                "frase": "Nadie respondió a la pregunta.",
                "palabra": "Nadie",
                "enunciado": "Indica si «Nadie» es DETERMINANTE o PRONOMBRE.",
                "respuesta": "pronombre",
                "puntos": 0.1666
            }
        ],

        # ==========================================================
        # 4. SEMÁNTICA
        # ==========================================================
        "semantica": [
            {
                "id": "s1",
                "elemento": "Frío / calor",
                "enunciado": "Indica la relación semántica:",
                "respuesta": "antonimia",
                "puntos": 0.10
            },
            {
                "id": "s2",
                "elemento": "Perro, gato, caballo",
                "enunciado": "Indica la relación semántica:",
                "respuesta": "campo semántico",
                "puntos": 0.10
            },
            {
                "id": "s3",
                "elemento": "Hoja (árbol / papel)",
                "enunciado": "Indica la relación semántica:",
                "respuesta": "polisemia",
                "puntos": 0.10
            },
            {
                "id": "s4",
                "elemento": "Rueda y volante respecto a coche",
                "enunciado": "Indica la relación semántica:",
                "respuesta": "meronimia",
                "puntos": 0.10
            },
            {
                "id": "s5",
                "elemento": "León, tigre, pantera",
                "enunciado": "Indica la relación semántica:",
                "respuesta": "hipónimos",
                "puntos": 0.10
            }
        ],

        # ==========================================================
        # 5. TIPOLOGÍA TEXTUAL
        # ==========================================================
        "textos": [
            {
                "id": "t1",
                "texto": "Texto A: «Apaga el horno y deja reposar la masa durante diez minutos antes de usarla.»",
                "enunciado": "4.1. Texto A → Tipo de texto",
                "respuesta": "instructivo",
                "puntos": 0.25
            },
            {
                "id": "t2",
                "texto": "Texto B: «Los mamíferos son animales vertebrados que alimentan a sus crías con leche.»",
                "enunciado": "4.1. Texto B → Tipo de texto",
                "respuesta": "expositivo",
                "puntos": 0.25
            },
            {
                "id": "t3",
                "texto": "Texto C: «Reciclar ayuda a reducir la contaminación y cuidar el medio ambiente.»",
                "enunciado": "4.1. Texto C → Tipo de texto",
                "respuesta": "argumentativo",
                "puntos": 0.25
            }
        ],

        # ==========================================================
        # 6. LITERATURA
        # ==========================================================
        "literatura": [
            {
                "id": "l0",
                "tipo": "poema",
                "enunciado": "Lee el siguiente poema:",
                "versos": [
                    "La lluvia cae suave en la ciudad,",
                    "las calles brillan bajo la farola,",
                    "y el viento juega solo en la escuela",
                    "como si todo fuera soledad."
                ]
            },
            {
                "id": "l1",
                "enunciado": "5.1. Número de versos",
                "respuesta": "4",
                "puntos": 0.25
            },
            {
                "id": "l2",
                "enunciado": "5.2. ¿Es de arte mayor o de arte menor?",
                "respuesta": "arte mayor",
                "puntos": 0.25
            },
            {
                "id": "l3",
                "enunciado": "5.3. Esquema métrico",
                "respuesta": "14A 14B 14B 14A",
                "alternativas": [
                    "14A 14B 14B 14A",
                    "14A, 14B, 14B, 14A",
                    "14A/14B/14B/14A"
                ],
                "puntos": 0.35
            },
            {
                "id": "l4",
                "enunciado": "5.4. Tipo de rima",
                "respuesta": "consonante",
                "puntos": 0.25
            },
            {
                "id": "l5",
                "enunciado": "5.5. Localiza una sinalefa del poema y escribe las dos palabras exactas que la forman.",
                "ayuda": "Escribe únicamente las dos palabras que forman la sinalefa. No tienes que explicar nada.",
                "tipo": "sinalefa",
                "respuestas_validas": [
                    "suave en",
                    "y el",
                    "solo en",
                    "la escuela"
                ],
                "puntos": 0.45
            },
            {
                "id": "l6",
                "enunciado": "5.6. Localiza una personificación del poema y escribe las palabras exactas que la forman.",
                "ayuda": "Escribe únicamente las palabras que forman la personificación. No tienes que explicar nada.",
                "tipo": "personificacion",
                "respuestas_validas": [
                    "el viento juega",
                    "viento juega"
                ],
                "puntos": 0.45
            }
        ],

        # ==========================================================
        # 7. SINTAXIS
        # ==========================================================
        "sintaxis": [
            {
                "id": "x1",
                "frase": "Buenas tardes.",
                "enunciado": "Indica si es FRASE u ORACIÓN:",
                "respuesta": "frase",
                "puntos": 0.10
            },
            {
                "id": "x2",
                "frase": "Llueve mucho hoy.",
                "enunciado": "Indica si es FRASE u ORACIÓN:",
                "respuesta": "oración",
                "puntos": 0.10
            },
            {
                "id": "x3",
                "frase": "¡Qué alegría!",
                "enunciado": "Indica si es FRASE u ORACIÓN:",
                "respuesta": "frase",
                "puntos": 0.10
            },
            {
                "id": "x4",
                "frase": "No hablar en clase.",
                "enunciado": "Indica si es FRASE u ORACIÓN:",
                "respuesta": "oración",
                "puntos": 0.10
            },
            {
                "id": "x5",
                "frase": "El perro ladra.",
                "enunciado": "Indica si es FRASE u ORACIÓN:",
                "respuesta": "oración",
                "puntos": 0.10
            },
            {
                "id": "x6",
                "frase": "¿Vienes conmigo?",
                "enunciado": "Indica la MODALIDAD ORACIONAL:",
                "respuesta": "interrogativa",
                "puntos": 0.10
            },
            {
                "id": "x7",
                "frase": "Ojalá apruebe el examen.",
                "enunciado": "Indica la MODALIDAD ORACIONAL:",
                "respuesta": "desiderativa",
                "puntos": 0.10
            },
            {
                "id": "x8",
                "frase": "¡Qué frío hace!",
                "enunciado": "Indica la MODALIDAD ORACIONAL:",
                "respuesta": "exclamativa",
                "puntos": 0.10
            },
            {
                "id": "x9",
                "frase": "Mañana iremos al cine.",
                "enunciado": "Indica la MODALIDAD ORACIONAL:",
                "respuesta": "enunciativa",
                "puntos": 0.10
            },
            {
                "id": "x10",
                "frase": "Cierra la puerta.",
                "enunciado": "Indica la MODALIDAD ORACIONAL:",
                "respuesta": "exhortativa",
                "puntos": 0.10
            }
        ],

        # ==========================================================
        # 8. DIÁLOGO
        # ==========================================================
        "dialogo": {
            "texto": """Lucía: ¿Has terminado el resumen de Lengua?
Carlos: Sí, lo hice ayer por la tarde.
Lucía: Yo todavía estoy con la conclusión.
Carlos: Si quieres, lo revisamos juntos después de clase.
Lucía: Vale, quedamos en la biblioteca.
Carlos: Perfecto, allí estaremos más tranquilos.""",

            "preguntas": [
                {
                    "id": "d1",
                    "enunciado": "7.1. ¿Quiénes son los interlocutores?Sepáralos por comas ",
                    "ayuda": "Escribe los dos nombres. Sepáralos por comas o escribe uno en cada línea.",
                    "respuesta": "Lucía y Carlos",
                    "tipo": "lista",
                    "criterios": [
                        "lucía",
                        "carlos"
                    ],
                    "puntos": 0.15
                },
                {
                    "id": "d2",
                    "enunciado": "7.2. ¿Cuál es el número de intervenciones?",
                    "respuesta": "6",
                    "puntos": 0.15
                },
                {
                    "id": "d3",
                    "enunciado": "7.3. Pasa a estilo indirecto la intervención de Carlos: «Sí, lo hice ayer por la tarde.»",
                    "tipo": "estilo_indirecto",
                    "puntos": 0.45
                }
            ]
        }
    }
}
