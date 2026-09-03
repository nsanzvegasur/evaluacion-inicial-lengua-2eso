import streamlit as st

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2.º ESO NEE",
    page_icon="📚",
    layout="centered"
)

st.title("PRUEBA — LA APP HA ARRANCADO")


import csv
import io
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd
import streamlit as st
from openpyxl import Workbook

from examen2ESO_NEE import EXAMEN
from analytics import radar_chart, comparativa, generar_perfil


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Evaluación Inicial Lengua 2.º ESO NEE",
    page_icon="📚",
    layout="centered"
)

CSV_FILE = "results.csv"

# Estado de sesión
if "examen_enviado" not in st.session_state:
    st.session_state.examen_enviado = False

if "resultado_fila" not in st.session_state:
    st.session_state.resultado_fila = None

if "resultado_respuestas" not in st.session_state:
    st.session_state.resultado_respuestas = None

if "resultado_perfil" not in st.session_state:
    st.session_state.resultado_perfil = None

if "resultado_excel" not in st.session_state:
    st.session_state.resultado_excel = None

if "resultado_csv" not in st.session_state:
    st.session_state.resultado_csv = None


EXAM = EXAMEN["2ESO_NEE"]


# ============================================================
# PUNTUACIÓN
# ============================================================

# Igual estructura que el examen ordinario:
#
# Comprensión ........ 2,0
# Morfología ......... 2,5
# Semántica .......... 1,0
# Textos + diálogo ... 1,5
# Literatura ......... 2,0
# Sintaxis ........... 1,0
#
# TOTAL AUTOMÁTICO = 10 puntos
# Se transforma a 9 puntos.
#
# Producción escrita = 1 punto adicional.
#
# NOTA FINAL = automático / 9 + producción / 1

PESOS = {
    "comprension": 2.0,
    "morfologia": 2.5,
    "semantica": 1.0,
    "textos": 1.5,
    "literatura": 2.0,
    "sintaxis": 1.0,
}


NOMBRES = {
    "comprension": "Comprensión lectora",
    "morfologia": "Morfología",
    "semantica": "Semántica",
    "textos": "Tipos de texto y diálogo",
    "literatura": "Literatura",
    "sintaxis": "Sintaxis",
}


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar(texto):
    if texto is None:
        return ""

    texto = str(texto).strip().lower()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto


def lista_normalizada(texto):
    """
    Permite respuestas separadas por:
    - comas
    - punto y coma
    - saltos de línea
    """
    if texto is None:
        return []

    partes = re.split(r"[,;\n]+", str(texto))

    return [
        normalizar(p)
        for p in partes
        if normalizar(p)
    ]


def exacta(respuesta, opciones):
    r = normalizar(respuesta)

    if isinstance(opciones, str):
        opciones = [opciones]

    return r in [normalizar(x) for x in opciones]


def contiene(respuesta, opciones):
    r = normalizar(respuesta)

    if isinstance(opciones, str):
        opciones = [opciones]

    return any(normalizar(x) in r for x in opciones)


# ============================================================
# CORRECCIÓN DE COMPRENSIÓN
# ============================================================

def corregir_comprension(res):
    puntos = 0.0

    # --------------------------------------------------------
    # C1 - Lugar
    # --------------------------------------------------------

    r = res.get("c1", "")

    if contiene(
        r,
        [
            "tren",
            "vagon",
            "vagón",
            "estacion",
            "estación",
            "ciudad"
        ]
    ):
        puntos += 0.30

    # --------------------------------------------------------
    # C2 - Personajes
    # --------------------------------------------------------

    r = res.get("c2", "")
    elementos = lista_normalizada(r)

    personajes_validos = {
        "hombre",
        "hombre joven",
        "joven",
        "viajero",
        "anciana",
        "mujer",
    }

    encontrados = set()

    for elemento in elementos:
        for personaje in personajes_validos:
            if elemento == personaje:
                encontrados.add(personaje)

    # Se considera correcta si identifica al menos:
    # hombre/joven/viajero + anciana
    tiene_hombre = any(
        x in encontrados
        for x in ["hombre", "hombre joven", "joven", "viajero"]
    )

    tiene_anciana = "anciana" in encontrados or "mujer" in encontrados

    if tiene_hombre and tiene_anciana:
        puntos += 0.35
    elif tiene_hombre or tiene_anciana:
        puntos += 0.15

    # --------------------------------------------------------
    # C3 - Momento del día
    # --------------------------------------------------------

    r = res.get("c3", "")

    if contiene(
        r,
        [
            "madrugada",
            "amanecer",
            "mañana",
            "mañana temprano",
            "de madrugada"
        ]
    ):
        puntos += 0.35

    # --------------------------------------------------------
    # C4 - Tres acciones
    # --------------------------------------------------------

    r = res.get("c4", "")
    acciones = lista_normalizada(r)

    acciones_validas = {
        "mirar",
        "miraba",
        "sujetar",
        "sujetaba",
        "dormir",
        "dormia",
        "llegar",
        "llego",
        "bajar",
        "bajo",
        "respirar",
        "respiro",
        "caminar",
        "camino",
        "detenerse",
        "se detenia",
        "se detuvo",
        "avanzar",
        "avanzaba",
        "recorrer",
        "recorria",
        "cubrir",
        "cubria",
        "ver",
        "veia",
        "salir",
        "salio",
        "sentir",
        "sintio",
    }

    acciones_encontradas = []

    for accion in acciones:
        if accion in acciones_validas:
            if accion not in acciones_encontradas:
                acciones_encontradas.append(accion)

    cantidad = min(len(acciones_encontradas), 3)

    if cantidad == 1:
        puntos += 0.12

    elif cantidad == 2:
        puntos += 0.24

    elif cantidad >= 3:
        puntos += 0.35

    return min(round(puntos, 2), 2.0)


