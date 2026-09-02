```python
import streamlit as st
import pandas as pd
from datetime import datetime
import re

from analytics import radar_chart, comparativa, generar_perfil
from pdf_report import generar_pdf
from examen2ESO import EXAMEN


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2º ESO",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Evaluación Inicial — Lengua Castellana y Literatura")
st.caption("2.º ESO")


# ============================================================
# CARGAR RESULTADOS
# ============================================================

COLUMNAS = [
    "name",
    "group",
    "date",
    "comprension",
    "morfologia",
    "semantica",
    "textos",
    "literatura",
    "sintaxis",
    "dialogo",
    "ortografia",
    "tildes",
    "descuento_ortografia",
    "nota_inicial",
    "nota_final",
    "total"
]

try:
    df = pd.read_csv("results.csv")
except Exception:
    df = pd.DataFrame(columns=COLUMNAS)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def contar_faltas_ortografia(texto):
    """
    Detección sencilla automática de faltas ortográficas.

    IMPORTANTE:
    No pretende sustituir un corrector lingüístico profesional.
    Cuenta errores muy claros mediante reglas básicas.
    """

    if not texto:
        return 0

    errores = 0

    palabras = re.findall(r"\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+\b", texto)

    # Errores muy habituales que podemos detectar mediante reglas.
    reglas = {
        "aver": "haber",
        "haver": "haber",
        "havía": "había",
        "avia": "había",
        "havia": "había",
        "habian": "habían",
        "tambien": "también",
        "mas": "más",
        "despues": "después",
        "porque": "porque",
        "hay": "hay",
        "valla": "vaya",
        "echo": "hecho",
        "hechar": "echar",
        "llendo": "yendo",
        "alluda": "ayuda",
        "haci": "así",
        "asi": "así",
        "ocurrio": "ocurrió",
        "ocurren": "ocurren",
        "estava": "estaba",
        "estava": "estaba",
        "tubo": "tuvo",
        "tubieron": "tuvieron",
        "andava": "andaba",
        "andavan": "andaban",
        "iva": "iba",
        "iban": "iban",
        "vien": "bien",
        "vienes": "vienes",
        "hombre": "hombre",
        "escribir": "escribir"
    }

    for palabra in palabras:
        p = palabra.lower()

        if p in reglas and reglas[p] != p:
            errores += 1

    return errores


def contar_faltas_tilde(texto):
    """
    Detección automática básica de palabras frecuentes
    que deberían llevar tilde.
    """

    if not texto:
        return 0

    palabras = re.findall(r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b", texto)

    palabras_sin_tilde = {
        "tambien",
        "despues",
        "ademas",
        "tambien",
        "rapidamente",
        "facilmente",
        "numero",
        "numero",
        "accion",
        "acciones",
        "comprension",
        "morfologia",
        "semantica",
        "literatura",
        "sintaxis",
        "dialogo",
        "oracion",
        "intervencion",
        "intervenciones",
        "personajes",
        "dia",
        "dias",
        "esta",
        "estan",
        "solo",
        "aun",
        "mas"
    }

    errores = 0

    for palabra in palabras:
        if palabra.lower() in palabras_sin_tilde:
            errores += 1

    return errores


def recopilar_textos(respuestas):
    """
    Convierte todas las respuestas en un único texto
    para realizar el análisis automático de ortografía.
    """

    textos = []

    if isinstance(respuestas, dict):

        for valor in respuestas.values():

            if isinstance(valor, dict):
                textos.extend(recopilar_textos(valor))

            elif isinstance(valor, str):
                textos.append(valor)

    elif isinstance(respuestas, str):
        textos.append(respuestas)

    return " ".join(textos)


def puntuar_respuestas(respuestas, maximo):
    """
    Puntuación proporcional básica.

    Se utiliza mientras no haya un sistema de corrección
    semántica avanzada.
    """

    texto = recopilar_textos(respuestas)

    if not texto.strip():
        return 0.0

    palabras = len(texto.split())

    # No da más del máximo.
    puntuacion = min(maximo, palabras / 8)

    return round(puntuacion, 2)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "🧑‍🎓 Examen",
    "📊 Dashboard",
    "👤 Alumno"
])


# ============================================================
# VARIABLES
# ============================================================

q_comp = {}
q_morf = {}
q_sem = {}
q_textos = {}
q_lit = {}
q_syn = {}
q_dialogo = {}


# ============================================================
# EXAMEN
# ============================================================

with tab1:

    st.header("📝 Evaluación inicial")

    # --------------------------------------------------------
    # DATOS DEL ALUMNO
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Nombre y apellidos",
            key="nombre_alumno"
        )

    with col2:
        group = st.text_input(
            "Grupo",
            key="grupo_alumno"
        )


    st.divider()


    # ========================================================
    # 1. COMPRENSIÓN LECTORA
    # ========================================================

    st.header("1. COMPRENSIÓN LECTORA")

    texto_comp = EXAMEN["2ESO"]["comprension"]["texto"]

    st.markdown("### Lee el siguiente texto")

    st.markdown(
        f"""
        <div style="
            background-color:#f5f5f5;
            padding:20px;
            border-radius:10px;
            line-height:1.8;
            font-size:17px;
        ">
        {texto_comp}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 1.1. Indica el lugar, los personajes y el tiempo del texto")

    q_comp["c1_lugar"] = st.text_input(
        "Lugar",
        key="comp_c1_lugar"
    )

    q_comp["c1_personajes"] = st.text_input(
        "Personajes",
        key="comp_c1_personajes"
    )

    q_comp["c1_tiempo"] = st.text_input(
        "Tiempo",
        key="comp_c1_tiempo"
    )


    st.markdown(
        "**1.2. Localiza tres acciones que ocurren en el texto y escríbelas en infinitivo**"
    )

    q_comp["c2_accion1"] = st.text_input(
        "Primera acción",
        key="comp_c2_accion1"
    )

    q_comp["c2_accion2"] = st.text_input(
        "Segunda acción",
        key="comp_c2_accion2"
    )

    q_comp["c2_accion3"] = st.text_input(
        "Tercera acción",
        key="comp_c2_accion3"
    )


    st.markdown("### 1.3. Resume el texto con tus palabras")

    q_comp["c3_resumen"] = st.text_area(
        "Resumen",
        height=150,
        key="comp_c3_resumen"
    )


    # ========================================================
    # 2. MORFOLOGÍA
    # ========================================================

    st.divider()

    st.header("2. MORFOLOGÍA Y CATEGORÍAS GRAMATICALES")

    st.markdown(
        "**Analiza cada palabra completando todas las casillas.**"
    )

    for palabra_data in EXAMEN["2ESO"]["morfologia"]:

        palabra = palabra_data["palabra"]
        pid = palabra_data["id"]

        st.markdown(f"### 🔹 {palabra}")

        respuestas = {}

        campos = palabra_data.get(
            "campos",
            [
                "Lexema",
                "Morfemas",
                "Tipo de estructura",
                "Categoría gramatical completa",
                "V / I"
            ]
        )

        # Dos columnas para que la tabla sea cómoda en pantalla.
        col1, col2 = st.columns(2)

        for i, campo in enumerate(campos):

            if i % 2 == 0:
                with col1:
                    respuestas[campo] = st.text_input(
                        campo,
                        key=f"morf_{pid}_{i}"
                    )
            else:
                with col2:
                    respuestas[campo] = st.text_input(
                        campo,
                        key=f"morf_{pid}_{i}"
                    )

        q_morf[pid] = respuestas


    # ========================================================
    # 2.2 DETERMINANTES Y PRONOMBRES
    # ========================================================

    st.markdown("### 2.2. Determinantes y pronombres")

    st.write(
        "Indica si la palabra destacada funciona como determinante o pronombre."
    )

    q_morf["det1"] = st.text_input(
        "a) Aquellos estudiantes llegaron tarde. → Aquellos",
        key="det1"
    )

    q_morf["det2"] = st.text_input(
        "b) Mi cuaderno está en la mesa. → Mi",
        key="det2"
    )

    q_morf["det3"] = st.text_input(
        "c) Nadie respondió a la pregunta. → Nadie",
        key="det3"
    )


    # ========================================================
    # 3. SEMÁNTICA
    # ========================================================

    st.divider()

    st.header("3. SEMÁNTICA")

    st.write(
        "Indica únicamente el nombre de la relación semántica."
    )

    opciones_semantica = [
        "Antonimia",
        "Campo semántico",
        "Polisemia",
        "Meronimia",
        "Hipónimos"
    ]

    for pregunta in EXAMEN["2ESO"]["semantica"]:

        pid = pregunta["id"]

        st.markdown(
            f"**{pregunta['elemento']}**"
        )

        q_sem[pid] = st.selectbox(
            "Relación semántica",
            ["Selecciona una opción"] + opciones_semantica,
            key=f"sem_{pid}"
        )


    # ========================================================
    # 4. TEXTOS
    # ========================================================

    st.divider()

    st.header("4. TEXTOS")

    textos_examen = EXAMEN["2ESO"]["textos"]

    for pregunta in textos_examen:

        pid = pregunta["id"]

        if "texto" in pregunta:

            st.markdown(
                f"**{pregunta['texto']}**"
            )

            if pid in ["t1", "t2", "t3"]:

                q_textos[pid] = st.selectbox(
                    pregunta["enunciado"],
                    [
                        "Selecciona una opción",
                        "Narrativo",
                        "Descriptivo",
                        "Expositivo",
                        "Instructivo",
                        "Argumentativo",
                        "Dialogado"
                    ],
                    key=f"texto_{pid}"
                )

        else:

            q_textos[pid] = st.text_area(
                pregunta["enunciado"],
                key=f"texto_{pid}"
            )


    # ========================================================
    # 5. LITERATURA
    # ========================================================

    st.divider()

    st.header("5. LITERATURA")

    literatura = EXAMEN["2ESO"]["literatura"]

    poema = None

    for pregunta in literatura:

        if pregunta.get("tipo") == "poema":

            poema = pregunta

    if poema:

        st.markdown("### Lee el siguiente poema:")

        # Cada verso aparece en una fila independiente.
        for verso in poema["versos"]:
            st.markdown(
                f"""
                <div style="
                    padding:8px 12px;
                    margin:2px 0;
                    background-color:#f5f5f5;
                    border-radius:5px;
                    font-size:17px;
                    font-style:italic;
                ">
                {verso}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### Responde")

    for pregunta in literatura:

        pid = pregunta["id"]

        if pid == "l0":
            continue

        q_lit[pid] = st.text_input(
            pregunta["enunciado"],
            key=f"lit_{pid}"
        )


    # ========================================================
    # 6. SINTAXIS
    # ========================================================

    st.divider()

    st.header("6. SINTAXIS")

    st.markdown("### 6.1. Frase u oración")

    for pregunta in EXAMEN["2ESO"]["sintaxis"]:

        pid = pregunta["id"]

        if pid in ["x1", "x2", "x3", "x4", "x5"]:

            st.markdown(
                f"**{pregunta['frase']}**"
            )

            q_syn[pid] = st.selectbox(
                pregunta["enunciado"],
                [
                    "Selecciona una opción",
                    "Frase",
                    "Oración"
                ],
                key=f"syn_{pid}"
            )


    st.markdown("### 6.2. Modalidad oracional")

    modalidades = [
        "Enunciativa",
        "Interrogativa",
        "Exclamativa",
        "Desiderativa",
        "Imperativa / exhortativa",
        "Dubitativa"
    ]

    for pregunta in EXAMEN["2ESO"]["sintaxis"]:

        pid = pregunta["id"]

        if pid in ["x6", "x7", "x8", "x9", "x10"]:

            st.markdown(
                f"**{pregunta['frase']}**"
            )

            q_syn[pid] = st.selectbox(
                pregunta["enunciado"],
                ["Selecciona una opción"] + modalidades,
                key=f"syn_{pid}"
            )


    # ========================================================
    # 7. DIÁLOGO
    # ========================================================

    st.divider()

    st.header("7. DIÁLOGO")

    dialogo = EXAMEN["2ESO"]["dialogo"]

    st.markdown("### Lee el diálogo")

    st.markdown(
        f"""
        <div style="
            background-color:#f5f5f5;
            padding:20px;
            border-radius:10px;
            line-height:1.8;
        ">
        {dialogo["texto"].replace(chr(10), "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    for pregunta in dialogo["preguntas"]:

        pid = pregunta["id"]

        q_dialogo[pid] = st.text_area(
            pregunta["enunciado"],
            key=f"dialogo_{pid}"
        )


    # ========================================================
    # ORTOGRAFÍA
    # ========================================================

    st.divider()

    st.header("✏️ Corrección ortográfica")

    st.info(
        "Las faltas de ortografía y tildes se detectarán automáticamente "
        "a partir de las respuestas escritas. El alumno no puede modificar "
        "estos valores."
    )


    # ========================================================
    # BOTÓN ENVIAR
    # ========================================================

    st.divider()

    if st.button(
        "📤 ENVIAR Y CORREGIR EXAMEN",
        type="primary"
    ):

        if not name.strip() or not group.strip():

            st.error(
                "Debes introducir el nombre y el grupo."
            )

        else:

            # ====================================================
            # RECOGER TODO EL TEXTO DEL EXAMEN
            # ====================================================

            texto_total = " ".join([
                recopilar_textos(q_comp),
                recopilar_textos(q_morf),
                recopilar_textos(q_sem),
                recopilar_textos(q_textos),
                recopilar_textos(q_lit),
                recopilar_textos(q_syn),
                recopilar_textos(q_dialogo)
            ])


            # ====================================================
            # DETECCIÓN AUTOMÁTICA ORTOGRAFÍA
            # ====================================================

            faltas_ortografia = contar_faltas_ortografia(
                texto_total
            )

            faltas_tildes = contar_faltas_tilde(
                texto_total
            )

            descuento_ortografia = min(
                2.0,
                faltas_ortografia * 0.2 +
                faltas_tildes * 0.1
            )


            # ====================================================
            # PUNTUACIONES
            # ====================================================

            # Comprensión: 2 puntos
            comp_texto = recopilar_textos(q_comp)

            if comp_texto.strip():
                comprension = min(
                    10,
                    len(comp_texto.split()) / 10
                )
            else:
                comprension = 0


            # Morfología: 2,5 puntos
            morfologia = puntuar_respuestas(
                q_morf,
                10
            )


            # Semántica: 1,5 puntos
            correctas_sem = 0

            respuestas_correctas_sem = {
                "s1": "Antonimia",
                "s2": "Hipónimos",
                "s3": "Polisemia",
                "s4": "Meronimia",
                "s5": "Campo semántico"
            }

            for pid, correcta in respuestas_correctas_sem.items():

                if q_sem.get(pid) == correcta:
                    correctas_sem += 1

            semantica = round(
                correctas_sem / 5 * 10,
                2
            )


            # Textos: 1 punto
            correctas_textos = 0

            respuestas_correctas_textos = {
                "t1": "Instructivo",
                "t2": "Expositivo",
                "t3": "Argumentativo"
            }

            for pid, correcta in respuestas_correctas_textos.items():

                if q_textos.get(pid) == correcta:
                    correctas_textos += 1

            textos = round(
                correctas_textos / 3 * 10,
                2
            )


            # Literatura: 2 puntos
            literatura_score = puntuar_respuestas(
                q_lit,
                10
            )


            # Sintaxis: 1 punto
            sintaxis_score = 0

            correctas_sintaxis = {
                "x1": "Frase",
                "x2": "Oración",
                "x3": "Frase",
                "x4": "Frase",
                "x5": "Oración",
                "x6": "Interrogativa",
                "x7": "Desiderativa",
                "x8": "Exclamativa",
                "x9": "Enunciativa",
                "x10": "Imperativa / exhortativa"
            }

            for pid, correcta in correctas_sintaxis.items():

                if q_syn.get(pid) == correcta:
                    sintaxis_score += 1

            sintaxis = round(
                sintaxis_score / 10 * 10,
                2
            )


            # Diálogo
            dialogo_score = 0

            if q_dialogo.get("d1", "").strip():
                dialogo_score += 1

            if q_dialogo.get("d2", "").strip():
                dialogo_score += 1

            if q_dialogo.get("d3", "").strip():
                dialogo_score += 1

            dialogo_score = round(
                dialogo_score / 3 * 10,
                2
            )


            # ====================================================
            # NOTA INICIAL
            # ====================================================

            scores = {
                "comprension": comprension,
                "morfologia": morfologia,
                "semantica": semantica,
                "textos": textos,
                "literatura": literatura_score,
                "sintaxis": sintaxis,
                "dialogo": dialogo_score
            }

            nota_inicial = round(
                sum(scores.values()) / len(scores),
                2
            )


            # ====================================================
            # NOTA FINAL
            # ====================================================

            nota_final = max(
                0,
                round(
                    nota_inicial - descuento_ortografia,
                    2
                )
            )


            # ====================================================
            # GUARDAR RESULTADO
            # ====================================================

            row = {
                "name": name,
                "group": group,
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                **scores,
                "ortografia": faltas_ortografia,
                "tildes": faltas_tildes,
                "descuento_ortografia": descuento_ortografia,
                "nota_inicial": nota_inicial,
                "nota_final": nota_final,
                "total": nota_final
            }

            df = pd.concat(
                [df, pd.DataFrame([row])],
                ignore_index=True
            )

            df.to_csv(
                "results.csv",
                index=False
            )


            # ====================================================
            # MOSTRAR RESULTADOS
            # ====================================================

            st.success(
                "✅ Examen corregido y guardado correctamente."
            )

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Nota inicial",
                    f"{nota_inicial:.2f}"
                )

            with col2:
                st.metric(
                    "Descuento",
                    f"-{descuento_ortografia:.2f}"
                )

            with col3:
                st.metric(
                    "Nota final",
                    f"{nota_final:.2f}"
                )


            st.subheader("✏️ Faltas detectadas automáticamente")

            st.write(
                f"Faltas de ortografía: **{faltas_ortografia}**"
            )

            st.write(
                f"Faltas de tilde: **{faltas_tildes}**"
            )

            st.write(
                f"Descuento aplicado: **-{descuento_ortografia:.2f} puntos**"
            )


            # ====================================================
            # RESULTADOS POR COMPETENCIA
            # ====================================================

            st.subheader("📊 Resultados por competencia")

            resultados_df = pd.DataFrame({
                "Competencia": [
                    "Comprensión",
                    "Morfología",
                    "Semántica",
                    "Textos",
                    "Literatura",
                    "Sintaxis",
                    "Diálogo"
                ],
                "Nota": [
                    comprension,
                    morfologia,
                    semantica,
                    textos,
                    literatura_score,
                    sintaxis,
                    dialogo_score
                ]
            })

            st.dataframe(
                resultados_df,
                use_container_width=True,
                hide_index=True
            )


            # ====================================================
            # RADAR
            # ====================================================

            st.subheader("📈 Perfil competencial")

            # analytics.py espera las cinco competencias principales.
            radar_scores = {
                "comprension": comprension,
                "morfologia": morfologia,
                "semantica": semantica,
                "literatura": literatura_score,
                "sintaxis": sintaxis
            }

            st.plotly_chart(
                radar_chart(
                    radar_scores,
                    name
                ),
                use_container_width=True
            )


            # ====================================================
            # PERFIL
            # ====================================================

            perfil = generar_perfil(
                radar_scores
            )

            st.subheader("🧠 Perfil del alumno")

            for item in perfil:
                st.write(
                    f"• {item}"
                )


            # ====================================================
            # PDF
            # ====================================================

            st.subheader("📄 Informe")

            try:

                pdf_file = generar_pdf(
                    name,
                    group,
                    radar_scores,
                    perfil
                )

                with open(
                    pdf_file,
                    "rb"
                ) as f:

                    st.download_button(
                        label="📄 Descargar informe PDF",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

            except Exception as e:

                st.warning(
                    "El resultado se ha guardado, pero no se ha podido "
                    f"generar el PDF: {e}"
                )


# ============================================================
# DASHBOARD
# ============================================================

with tab2:

    st.header("📊 Dashboard de clase")

    if df.empty:

        st.info(
            "Todavía no hay exámenes registrados."
        )

    else:

        competencias = [
            "comprension",
            "morfologia",
            "semantica",
            "literatura",
            "sintaxis"
        ]

        disponibles = [
            c for c in competencias
            if c in df.columns
        ]

        st.subheader("Media de la clase")

        if disponibles:

            st.bar_chart(
                df[disponibles].mean()
            )


        st.subheader("👤 Seleccionar alumno")

        alumno = st.selectbox(
            "Alumno",
            df["name"].dropna().unique(),
            key="dashboard_alumno"
        )

        user = df[
            df["name"] == alumno
        ].iloc[-1]


        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Nota inicial",
                f"{float(user.get('nota_inicial', 0)):.2f}"
            )

        with col2:
            st.metric(
                "Descuento",
                f"-{float(user.get('descuento_ortografia', 0)):.2f}"
            )

        with col3:
            st.metric(
                "Nota final",
                f"{float(user.get('nota_final', user.get('total', 0))):.2f}"
            )


        st.subheader("📋 Datos del alumno")

        st.dataframe(
            user.to_frame().T,
            use_container_width=True,
            hide_index=True
        )


        if disponibles:

            st.subheader(
                "📊 Alumno frente a la clase"
            )

            try:

                st.plotly_chart(
                    comparativa(
                        user,
                        df
                    ),
                    use_container_width=True
                )

            except Exception as e:

                st.warning(
                    f"No se ha podido generar la comparativa: {e}"
                )


# ============================================================
# HISTORIAL ALUMNO
# ============================================================

with tab3:

    st.header("👤 Historial del alumno")

    if df.empty:

        st.info(
            "Todavía no hay resultados."
        )

    else:

        alumno = st.selectbox(
            "Selecciona alumno",
            df["name"].dropna().unique(),
            key="historial_alumno"
        )

        historial = df[
            df["name"] == alumno
        ].copy()

        st.dataframe(
            historial,
            use_container_width=True,
            hide_index=True
        )

        if not historial.empty:

            ultimo = historial.iloc[-1]

            st.subheader("Último resultado")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Nota inicial",
                    f"{float(ultimo.get('nota_inicial', 0)):.2f}"
                )

            with col2:
                st.metric(
                    "Ortografía",
                    str(int(float(ultimo.get("ortografia", 0))))
                )

            with col3:
                st.metric(
                    "Tildes",
                    str(int(float(ultimo.get("tildes", 0))))
                )

            with col4:
                st.metric(
                    "Nota final",
                    f"{float(ultimo.get('nota_final', ultimo.get('total', 0))):.2f}"
                )
```
