EXAMEN = {
    "2ESO": {

        # =====================================================
        # 1. COMPRENSIÓN LECTORA - 2 PUNTOS
        # =====================================================

        "comprension": {

            "texto": """El tren de madrugada recorría lentamente la línea hacia la ciudad. La niebla cubría los campos y apenas dejaba ver el paisaje. En cada estación, el convoy se detenía unos segundos y volvía a avanzar con un chirrido metálico.

En uno de los vagones, un hombre joven miraba por la ventana sin hablar. Sujetaba una mochila y parecía cansado. A su lado, una anciana dormía profundamente. El silencio dentro del vagón era extraño, como si todos evitaran mirarse.

Cuando el tren llegó a la estación final, la luz del amanecer comenzó a aparecer entre los edificios. El viajero bajó lentamente, respiró hondo y caminó sin prisa hacia la salida.""",

            "preguntas": [

                {
                    "id": "c1",
                    "enunciado": "1.1. Indica el lugar del texto.",
                    "tipo": "texto",
                    "puntos": 0.20
                },

                {
                    "id": "c2",
                    "enunciado": "1.1. Indica el tiempo del texto.",
                    "tipo": "texto",
                    "puntos": 0.15
                },

                {
                    "id": "c3",
                    "enunciado": "1.1. Indica el ambiente del texto.",
                    "tipo": "texto",
                    "puntos": 0.15
                },

                {
                    "id": "c4",
                    "enunciado": "1.2. Escribe tres acciones que ocurren en el texto.",
                    "tipo": "texto",
                    "puntos": 0.50
                },

                {
                    "id": "c5",
                    "enunciado": "1.3. Resume el texto con tus palabras.",
                    "tipo": "texto_largo",
                    "puntos": 1.00
                }
            ]
        },


        # =====================================================
        # 2. MORFOLOGÍA - 2,5 PUNTOS
        # =====================================================

        "morfologia": [

            {
                "id": "m1",
                "palabra": "silencio",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Tipo de estructura",
                    "Categoría gramatical completa",
                    "V/I"
                ]
            },

            {
                "id": "m2",
                "palabra": "lentamente",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Tipo de estructura",
                    "Categoría gramatical completa",
                    "V/I"
                ]
            },

            {
                "id": "m3",
                "palabra": "desconocido",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Tipo de estructura",
                    "Categoría gramatical completa",
                    "V/I"
                ]
            },

            {
                "id": "m4",
                "palabra": "mochilas",
                "puntos": 0.50,
                "campos": [
                    "Lexema",
                    "Morfemas",
                    "Tipo de estructura",
                    "Categoría gramatical completa",
                    "V/I"
                ]
            }
        ],

        "determinantes_pronombres": [

            {
                "id": "m5",
                "texto": "Aquellos estudiantes llegaron tarde.",
                "respuesta": "determinante",
                "puntos": 0.17
            },

            {
                "id": "m6",
                "texto": "Mi cuaderno está en la mesa.",
                "respuesta": "determinante",
                "puntos": 0.17
            },

            {
                "id": "m7",
                "texto": "Nadie respondió a la pregunta.",
                "respuesta": "pronombre",
                "puntos": 0.16
            }
        ],


        # =====================================================
        # 3. SEMÁNTICA - 1,5 PUNTOS
        # =====================================================

        "semantica": [

            {
                "id": "s1",
                "texto": "Frío / calor",
                "respuesta": "Antonimia",
                "puntos": 0.10
            },

            {
                "id": "s2",
                "texto": "Perro, gato, caballo",
                "respuesta": "Campo semántico",
                "puntos": 0.10
            },

            {
                "id": "s3",
                "texto": "Hoja (árbol / papel)",
                "respuesta": "Polisemia",
                "puntos": 0.10
            },

            {
                "id": "s4",
                "texto": "Rueda y volante respecto a coche",
                "respuesta": "Meronimia",
                "puntos": 0.10
            },

            {
                "id": "s5",
                "texto": "León, tigre, pantera",
                "respuesta": "Hipónimos",
                "puntos": 0.10
            }
        ],


        # =====================================================
        # 4. TEXTOS - 1 PUNTO
        # =====================================================

        "textos": {

            "texto_a":
                "Apaga el horno y deja reposar la masa durante diez minutos antes de usarla.",

            "texto_b":
                "Los mamíferos son animales vertebrados que alimentan a sus crías con leche.",

            "texto_c":
                "Reciclar ayuda a reducir la contaminación y cuidar el medio ambiente.",

            "preguntas": [

                {
                    "id": "t1",
                    "texto": "Texto A",
                    "respuesta": "Instructivo",
                    "puntos": 0.25
                },

                {
                    "id": "t2",
                    "texto": "Texto B",
                    "respuesta": "Expositivo",
                    "puntos": 0.25
                },

                {
                    "id": "t3",
                    "texto": "Texto C",
                    "respuesta": "Argumentativo",
                    "puntos": 0.25
                },

                {
                    "id": "t4",
                    "texto": "Explica la finalidad de UNO de los textos.",
                    "puntos": 0.25
                }
            ]
        },


        # =====================================================
        # 5. LITERATURA - 2 PUNTOS
        # =====================================================

        "literatura": {

            "poema": [
                "La lluvia cae suave en la ciudad,",
                "las calles brillan bajo la farola,",
                "y el viento juega solo en la escuela",
                "como si todo fuera soledad."
            ],

            "preguntas": [

                {
                    "id": "l1",
                    "enunciado": "Número de versos",
                    "respuesta": "4",
                    "puntos": 0.25
                },

                {
                    "id": "l2",
                    "enunciado": "Arte mayor o menor",
                    "respuesta": "Arte menor",
                    "puntos": 0.25
                },

                {
                    "id": "l3",
                    "enunciado": "Esquema métrico",
                    "respuesta": "8a 8b 8b 8a",
                    "puntos": 0.40
                },

                {
                    "id": "l4",
                    "enunciado": "Tipo de rima",
                    "respuesta": "Consonante",
                    "puntos": 0.30
                },

                {
                    "id": "l5",
                    "enunciado": "Escribe una sinalefa y explícala.",
                    "puntos": 0.40
                },

                {
                    "id": "l6",
                    "enunciado": "Indica una personificación y explícala.",
                    "puntos": 0.40
                }
            ]
        },


        # =====================================================
        # 6. SINTAXIS - 1 PUNTO
        # =====================================================

        "sintaxis": [

            {
                "id": "x1",
                "frase": "Buenas tardes.",
                "tipo": "Frase u oración",
                "respuesta": "Frase"
            },

            {
                "id": "x2",
                "frase": "Llueve mucho hoy.",
                "tipo": "Frase u oración",
                "respuesta": "Oración"
            },

            {
                "id": "x3",
                "frase": "¡Qué alegría!",
                "tipo": "Frase u oración",
                "respuesta": "Frase"
            },

            {
                "id": "x4",
                "frase": "No hablar en clase.",
                "tipo": "Frase u oración",
                "respuesta": "Frase"
            },

            {
                "id": "x5",
                "frase": "El perro ladra.",
                "tipo": "Frase u oración",
                "respuesta": "Oración"
            },

            {
                "id": "x6",
                "frase": "¿Vienes conmigo?",
                "tipo": "Modalidad oracional",
                "respuesta": "Interrogativa"
            },

            {
                "id": "x7",
                "frase": "Ojalá apruebe el examen.",
                "tipo": "Modalidad oracional",
                "respuesta": "Desiderativa"
            },

            {
                "id": "x8",
                "frase": "¡Qué frío hace!",
                "tipo": "Modalidad oracional",
                "respuesta": "Exclamativa"
            },

            {
                "id": "x9",
                "frase": "Mañana iremos al cine.",
                "tipo": "Modalidad oracional",
                "respuesta": "Enunciativa"
            },

            {
                "id": "x10",
                "frase": "Cierra la puerta.",
                "tipo": "Modalidad oracional",
                "respuesta": "Imperativa"
            }
        ],


        # =====================================================
        # 7. DIÁLOGO - 0,5 PUNTOS
        # =====================================================

        "dialogo": {

            "texto": [
                "Lucía: ¿Has terminado el resumen de Lengua?",
                "Carlos: Sí, lo hice ayer por la tarde.",
                "Lucía: Yo todavía estoy con la conclusión.",
                "Carlos: Si quieres, lo revisamos juntos después de clase.",
                "Lucía: Vale, quedamos en la biblioteca.",
                "Carlos: Perfecto, allí estaremos más tranquilos."
            ],

            "preguntas": [

                {
                    "id": "d1",
                    "enunciado": "7.1. Indica los interlocutores.",
                    "respuesta": "Lucía y Carlos",
                    "puntos": 0.10
                },

                {
                    "id": "d2",
                    "enunciado": "7.2. Indica el número de intervenciones.",
                    "respuesta": "6",
                    "puntos": 0.10
                },

                {
                    "id": "d3",
                    "enunciado": "7.3. Pasa a estilo indirecto: Carlos: «Sí, lo hice ayer por la tarde».",
                    "puntos": 0.30
                }
            ]
        }
    }
}