# ============================================================
# CORRECCIÓN DE MORFOLOGÍA
# ============================================================

def corregir_morfologia(res):
    puntos = 0.0

    criterios = {
        "m1": {
            "lexema": ["silenci", "silencio"],
            "morfemas": ["o"],
            "estructura": ["simple"],
            "categoria": ["sustantivo", "masculino", "singular"],
            "vi": ["v"],
        },
        "m2": {
            "lexema": ["lent"],
            "morfemas": ["mente"],
            "estructura": ["derivada"],
            "categoria": ["adverbio", "modo"],
            "vi": ["i"],
        },
        "m3": {
            "lexema": ["conoc"],
            "morfemas": ["des", "ido"],
            "estructura": ["derivada"],
            "categoria": ["adjetivo", "masculino", "singular"],
            "vi": ["v"],
        },
        "m4": {
            "lexema": ["mochil"],
            "morfemas": ["a+s", "as", "a s"],
            "estructura": ["simple"],
            "categoria": ["sustantivo", "femenino", "plural"],
            "vi": ["v"],
        },
    }

    for mid, criterio in criterios.items():

        datos = res.get(mid, {})

        # Cada palabra vale 0,50
        # Lexema .......... 0,10
        # Morfemas ........ 0,10
        # Estructura ...... 0,10
        # Categoría ....... 0,15
        # V/I ............. 0,05

        if contiene(
            datos.get("lexema", ""),
            criterio["lexema"]
        ):
            puntos += 0.10

        if contiene(
            datos.get("morfemas", ""),
            criterio["morfemas"]
        ):
            puntos += 0.10

        if exacta(
            datos.get("estructura", ""),
            criterio["estructura"]
        ):
            puntos += 0.10

        categoria = normalizar(
            datos.get("categoria", "")
        )

        categoria_correcta = all(
            normalizar(x) in categoria
            for x in criterio["categoria"]
        )

        if categoria_correcta:
            puntos += 0.15

        if exacta(
            datos.get("vi", ""),
            criterio["vi"]
        ):
            puntos += 0.05

    # --------------------------------------------------------
    # Determinantes y pronombres
    # --------------------------------------------------------

    dp_correctas = {
        "dp1": "determinante",
        "dp2": "determinante",
        "dp3": "pronombre",
    }

    for did, correcta in dp_correctas.items():

        if exacta(
            res.get(did, ""),
            correcta
        ):
            puntos += 0.1667

    return min(round(puntos, 2), 2.5)


# ============================================================
# CORRECCIÓN DE SEMÁNTICA
# ============================================================

def corregir_semantica(res):
    puntos = 0.0

    correctas = {
        "s1": ["antonimia", "antónimos", "antonimos"],
        "s2": ["campo semántico", "campo semantico"],
        "s3": ["polisemia", "polisémica", "polisemica"],
        "s4": ["meronimia", "meronimia/holonimia"],
        "s5": ["hiponimia", "hipónimos", "hiponimos"],
    }

    for sid, opciones in correctas.items():

        if exacta(
            res.get(sid, ""),
            opciones
        ):
            puntos += 0.20

    return min(round(puntos, 2), 1.0)


# ============================================================
# CORRECCIÓN DE TIPOS DE TEXTO + DIÁLOGO
# ============================================================

def corregir_textos(res):
    puntos = 0.0

    correctas = {
        "t1": [
            "instructivo",
            "instruccional",
        ],
        "t2": [
            "expositivo",
        ],
        "t3": [
            "argumentativo",
            "persuasivo",
        ],
    }

    for tid, opciones in correctas.items():

        if exacta(
            res.get(tid, ""),
            opciones
        ):
            puntos += 0.3333

    # --------------------------------------------------------
    # Diálogo
    # --------------------------------------------------------

    # D1 - Interlocutores
    interlocutores = lista_normalizada(
        res.get("d1", "")
    )

    tiene_lucia = "lucia" in interlocutores
    tiene_carlos = "carlos" in interlocutores

    if tiene_lucia and tiene_carlos:
        puntos += 0.10

    # D2 - Número de intervenciones
    if exacta(
        res.get("d2", ""),
        [
            "6",
            "seis",
            "6 intervenciones",
            "seis intervenciones"
        ]
    ):
        puntos += 0.10

    # D3 - Estilo indirecto
    r = res.get("d3", "")
    rn = normalizar(r)

    d3 = 0.0

    # Verbo introductorio
    if contiene(
        rn,
        [
            "dijo",
            "respondio",
            "contesto",
            "afirmo",
            "explico",
        ]
    ):
        d3 += 0.10

    # Que
    if " que " in f" {rn} ":
        d3 += 0.10

    # Cambio temporal
    if contiene(
        rn,
        [
            "dia anterior",
            "dia antes",
            "tarde anterior",
            "dia previo",
        ]
    ):
        d3 += 0.05

    # Cambio verbal
    if contiene(
        rn,
        [
            "habia hecho",
            "habia realizado",
        ]
    ):
        d3 += 0.05

    puntos += d3

    # IMPORTANTE:
    # El bloque completo de textos + diálogo
    # nunca puede superar 1,5 puntos.
    return min(round(puntos, 2), 1.5)


# ============================================================
# CORRECCIÓN DE LITERATURA
# ============================================================

def corregir_literatura(res):
    puntos = 0.0

    # --------------------------------------------------------
    # L1 - Número de versos
    # --------------------------------------------------------

    if exacta(
        res.get("l1", ""),
        ["4", "cuatro", "4 versos", "cuatro versos"]
    ):
        puntos += 0.30

    # --------------------------------------------------------
    # L2 - Arte mayor / menor
    # --------------------------------------------------------

    if exacta(
        res.get("l2", ""),
        [
            "arte mayor",
            "mayor",
        ]
    ):
        puntos += 0.30

    # --------------------------------------------------------
    # L3 - Esquema métrico
    #
    # Acepta:
    # 10A 10B 10A 10B
    # 10A, 10B, 10A, 10B
    # 10A; 10B; 10A; 10B
    #
    # A y B deben aparecer en mayúscula.
    # --------------------------------------------------------

    esquema = res.get("l3", "")

    esquema_limpio = re.sub(
        r"[\s,;|/-]+",
        " ",
        str(esquema).strip()
    )

    esquema_limpio = re.sub(
        r"\s+",
        " ",
        esquema_limpio
    )

    if esquema_limpio == "10A 10B 10A 10B":
        puntos += 0.35

    # --------------------------------------------------------
    # L4 - Rima
    # --------------------------------------------------------

    if exacta(
        res.get("l4", ""),
        [
            "consonante",
        ]
    ):
        puntos += 0.35

    # --------------------------------------------------------
    # L5 - Sinalefa
    # --------------------------------------------------------

    r = normalizar(
        res.get("l5", "")
    )

    palabras_sinalefa = [
        "sobre el",
        "junto al",
    ]

    explica_sinalefa = [
        "sinalefa",
        "se unen",
        "union",
        "unión",
    ]

    tiene_palabras = any(
        normalizar(x) in r
        for x in palabras_sinalefa
    )

    tiene_explicacion = any(
        normalizar(x) in r
        for x in explica_sinalefa
    )

    if tiene_palabras and tiene_explicacion:
        puntos += 0.35

    # --------------------------------------------------------
    # L6 - Personificación
    # --------------------------------------------------------

    r = normalizar(
        res.get("l6", "")
    )

    tiene_expresion = (
        "viento susurra" in r
    )

    tiene_personificacion = any(
        x in r
        for x in [
            "personificacion",
            "personificación",
            "persona",
            "humana",
            "humano",
        ]
    )

    if tiene_expresion and tiene_personificacion:
        puntos += 0.35

    return min(round(puntos, 2), 2.0)


# ============================================================
# CORRECCIÓN DE SINTAXIS
# ============================================================

def corregir_sintaxis(res):
    """
    NEE:
    3 preguntas de frase/oración
    3 preguntas de modalidad

    Las seis juntas valen 1 punto.
    Por tanto:
        1 respuesta correcta = 0,1667
    """

    puntos = 0.0

    correctas = {
        "x1": ["frase"],
        "x2": ["oracion", "oración"],
        "x5": ["oracion", "oración"],
        "x6": ["interrogativa"],
        "x8": ["exclamativa"],
        "x9": ["enunciativa"],
    }

    for xid, opciones in correctas.items():

        if exacta(
            res.get(xid, ""),
            opciones
        ):
            puntos += 1 / 6

    return min(round(puntos, 2), 1.0)


# ============================================================
# CORRECCIÓN GENERAL
# ============================================================

def corregir(res):

    p = {}

    p["comprension"] = corregir_comprension(res)
    p["morfologia"] = corregir_morfologia(res)
    p["semantica"] = corregir_semantica(res)
    p["textos"] = corregir_textos(res)
    p["literatura"] = corregir_literatura(res)
    p["sintaxis"] = corregir_sintaxis(res)

    # Los apartados suman 10 puntos automáticos.
    total_automatico_sobre_10 = sum(p.values())

    # El examen automático equivale a 9 puntos.
    total_automatico = round(
        total_automatico_sobre_10 * 0.9,
        2
    )

    # Seguridad: nunca más de 9.
    total_automatico = min(
        total_automatico,
        9.0
    )

    return p, total_automatico


# ============================================================
# PRODUCCIÓN ESCRITA
# ============================================================

def corregir_produccion(texto):

    """
    La producción escrita vale 1 punto.

    No se añade una pregunta o tema nuevo.
    Se valora únicamente la extensión de la respuesta.
    """

    palabras = normalizar(
        texto
    ).split()

    n = len(palabras)

    if n == 0:
        return 0.0

    if n < 5:
        return 0.25

    if n < 10:
        return 0.50

    if n < 20:
        return 0.75

    return 1.0


# ============================================================
# ORTOGRAFÍA
# ============================================================

def detectar_ortografia(texto):

    texto = str(texto or "")

    faltas_ortografia = 0
    faltas_tildes = 0

    # Errores muy evidentes que queremos detectar.
    errores = [
        r"\bavia\b",
        r"\bhabia\b",
        r"\bahi\b",
        r"\btambien\b",
        r"\bdespues\b",
        r"\bmas\b",
    ]

    texto_normalizado = normalizar(texto)

    for patron in errores:
        if re.search(patron, texto_normalizado):
            faltas_tildes += 1

    return faltas_ortografia, faltas_tildes


# ============================================================
# CSV
# ============================================================

def guardar_csv(fila):

    columnas = list(fila.keys())

    existe = os.path.exists(CSV_FILE)

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columnas
        )

        if not existe:
            writer.writeheader()

        writer.writerow(fila)


# ============================================================
# CSV INDIVIDUAL
# ============================================================

def csv_individual(fila):

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=list(fila.keys())
    )

    writer.writeheader()
    writer.writerow(fila)

    return output.getvalue().encode(
        "utf-8-sig"
    )


# ============================================================
# EXCEL INDIVIDUAL
# ============================================================

def excel_individual(fila, puntos, respuestas):

    wb = Workbook()

    ws = wb.active
    ws.title = "Resultado"

    ws.append([
        "Alumno",
        fila.get("nombre", "")
    ])

    ws.append([
        "Grupo",
        fila.get("grupo", "")
    ])

    ws.append([
        "Fecha",
        fila.get("fecha", "")
    ])

    ws.append([])

    ws.append([
        "Apartado",
        "Puntuación"
    ])

    for clave, nombre in NOMBRES.items():
        ws.append([
            nombre,
            puntos.get(clave, 0)
        ])

    ws.append([])

    ws.append([
        "Automático / 9",
        fila.get("nota_automatica", 0)
    ])

    ws.append([
        "Producción / 1",
        fila.get("produccion", 0)
    ])

    ws.append([
        "Nota final / 10",
        fila.get("nota_final", 0)
    ])

    ws.append([])

    ws.append([
        "Respuestas"
    ])

    for clave, valor in respuestas.items():

        if isinstance(valor, dict):
            ws.append([
                clave,
                str(valor)
            ])
        else:
            ws.append([
                clave,
                str(valor)
            ])

    output = io.BytesIO()

    wb.save(output)

    output.seek(0)

    return output.getvalue()


# ============================================================
# LECTURA SEGURA DE RESULTADOS
# ============================================================

def safe_read_results():

    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()

    try:
        df = pd.read_csv(
            CSV_FILE,
            encoding="utf-8-sig"
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# COMPROBAR SI YA HA REALIZADO EL EXAMEN
# ============================================================

def alumno_ya_realizo_examen(nombre, grupo):

    df = safe_read_results()

    if df.empty:
        return False

    if "nombre" not in df.columns:
        return False

    if "grupo" not in df.columns:
        return False

    nombre_n = normalizar(nombre)
    grupo_n = normalizar(grupo)

    for _, fila in df.iterrows():

        if (
            normalizar(fila.get("nombre", "")) == nombre_n
            and
            normalizar(fila.get("grupo", "")) == grupo_n
        ):
            return True

    return False


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    html, body, [class*="css"] {
        font-family: "Atkinson Hyperlegible", Arial, sans-serif;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    p, li, label {
        font-size: 20px !important;
        line-height: 1.55 !important;
    }

    h1 {
        font-size: 34px !important;
    }

    h2 {
        font-size: 29px !important;
    }

    h3 {
        font-size: 25px !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] {
        font-size: 19px !important;
    }

    .bloque {
        padding: 1.2rem;
        border-radius: 12px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #cccccc;
    }

    .poema {
        font-size: 23px;
        line-height: 1.8;
        padding: 1rem;
        border-left: 4px solid #777;
        margin: 1rem 0;
    }

    .dialogo {
        font-size: 21px;
        line-height: 1.7;
        padding: 1rem;
        border: 1px solid #cccccc;
        border-radius: 10px;
        margin: 1rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PANTALLA DE RESULTADOS
# ============================================================

if st.session_state.examen_enviado:

    fila = st.session_state.resultado_fila
    puntos = st.session_state.resultado_perfil
    respuestas = st.session_state.resultado_respuestas

    st.title("📚 Resultado de la evaluación")

    st.success("La evaluación se ha guardado correctamente.")

    nota_automatica = float(
        fila.get("nota_automatica", 0)
    )

    produccion = float(
        fila.get("produccion", 0)
    )

    nota_final = float(
        fila.get("nota_final", 0)
    )

    st.metric(
        "Puntuación automática",
        f"{nota_automatica:.2f} / 9"
    )

    st.metric(
        "Producción escrita",
        f"{produccion:.2f} / 1"
    )

    st.metric(
        "Nota final",
        f"{nota_final:.2f} / 10"
    )

    st.markdown("---")

    st.subheader("📊 Resultados por apartados")

    datos_grafico = {
        clave: puntos.get(clave, 0)
        for clave in NOMBRES
    }

    try:
        fig = radar_chart(datos_grafico)
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    except Exception:
        pass

    for clave, nombre in NOMBRES.items():

        valor = float(
            puntos.get(clave, 0)
        )

        maximo = PESOS[clave]

        porcentaje = (
            valor / maximo * 100
            if maximo
            else 0
        )

        st.write(
            f"**{nombre}:** "
            f"{valor:.2f} / {maximo:.1f}"
        )

        st.progress(
            min(
                max(porcentaje / 100, 0),
                1
            )
        )

    st.markdown("---")

    # --------------------------------------------------------
    # ORTOGRAFÍA
    # --------------------------------------------------------

    faltas_ortografia = int(
        fila.get("faltas_ortografia", 0)
    )

    faltas_tildes = int(
        fila.get("faltas_tildes", 0)
    )

    st.subheader("✏️ Ortografía")

    st.write(
        f"Errores ortográficos detectados: "
        f"**{faltas_ortografia}**"
    )

    st.write(
        f"Errores de tildes detectados: "
        f"**{faltas_tildes}**"
    )

    st.info(
        "Los errores ortográficos se registran "
        "para la evaluación, pero no restan puntos "
        "de la nota automática."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # COMPARATIVA ANÓNIMA
    # --------------------------------------------------------

    st.subheader("📊 Estadísticas del grupo")

    df_resultados = safe_read_results()

    if not df_resultados.empty:

        # Nunca mostramos nombres reales.
        df_comparativa = df_resultados.copy()

        if "nota_final" in df_comparativa.columns:

            df_comparativa = df_comparativa[
                ["nota_final"]
            ].copy()

            df_comparativa["Alumno"] = [
                f"Alumno {i + 1}"
                for i in range(
                    len(df_comparativa)
                )
            ]

            df_comparativa = df_comparativa[
                ["Alumno", "nota_final"]
            ]

            df_comparativa = df_comparativa.rename(
                columns={
                    "nota_final": "Nota"
                }
            )

            st.dataframe(
                df_comparativa,
                use_container_width=True,
                hide_index=True
            )

            try:
                fig_comp = comparativa(
                    df_comparativa
                )

                st.plotly_chart(
                    fig_comp,
                    use_container_width=True
                )

            except Exception:
                pass

    # --------------------------------------------------------
    # DESCARGAS
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("📥 Descargar resultado")

    if st.session_state.resultado_excel:

        st.download_button(
            label="📊 Descargar Excel",
            data=st.session_state.resultado_excel,
            file_name="resultado_evaluacion_2ESO_NEE.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    if st.session_state.resultado_csv:

        st.download_button(
            label="📄 Descargar CSV",
            data=st.session_state.resultado_csv,
            file_name="resultado_evaluacion_2ESO_NEE.csv",
            mime="text/csv"
        )

    st.stop()


# ============================================================
# CABECERA
# ============================================================

st.title("📚 Evaluación Inicial de Lengua Castellana")
st.header("2.º ESO — Adaptación NEE")

st.write(
    "Completa todas las actividades con calma. "
    "Lee bien cada pregunta antes de responder."
)


# ============================================================
# DATOS DEL ALUMNO
# ============================================================

st.markdown("---")
st.header("Datos del alumno")

nombre = st.text_input(
    "Nombre y apellidos"
)

grupo = st.selectbox(
    "Grupo",
    [
        "",
        "2º A",
        "2º B",
        "2º C",
        "2º D",
    ]
)


# ============================================================
# FORMULARIO
# ============================================================

with st.form("examen_form"):

    respuestas = {}

    # ========================================================
    # 1. COMPRENSIÓN LECTORA
    # ========================================================

    st.markdown("---")
    st.header("1. Comprensión lectora")

    st.markdown(
        f"""
        <div class="bloque">
        {EXAM["comprension"]["texto"].replace(chr(10), "<br><br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    preguntas_comp = EXAM[
        "comprension"
    ][
        "preguntas"
    ]

    for pregunta in preguntas_comp:

        st.markdown(
            pregunta["enunciado"],
            unsafe_allow_html=True
        )

        respuestas[pregunta["id"]] = st.text_input(
            "Respuesta",
            key=f"resp_{pregunta['id']}"
        )

    # ========================================================
    # 2. MORFOLOGÍA
    # ========================================================

    st.markdown("---")
    st.header("2. Morfología")

    st.write(
        "Analiza las siguientes palabras."
    )

    respuestas["morfologia"] = {}

    estructuras = [
        "",
        "Simple",
        "Derivada",
    ]

    vi_opciones = [
        "",
        "V",
        "I",
    ]

    for palabra in EXAM["morfologia"]:

        mid = palabra["id"]

        st.markdown(
            f"<h3>{palabra['palabra']}</h3>",
            unsafe_allow_html=True
        )

        respuestas["morfologia"][mid] = {}

        respuestas["morfologia"][mid][
            "lexema"
        ] = st.text_input(
            "Lexema",
            key=f"{mid}_lexema"
        )

        respuestas["morfologia"][mid][
            "morfemas"
        ] = st.text_input(
            "Morfemas",
            key=f"{mid}_morfemas"
        )

        respuestas["morfologia"][mid][
            "estructura"
        ] = st.selectbox(
            "Estructura",
            estructuras,
            key=f"{mid}_estructura"
        )

        respuestas["morfologia"][mid][
            "categoria"
        ] = st.text_input(
            "Categoría gramatical",
            key=f"{mid}_categoria"
        )

        respuestas["morfologia"][mid][
            "vi"
        ] = st.selectbox(
            "V / I",
            vi_opciones,
            key=f"{mid}_vi"
        )

    # ========================================================
    # DETERMINANTES Y PRONOMBRES
    # ========================================================

    st.subheader(
        "2.2. Determinantes y pronombres"
    )

    dp_opciones = [
        "",
        "Determinante",
        "Pronombre",
    ]

    for pregunta in EXAM[
        "determinantes_pronombres"
    ]:

        st.markdown(
            pregunta["frase"],
            unsafe_allow_html=True
        )

        st.markdown(
            pregunta["enunciado"],
            unsafe_allow_html=True
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Respuesta",
            dp_opciones,
            key=f"resp_{pregunta['id']}"
        )

    # ========================================================
    # 3. SEMÁNTICA
    # ========================================================

    st.markdown("---")
    st.header("3. Semántica")

    semantica_opciones = [
        "",
        "Antonimia",
        "Campo semántico",
        "Polisemia",
        "Meronimia",
        "Hiponimia",
    ]

    for pregunta in EXAM["semantica"]:

        st.markdown(
            pregunta["enunciado"],
            unsafe_allow_html=True
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Relación semántica",
            semantica_opciones,
            key=f"resp_{pregunta['id']}"
        )

    # ========================================================
    # 4. TIPOS DE TEXTO
    # ========================================================

    st.markdown("---")
    st.header("4. Tipos de texto")

    st.markdown(
        EXAM["textos"]["enunciado"],
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="bloque">
        <strong>Texto A</strong><br>
        Apaga el horno y deja reposar la masa durante diez minutos antes de usarla.
        <br><br>
        <strong>Texto B</strong><br>
        Los mamíferos son animales vertebrados que alimentan a sus crías con leche.
        <br><br>
        <strong>Texto C</strong><br>
        Reciclar ayuda a reducir la contaminación y cuidar el medio ambiente.
        </div>
        """,
        unsafe_allow_html=True
    )

    tipo_texto_opciones = [
        "",
        "Instructivo",
        "Expositivo",
        "Argumentativo",
    ]

    for pregunta in EXAM[
        "textos"
    ][
        "preguntas"
    ]:

        st.markdown(
            pregunta["enunciado"],
            unsafe_allow_html=True
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Tipo de texto",
            tipo_texto_opciones,
            key=f"resp_{pregunta['id']}"
        )

    # ========================================================
    # 5. LITERATURA
    # ========================================================

    st.markdown("---")
    st.header("5. Literatura")

    st.markdown(
        "Lee el poema.",
        unsafe_allow_html=True
    )

    poema_html = (
        EXAM["literatura"]["poema"]
        .replace("\n", "<br>")
    )

    st.markdown(
        f"""
        <div class="poema">
        {poema_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    preguntas_lit = EXAM[
        "literatura"
    ][
        "preguntas"
    ]

    # L1
    st.markdown(
        preguntas_lit[0]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l1"] = st.selectbox(
        "Número de versos",
        ["", "4", "3", "5"],
        key="resp_l1"
    )

    # L2
    st.markdown(
        preguntas_lit[1]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l2"] = st.selectbox(
        "Arte mayor o menor",
        [
            "",
            "Arte mayor",
            "Arte menor",
        ],
        key="resp_l2"
    )

    # L3
    st.markdown(
        preguntas_lit[2]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l3"] = st.text_input(
        "Esquema métrico",
        key="resp_l3",
        placeholder="Ejemplo: 10A 10B 10A 10B"
    )

    # L4
    st.markdown(
        preguntas_lit[3]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l4"] = st.selectbox(
        "Tipo de rima",
        [
            "",
            "Consonante",
            "Asonante",
        ],
        key="resp_l4"
    )

    # L5
    st.markdown(
        preguntas_lit[4]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l5"] = st.text_input(
        "Sinalefa",
        key="resp_l5"
    )

    # L6
    st.markdown(
        preguntas_lit[5]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["l6"] = st.text_area(
        "Personificación",
        key="resp_l6"
    )

    # ========================================================
    # 6. SINTAXIS
    # ========================================================

    st.markdown("---")
    st.header("6. Sintaxis")

    st.subheader(
        "6.1. Frase u oración"
    )

    # IMPORTANTE:
    # NEE tiene exactamente 3 aquí:
    # x1, x2, x5
    #
    # No usamos [:5] porque el examen NEE
    # solo tiene 6 preguntas.

    for pregunta in EXAM["sintaxis"][:3]:

        st.markdown(
            f"<strong>{pregunta['frase']}</strong>",
            unsafe_allow_html=True
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Respuesta",
            [
                "",
                "Frase",
                "Oración",
            ],
            key=f"resp_{pregunta['id']}"
        )

    st.subheader(
        "6.2. Modalidad oracional"
    )

    # Las 3 restantes:
    # x6, x8, x9

    modalidades = [
        "",
        "Enunciativa",
        "Interrogativa",
        "Exclamativa",
        "Desiderativa",
        "Exhortativa",
    ]

    for pregunta in EXAM["sintaxis"][3:]:

        st.markdown(
            f"<strong>{pregunta['frase']}</strong>",
            unsafe_allow_html=True
        )

        respuestas[
            pregunta["id"]
        ] = st.selectbox(
            "Modalidad",
            modalidades,
            key=f"resp_{pregunta['id']}"
        )

    # ========================================================
    # 7. DIÁLOGO
    # ========================================================

    st.markdown("---")
    st.header("7. Diálogo")

    dialogo_html = (
        EXAM["dialogo"]["texto"]
        .replace("\n", "<br>")
    )

    st.markdown(
        f"""
        <div class="dialogo">
        {dialogo_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    preguntas_dialogo = EXAM[
        "dialogo"
    ][
        "preguntas"
    ]

    # D1
    st.markdown(
        preguntas_dialogo[0]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["d1"] = st.text_input(
        "Interlocutores",
        key="resp_d1",
        placeholder="Ejemplo: Lucía, Carlos"
    )

    # D2
    st.markdown(
        preguntas_dialogo[1]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["d2"] = st.text_input(
        "Número",
        key="resp_d2"
    )

    # D3
    st.markdown(
        preguntas_dialogo[2]["enunciado"],
        unsafe_allow_html=True
    )

    respuestas["d3"] = st.text_area(
        "Respuesta",
        key="resp_d3"
    )

    # ========================================================
    # 8. PRODUCCIÓN ESCRITA
    # ========================================================

    st.markdown("---")
    st.header("8. Producción escrita — 1 punto")

    st.text_area(
        "Respuesta",
        key="produccion"
    )

    # ========================================================
    # ENVÍO
    # ========================================================

    st.markdown("---")

    enviado = st.form_submit_button(
        "✅ Entregar evaluación",
        use_container_width=True
    )


# ============================================================
# PROCESAR ENVÍO
# ============================================================

if enviado:

    # --------------------------------------------------------
    # Comprobar datos
    # --------------------------------------------------------

    if not nombre.strip():

        st.error(
            "Escribe tu nombre y apellidos antes de entregar."
        )

        st.stop()

    if not grupo:

        st.error(
            "Selecciona tu grupo antes de entregar."
        )

        st.stop()

    # --------------------------------------------------------
    # Evitar duplicados
    # --------------------------------------------------------

    if alumno_ya_realizo_examen(
        nombre,
        grupo
    ):

        st.error(
            "Ya existe una evaluación registrada "
            "con ese nombre y grupo."
        )

        st.stop()

    # --------------------------------------------------------
    # Preparar respuestas para corrección
    # --------------------------------------------------------

    respuestas_correccion = {}

    # Comprensión
    for pregunta in EXAM[
        "comprension"
    ][
        "preguntas"
    ]:

        respuestas_correccion[
            pregunta["id"]
        ] = respuestas.get(
            pregunta["id"],
            ""
        )

    # Morfología
    for mid, datos in respuestas.get(
        "morfologia",
        {}
    ).items():

        respuestas_correccion[mid] = datos

    # DP
    for pregunta in EXAM[
        "determinantes_pronombres"
    ]:

        did = pregunta["id"]

        respuestas_correccion[did] = (
            respuestas.get(did, "")
        )

    # Semántica
    for pregunta in EXAM["semantica"]:

        sid = pregunta["id"]

        respuestas_correccion[sid] = (
            respuestas.get(sid, "")
        )

    # Textos
    for pregunta in EXAM[
        "textos"
    ][
        "preguntas"
    ]:

        tid = pregunta["id"]

        respuestas_correccion[tid] = (
            respuestas.get(tid, "")
        )

    # Literatura
    for pregunta in EXAM[
        "literatura"
    ][
        "preguntas"
    ]:

        lid = pregunta["id"]

        respuestas_correccion[lid] = (
            respuestas.get(lid, "")
        )

    # Sintaxis
    for pregunta in EXAM["sintaxis"]:

        xid = pregunta["id"]

        respuestas_correccion[xid] = (
            respuestas.get(xid, "")
        )

    # Diálogo
    for pregunta in EXAM[
        "dialogo"
    ][
        "preguntas"
    ]:

        did = pregunta["id"]

        respuestas_correccion[did] = (
            respuestas.get(did, "")
        )

    # --------------------------------------------------------
    # Corrección
    # --------------------------------------------------------

    puntos, nota_automatica = corregir(
        respuestas_correccion
    )

    # --------------------------------------------------------
    # Producción
    # --------------------------------------------------------

    texto_produccion = st.session_state.get(
        "produccion",
        ""
    )

    produccion = corregir_produccion(
        texto_produccion
    )

    # --------------------------------------------------------
    # Ortografía
    # --------------------------------------------------------

    texto_para_ortografia = " ".join(
        str(x)
        for x in respuestas_correccion.values()
        if not isinstance(x, dict)
    )

    texto_para_ortografia += " "
    texto_para_ortografia += texto_produccion

    faltas_ortografia, faltas_tildes = (
        detectar_ortografia(
            texto_para_ortografia
        )
    )

    # --------------------------------------------------------
    # IMPORTANTE:
    # NO se descuenta ortografía.
    # --------------------------------------------------------

    nota_final = round(
        nota_automatica + produccion,
        2
    )

    nota_final = min(
        nota_final,
        10.0
    )

    # --------------------------------------------------------
    # Fecha
    # --------------------------------------------------------

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # Fila para CSV
    # --------------------------------------------------------

    fila = {
        "nombre": nombre.strip(),
        "grupo": grupo,
        "fecha": fecha,

        "comprension": puntos["comprension"],
        "morfologia": puntos["morfologia"],
        "semantica": puntos["semantica"],
        "textos": puntos["textos"],
        "literatura": puntos["literatura"],
        "sintaxis": puntos["sintaxis"],

        "nota_automatica": nota_automatica,
        "produccion": produccion,
        "nota_final": nota_final,

        "faltas_ortografia": faltas_ortografia,
        "faltas_tildes": faltas_tildes,
    }

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    guardar_csv(fila)

    # --------------------------------------------------------
    # Archivos descargables
    # --------------------------------------------------------

    excel_bytes = excel_individual(
        fila,
        puntos,
        respuestas_correccion
    )

    csv_bytes = csv_individual(
        fila
    )

    # --------------------------------------------------------
    # Guardar estado
    # --------------------------------------------------------

    st.session_state.resultado_fila = fila

    st.session_state.resultado_perfil = puntos

    st.session_state.resultado_respuestas = (
        respuestas_correccion
    )

    st.session_state.resultado_excel = (
        excel_bytes
    )

    st.session_state.resultado_csv = (
        csv_bytes
    )

    st.session_state.examen_enviado = True

    st.rerun()
