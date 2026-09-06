#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_manual_svg.py
=====================

Generador programático del *Manual de Evaluación y Calificación del Desempeño
Académico* (Facultad de Ingeniería · Universidad de Santiago de Chile) como
**SVG multipágina A4 vertical, 100 % editable en Inkscape**.

Jerarquía de fuentes aplicada
-----------------------------
1. ``manual_desempeno_especificacion_editorial_CORREGIDA.md`` — fuente principal
   y autoritativa: define contenido, estructura, diseño editorial, páginas,
   componentes y correcciones (``CORRECTION_OVERRIDE``).
2. ``V2_ManualBorradorResolucion.docx`` — validación del contenido textual.
3. ``avance_manual.svg`` — referencia visual y geométrica (estilo, proporciones,
   iconografía, ritmo visual). Sus errores no se reproducen cuando contradicen
   el Markdown corregido.

Salidas
-------
* ``manual_desempeno_final.svg`` — 30 páginas A4 en un único documento Inkscape.
* ``manual_desempeno_final.pdf`` — 30 páginas.
* ``preview/pagina_NN.png`` — control visual página a página.

Reglas de editabilidad respetadas
---------------------------------
* Todo el texto es ``<text>``/``<tspan>``; ningún texto se convierte a path.
* Tablas, iconos, diagramas y figuras son geometría SVG nativa (``rect``,
  ``line``, ``circle``, ``path``); nada se rasteriza.
* Sólo se usan ``Noto Sans`` y ``Noto Serif Display``.
* Cada objeto conserva un id descriptivo y se agrupa semánticamente en ``<g>``.

Validación automática
---------------------
Antes de escribir el SVG, el generador audita la composición con las métricas
reales de las fuentes Noto: desbordes laterales respecto del margen útil,
invasión de la zona de pie de cada página, solapamientos entre objetos de
texto, filetes que atraviesan una línea y familias tipográficas no permitidas.
``--auditar`` imprime el informe completo; la salida estable no debe arrojar
ningún hallazgo.

Dependencias
------------
* ``fontTools``  — métrica tipográfica real (reflujo y auditoría).
* ``cairosvg``   — render de PNG y PDF por página.
* ``pypdf``      — unión de las 30 páginas en un único PDF.
Si alguna falta, el SVG se genera igual y sólo se omite la salida asociada.

Uso
---
    python3 generar_manual_svg.py            # genera SVG + PDF + previews
    python3 generar_manual_svg.py --no-pdf   # sólo SVG
    python3 generar_manual_svg.py --auditar  # SVG + informe de validación
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN EDITORIAL MAESTRA
#    (DISEÑO EDITORIAL MAESTRO del Markdown corregido)
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SPEC_MD = os.path.join(BASE_DIR, "manual_desempeno_especificacion_editorial_CORREGIDA.md")
SALIDA_SVG = os.path.join(BASE_DIR, "manual_desempeno_final.svg")
SALIDA_PDF = os.path.join(BASE_DIR, "manual_desempeno_final.pdf")
DIR_PREVIEW = os.path.join(BASE_DIR, "preview")

# --- Formato de página -----------------------------------------------------
PAGE_W = 210.0          # mm
PAGE_H = 297.0          # mm
PAGE_GAP = 12.0         # separación entre páginas en el lienzo Inkscape
TOTAL_PAGINAS = 30
VIEWBOX_PAGINA = "0 0 210 297"
FONDO = "#FFFFFF"

# --- Márgenes y zonas seguras ---------------------------------------------
MARGEN_IZQ = 18.0
MARGEN_DER = 192.0      # límite visual derecho
ANCHO_UTIL = MARGEN_DER - MARGEN_IZQ        # 174 mm
CUERPO_TOP = 35.0
CUERPO_BOTTOM_SEGURO = 274.0                # el cuerpo no debe cruzar esta línea
ZONA_PIE_TOP = 276.0

# --- Paleta institucional (COLOR_PALETTE) ---------------------------------
PRIMARY_BLUE = "#0a2d69"
SECONDARY_BLUE = "#5b94d2"
BACKGROUND_WHITE = "#ffffff"
VERY_LIGHT_BLUE = "#eef5fc"
LIGHT_BLUE_2 = "#e8f2fc"
LIGHT_BLUE_3 = "#ddeaf8"
MID_LIGHT_BLUE = "#88b4e3"
RULE_BLUE = "#a8c4e6"

# --- Tipografía normalizada (TYPOGRAPHY) ----------------------------------
SANS = "Noto Sans"
SERIF = "Noto Serif Display"

FAMILIAS_PERMITIDAS = {SANS, SERIF}

RUTA_FUENTES = "/usr/share/fonts/truetype/noto"
ARCHIVOS_FUENTE = {
    (SANS, 100): "NotoSans-Thin.ttf",
    (SANS, 200): "NotoSans-ExtraLight.ttf",
    (SANS, 300): "NotoSans-Light.ttf",
    (SANS, 400): "NotoSans-Regular.ttf",
    (SANS, 500): "NotoSans-Medium.ttf",
    (SANS, 600): "NotoSans-SemiBold.ttf",
    (SANS, 700): "NotoSans-Bold.ttf",
    (SANS, 800): "NotoSans-ExtraBold.ttf",
    (SANS, 900): "NotoSans-Black.ttf",
    (SERIF, 100): "NotoSerifDisplay-Thin.ttf",
    (SERIF, 200): "NotoSerifDisplay-ExtraLight.ttf",
    (SERIF, 300): "NotoSerifDisplay-Light.ttf",
    (SERIF, 400): "NotoSerifDisplay-Regular.ttf",
    (SERIF, 500): "NotoSerifDisplay-Medium.ttf",
    (SERIF, 600): "NotoSerifDisplay-SemiBold.ttf",
    (SERIF, 700): "NotoSerifDisplay-Bold.ttf",
    (SERIF, 800): "NotoSerifDisplay-ExtraBold.ttf",
    (SERIF, 900): "NotoSerifDisplay-Black.ttf",
}


# ---------------------------------------------------------------------------
# 2. MÉTRICA TIPOGRÁFICA
#    Permite reflujo real de texto y auditoría de desbordes.
# ---------------------------------------------------------------------------

class MedidorTexto:
    """Mide anchos de cadena usando las métricas reales de las fuentes Noto."""

    def __init__(self, ruta: str = RUTA_FUENTES) -> None:
        self.ruta = ruta
        self._cache: Dict[Tuple[str, int], Optional[dict]] = {}
        self._disponible = importlib.util.find_spec("fontTools") is not None

    # -- carga perezosa de métricas ----------------------------------------
    def _metricas(self, familia: str, peso: int) -> Optional[dict]:
        peso = self._peso_normalizado(peso)
        clave = (familia, peso)
        if clave in self._cache:
            return self._cache[clave]
        datos = None
        archivo = ARCHIVOS_FUENTE.get(clave)
        if self._disponible and archivo:
            ruta = os.path.join(self.ruta, archivo)
            if os.path.exists(ruta):
                from fontTools.ttLib import TTFont
                tt = TTFont(ruta, lazy=True)
                cmap = tt.getBestCmap()
                hmtx = tt["hmtx"]
                upem = tt["head"].unitsPerEm
                anchos = {}
                for code, nombre in cmap.items():
                    try:
                        anchos[code] = hmtx[nombre][0] / upem
                    except KeyError:
                        continue
                datos = {"anchos": anchos, "fallback": 0.5}
                tt.close()
        self._cache[clave] = datos
        return datos

    @staticmethod
    def _peso_normalizado(peso: int) -> int:
        pesos = sorted({p for _, p in ARCHIVOS_FUENTE})
        return min(pesos, key=lambda p: abs(p - int(peso)))

    # -- API pública --------------------------------------------------------
    def ancho(self, texto: str, familia: str, tam: float, peso: int = 400,
              letter_spacing: float = 0.0) -> float:
        """Ancho de avance en unidades SVG (mm) de ``texto``."""
        met = self._metricas(familia, peso)
        if not met:
            # aproximación conservadora si fontTools no está disponible
            return len(texto) * tam * 0.52 + max(0, len(texto) - 1) * letter_spacing
        anchos = met["anchos"]
        fb = met["fallback"]
        total = sum(anchos.get(ord(c), fb) for c in texto)
        return total * tam + max(0, len(texto) - 1) * letter_spacing

    def ajustar_lineas(self, texto: str, ancho_max: float, familia: str,
                       tam: float, peso: int = 400) -> List[str]:
        """Reparte ``texto`` en líneas que caben en ``ancho_max``."""
        palabras = texto.split()
        lineas: List[str] = []
        actual = ""
        for palabra in palabras:
            tentativa = f"{actual} {palabra}".strip()
            if actual and self.ancho(tentativa, familia, tam, peso) > ancho_max:
                lineas.append(actual)
                actual = palabra
            else:
                actual = tentativa
        if actual:
            lineas.append(actual)
        return lineas or [""]


MEDIDOR = MedidorTexto()


# ---------------------------------------------------------------------------
# 3. MODELO DE DATOS
# ---------------------------------------------------------------------------

@dataclass
class Run:
    """Una línea (``<tspan>``) dentro de un objeto de texto."""
    texto: str
    x: float
    y: float
    familia: str = SANS
    tam: float = 2.82
    peso: int = 400
    estilo: str = "normal"
    color: str = PRIMARY_BLUE
    anchor: Optional[str] = None
    letter_spacing: float = 0.0

    def ancho(self) -> float:
        return MEDIDOR.ancho(self.texto, self.familia, self.tam, self.peso,
                             self.letter_spacing)

    def x_izq(self) -> float:
        a = self.anchor or "start"
        if a == "middle":
            return self.x - self.ancho() / 2.0
        if a == "end":
            return self.x - self.ancho()
        return self.x

    def x_der(self) -> float:
        return self.x_izq() + self.ancho()


@dataclass
class ElementoTexto:
    id: str
    role: str
    runs: List[Run]
    familia: str = SANS
    tam: float = 2.82
    peso: int = 400
    estilo: str = "normal"
    color: str = PRIMARY_BLUE
    anchor: Optional[str] = None
    letter_spacing: float = 0.0
    matriz: str = ""
    grupo: str = "cuerpo"
    bbox: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

    # -- transformaciones editoriales --------------------------------------
    def mover(self, dx: float = 0.0, dy: float = 0.0) -> "ElementoTexto":
        for r in self.runs:
            r.x += dx
            r.y += dy
        x, y, w, h = self.bbox
        self.bbox = (x + dx, y + dy, w, h)
        return self

    def escalar(self, factor: float, cx: float, cy: float) -> "ElementoTexto":
        for r in self.runs:
            r.x = cx + (r.x - cx) * factor
            r.y = cy + (r.y - cy) * factor
            r.tam = round(r.tam * factor, 3)
        self.tam = round(self.tam * factor, 3)
        return self

    def fijar_tam(self, tam: float) -> "ElementoTexto":
        self.tam = tam
        for r in self.runs:
            r.tam = tam
        return self

    def escalar_tam(self, factor: float) -> "ElementoTexto":
        return self.fijar_tam(round(self.tam * factor, 3))

    def comprimir_interlineado(self, factor: float) -> "ElementoTexto":
        """Reduce el interlineado conservando la primera línea de base."""
        if len(self.runs) < 2:
            return self
        y0 = self.runs[0].y
        for r in self.runs[1:]:
            r.y = round(y0 + (r.y - y0) * factor, 4)
        return self

    def texto_plano(self) -> str:
        return " ".join(r.texto for r in self.runs).strip()

    def y_min(self) -> float:
        return min(r.y for r in self.runs) - self.tam
    def y_max(self) -> float:
        return max(r.y for r in self.runs)
    def x_min(self) -> float:
        return min(r.x_izq() for r in self.runs)
    def x_max(self) -> float:
        return max(r.x_der() for r in self.runs)


@dataclass
class ElementoVector:
    id: str
    tipo: str
    geom: Dict[str, str]
    estilo: Dict[str, str]
    matriz: str = ""
    grupo: str = "cuerpo"
    bbox: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

    # -- transformaciones ---------------------------------------------------
    def mover(self, dx: float = 0.0, dy: float = 0.0) -> "ElementoVector":
        g = self.geom
        if self.tipo == "rect":
            g["x"] = _num(g.get("x", 0)) + dx
            g["y"] = _num(g.get("y", 0)) + dy
        elif self.tipo == "circle":
            g["cx"] = _num(g.get("cx", 0)) + dx
            g["cy"] = _num(g.get("cy", 0)) + dy
        elif self.tipo == "line":
            g["x1"] = _num(g.get("x1", 0)) + dx
            g["x2"] = _num(g.get("x2", 0)) + dx
            g["y1"] = _num(g.get("y1", 0)) + dy
            g["y2"] = _num(g.get("y2", 0)) + dy
        elif self.tipo == "path":
            self.matriz = _componer_traslacion(self.matriz, dx, dy)
        x, y, w, h = self.bbox
        self.bbox = (x + dx, y + dy, w, h)
        return self

    def escalar(self, factor: float, cx: float, cy: float) -> "ElementoVector":
        g = self.geom
        if self.tipo == "rect":
            g["x"] = cx + (_num(g.get("x", 0)) - cx) * factor
            g["y"] = cy + (_num(g.get("y", 0)) - cy) * factor
            g["width"] = _num(g.get("width", 0)) * factor
            g["height"] = _num(g.get("height", 0)) * factor
            for k in ("rx", "ry"):
                if k in g:
                    g[k] = _num(g[k]) * factor
        elif self.tipo == "circle":
            g["cx"] = cx + (_num(g.get("cx", 0)) - cx) * factor
            g["cy"] = cy + (_num(g.get("cy", 0)) - cy) * factor
            g["r"] = _num(g.get("r", 0)) * factor
        elif self.tipo == "line":
            g["x1"] = cx + (_num(g.get("x1", 0)) - cx) * factor
            g["x2"] = cx + (_num(g.get("x2", 0)) - cx) * factor
            g["y1"] = cy + (_num(g.get("y1", 0)) - cy) * factor
            g["y2"] = cy + (_num(g.get("y2", 0)) - cy) * factor
        elif self.tipo == "path":
            self.matriz = _componer_escala(self.matriz, factor, cx, cy)
        x, y, w, h = self.bbox
        self.bbox = (cx + (x - cx) * factor, cy + (y - cy) * factor,
                     w * factor, h * factor)
        return self

    def alto(self, valor: float) -> "ElementoVector":
        if self.tipo == "rect":
            self.geom["height"] = valor
            x, y, w, _h = self.bbox
            self.bbox = (x, y, w, valor)
        return self

    def y_min(self) -> float:
        return self.bbox[1]
    def y_max(self) -> float:
        return self.bbox[1] + self.bbox[3]
    def x_min(self) -> float:
        return self.bbox[0]
    def x_max(self) -> float:
        return self.bbox[0] + self.bbox[2]


@dataclass
class Pagina:
    numero: int
    tipo: str = "STANDARD"
    master: str = "MASTER_PAGE_STANDARD_ODD"
    descripcion: str = ""
    vectores: List[ElementoVector] = field(default_factory=list)
    textos: List[ElementoTexto] = field(default_factory=list)
    contenido: Dict[str, object] = field(default_factory=dict)  # bloques TEXT_CONTENT

    # -- selectores ---------------------------------------------------------
    def texto(self, id_: str) -> Optional[ElementoTexto]:
        for t in self.textos:
            if t.id == id_:
                return t
        return None

    def textos_por_grupo(self, *grupos: str) -> List[ElementoTexto]:
        return [t for t in self.textos if t.grupo in grupos]

    def vectores_por_grupo(self, *grupos: str) -> List[ElementoVector]:
        return [v for v in self.vectores if v.grupo in grupos]

    def textos_bajo(self, y: float) -> List[ElementoTexto]:
        return [t for t in self.textos if t.runs and t.y_max() >= y]

    def textos_entre(self, y0: float, y1: float) -> List[ElementoTexto]:
        return [t for t in self.textos
                if t.runs and y0 <= min(r.y for r in t.runs) <= y1]

    def vectores_entre(self, y0: float, y1: float) -> List[ElementoVector]:
        return [v for v in self.vectores if y0 <= v.bbox[1] <= y1]

    def objetos_entre(self, y0: float, y1: float) -> List[object]:
        return list(self.textos_entre(y0, y1)) + list(self.vectores_entre(y0, y1))

    def mover_zona(self, y0: float, y1: float, dy: float,
                   excluir_grupos: Sequence[str] = ("pie", "fondo", "encabezado")) -> int:
        """Desplaza verticalmente todo objeto cuyo origen esté en [y0, y1]."""
        n = 0
        for obj in self.objetos_entre(y0, y1):
            if getattr(obj, "grupo", "") in excluir_grupos:
                continue
            obj.mover(0, dy)
            n += 1
        return n


# ---------------------------------------------------------------------------
# 4. UTILIDADES GEOMÉTRICAS
# ---------------------------------------------------------------------------

def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _fmt(v: float, dec: int = 4) -> str:
    """Formatea un número para el SVG sin ceros ni notación científica sobrante."""
    if isinstance(v, str):
        return v
    if abs(v) < 1e-9:
        return "0"
    s = f"{v:.{dec}f}".rstrip("0").rstrip(".")
    return s or "0"


def _parse_matriz(m: str) -> List[float]:
    nums = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", m or "")
    if len(nums) != 6:
        return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    return [float(n) for n in nums]


def _matriz_str(m: Sequence[float]) -> str:
    if [round(x, 6) for x in m] == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]:
        return ""
    return "matrix(" + " ".join(_fmt(x, 6) for x in m) + ")"


def _componer_traslacion(m: str, dx: float, dy: float) -> str:
    a, b, c, d, e, f = _parse_matriz(m)
    return _matriz_str([a, b, c, d, e + dx, f + dy])


def _componer_escala(m: str, k: float, cx: float, cy: float) -> str:
    a, b, c, d, e, f = _parse_matriz(m)
    return _matriz_str([k * a, k * b, k * c, k * d,
                        k * e + cx * (1 - k), k * f + cy * (1 - k)])


def _escape(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _bbox_path(d: str, matriz: str) -> Tuple[float, float, float, float]:
    """BBox aproximada de un path a partir de sus coordenadas absolutas."""
    a, b, c, dd, e, f = _parse_matriz(matriz)
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d or "")
    xs: List[float] = []
    ys: List[float] = []
    cmd = "M"
    cx = cy = 0.0
    i = 0
    def num():
        nonlocal i
        while i < len(tokens) and re.match(r"^[A-Za-z]$", tokens[i]):
            i += 1
        if i >= len(tokens):
            return 0.0
        v = float(tokens[i]); i += 1
        return v
    while i < len(tokens):
        tk = tokens[i]
        if re.match(r"^[A-Za-z]$", tk):
            cmd = tk; i += 1
            if cmd in "Zz":
                continue
        rel = cmd.islower()
        up = cmd.upper()
        if up == "H":
            v = num(); cx = cx + v if rel else v
        elif up == "V":
            v = num(); cy = cy + v if rel else v
        elif up in ("M", "L", "T"):
            x = num(); y = num()
            cx = cx + x if rel else x
            cy = cy + y if rel else y
        elif up in ("C",):
            pts = [num() for _ in range(6)]
            cx = cx + pts[4] if rel else pts[4]
            cy = cy + pts[5] if rel else pts[5]
        elif up in ("S", "Q"):
            pts = [num() for _ in range(4)]
            cx = cx + pts[2] if rel else pts[2]
            cy = cy + pts[3] if rel else pts[3]
        elif up == "A":
            pts = [num() for _ in range(7)]
            cx = cx + pts[5] if rel else pts[5]
            cy = cy + pts[6] if rel else pts[6]
        else:
            i += 1
            continue
        xs.append(cx); ys.append(cy)
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    px = [a * x + c * y + e for x, y in zip(xs, ys)]
    py = [b * x + dd * y + f for x, y in zip(xs, ys)]
    return (min(px), min(py), max(px) - min(px), max(py) - min(py))


# ---------------------------------------------------------------------------
# 5. PARSER DE LA ESPECIFICACIÓN EDITORIAL (fuente principal)
# ---------------------------------------------------------------------------

_RE_CAMPO = re.compile(r"^([A-Z_0-9]+):\s*(.*?)\s*$")
_RE_BACKTICK = re.compile(r"^`(.*)`$", re.S)


def _campos(bloque: str) -> Dict[str, str]:
    """Extrae los pares ``CLAVE: valor`` de un bloque, ignorando los fences."""
    datos: Dict[str, str] = {}
    dentro_fence = False
    for linea in bloque.split("\n"):
        if linea.strip().startswith("```"):
            dentro_fence = not dentro_fence
            continue
        if dentro_fence or linea.startswith(" ") or linea.startswith("-"):
            continue
        m = _RE_CAMPO.match(linea.rstrip())
        if m:
            valor = m.group(2).strip()
            mb = _RE_BACKTICK.match(valor)
            datos[m.group(1)] = mb.group(1) if mb else valor
    return datos


def _fence(bloque: str, clave: str, lang: str = "text") -> Optional[str]:
    m = re.search(rf"^{clave}:\n```{lang}\n(.*?)\n```", bloque, re.S | re.M)
    return m.group(1) if m else None


def _bbox(valor: str) -> Tuple[float, float, float, float]:
    d = dict(re.findall(r"(\w+)=(-?[\d.eE+-]+)", valor or ""))
    return (_num(d.get("x")), _num(d.get("y")),
            _num(d.get("width")), _num(d.get("height")))


def _grupo(valor: str) -> str:
    """Último id de grupo de origen, normalizado a nombre semántico."""
    partes = [p.strip() for p in (valor or "").split(">") if p.strip()]
    if not partes:
        return "cuerpo"
    ultimo = partes[-1]
    if ultimo.startswith("layer"):
        return "cuerpo"
    m = re.match(r"^p\d+_(.+)$", ultimo)
    return (m.group(1) if m else ultimo).lower()


def _familia(valor: str) -> str:
    fam = (valor or "").strip().strip("'\"")
    # NORMALIZACIÓN OBLIGATORIA: ninguna tercera familia sobrevive.
    if "serif" in fam.lower() or "garamond" in fam.lower():
        return SERIF
    return SANS


def _peso(valor: Optional[str]) -> int:
    if not valor:
        return 400
    v = valor.strip().lower()
    tabla = {"normal": 400, "bold": 700, "semibold": 600, "medium": 500}
    if v in tabla:
        return tabla[v]
    try:
        return int(float(v))
    except ValueError:
        return 400


def _tam(valor: Optional[str]) -> float:
    if not valor:
        return 2.82
    return _num(re.sub(r"[^\d.eE+-]", "", valor))


def _estilo_vector(valor: str) -> Dict[str, str]:
    est: Dict[str, str] = {}
    for par in (valor or "").split(";"):
        if "=" in par:
            k, v = par.split("=", 1)
            est[k.strip()] = v.strip()
    return est


def _geom_yaml(bloque: str) -> Dict[str, str]:
    txt = _fence(bloque, "SOURCE_GEOMETRY", "yaml") or ""
    geom: Dict[str, str] = {}
    for linea in txt.split("\n"):
        if ":" in linea:
            k, v = linea.split(":", 1)
            geom[k.strip()] = v.strip()
    return geom


_RE_RUN = re.compile(
    r"-\s+RUN_\d+:\s*TEXT=`(?P<texto>.*?)`;\s*ATTRS=`(?P<attrs>.*?)`;"
    r"\s*STYLE=`(?P<style>.*?)`(?:;\s*MATRIX=`(?P<matrix>.*?)`)?\s*$",
    re.M,
)


def _parse_runs(bloque: str, base: ElementoTexto) -> List[Run]:
    runs: List[Run] = []
    for m in _RE_RUN.finditer(bloque):
        attrs = dict(re.findall(r"([\w-]+)\s*=\s*([^;]+)", m.group("attrs")))
        style = dict(re.findall(r"([\w-]+)\s*=\s*([^;]+)", m.group("style")))
        fam = _familia(style.get("font-family", base.familia))
        runs.append(Run(
            texto=m.group("texto"),
            x=_num(attrs.get("x", 0)),
            y=_num(attrs.get("y", 0)),
            familia=fam,
            tam=_tam(style.get("font-size")) or base.tam,
            peso=_peso(style.get("font-weight")) if "font-weight" in style else base.peso,
            estilo=base.estilo,
            color=(style.get("fill") or base.color).strip(),
            anchor=(style.get("text-anchor") or base.anchor or None),
            letter_spacing=base.letter_spacing,
        ))
    return runs


def _es_traslacion(m: Sequence[float]) -> bool:
    return (abs(m[0] - 1) < 1e-9 and abs(m[1]) < 1e-9
            and abs(m[2]) < 1e-9 and abs(m[3] - 1) < 1e-9)


def _normalizar_texto_local(el: ElementoTexto) -> ElementoTexto:
    """Lleva el objeto a coordenadas locales de página.

    Varias páginas del SVG de avance conservan coordenadas del lienzo global
    (p. ej. PAGE_03 y PAGE_04); ``LOCAL_MATRIX`` es la traslación que las
    devuelve al viewBox ``0 0 210 297``. Se hornea en las coordenadas para que
    el modelo sea siempre local y editable sin transformaciones anidadas.
    """
    m = _parse_matriz(el.matriz)
    if _es_traslacion(m):
        dx, dy = m[4], m[5]
        if dx or dy:
            for r in el.runs:
                r.x += dx
                r.y += dy
        el.matriz = ""
    return el


def _normalizar_vector_local(el: ElementoVector) -> ElementoVector:
    """Idéntico criterio para la geometría: traslaciones horneadas."""
    m = _parse_matriz(el.matriz)
    if _es_traslacion(m) and el.tipo != "path":
        dx, dy = m[4], m[5]
        if dx or dy:
            g = el.geom
            for k in ("x", "cx", "x1", "x2"):
                if k in g:
                    g[k] = _num(g[k]) + dx
            for k in ("y", "cy", "y1", "y2"):
                if k in g:
                    g[k] = _num(g[k]) + dy
        el.matriz = ""
    return el


def _parse_texto(bloque: str) -> Optional[ElementoTexto]:
    c = _campos(bloque)
    exacto = _fence(bloque, "TEXT_EXACT")
    if exacto is None:
        return None
    familia = _familia(c.get("FONT_FAMILY", ""))
    el = ElementoTexto(
        id=c.get("ID", "texto"),
        role=c.get("ROLE", "BODY_TEXT"),
        runs=[],
        familia=familia,
        tam=_tam(c.get("FONT_SIZE")),
        peso=_peso(c.get("FONT_WEIGHT")),
        estilo=(c.get("FONT_STYLE") or "normal").strip(),
        color=(c.get("COLOR") or PRIMARY_BLUE).strip(),
        anchor=c.get("TEXT_ANCHOR"),
        letter_spacing=_num(c.get("LETTER_SPACING", 0)),
        matriz=c.get("LOCAL_MATRIX", ""),
        grupo=_grupo(c.get("SOURCE_PARENT_GROUP_IDS", "")),
        bbox=_bbox(c.get("BBOX_LOCAL_MM", "")),
    )
    runs = _parse_runs(bloque, el)
    if not runs:
        attrs = dict(re.findall(r"([\w-]+)\s*=\s*([^;]+)",
                                c.get("SOURCE_TEXT_ATTRIBUTES", "")))
        runs = [Run(
            texto=exacto.strip(),
            x=_num(attrs.get("x", el.bbox[0])),
            y=_num(attrs.get("y", el.bbox[1] + el.tam)),
            familia=el.familia, tam=el.tam, peso=el.peso, estilo=el.estilo,
            color=el.color, anchor=el.anchor, letter_spacing=el.letter_spacing,
        )]
    for r in runs:
        r.estilo = el.estilo
        r.letter_spacing = el.letter_spacing
    el.runs = runs
    return el


def _parse_vector(bloque: str) -> Optional[ElementoVector]:
    c = _campos(bloque)
    tipo = (c.get("TYPE") or "").strip()
    if tipo not in ("rect", "circle", "line", "path"):
        return None
    geom = _geom_yaml(bloque)
    matriz = c.get("LOCAL_MATRIX", "")
    bbox = _bbox(c.get("BBOX_LOCAL_MM", ""))
    return ElementoVector(
        id=c.get("ID", "vector"),
        tipo=tipo,
        geom=geom,
        estilo=_estilo_vector(c.get("EFFECTIVE_STYLE", "")),
        matriz=matriz,
        grupo=_grupo(c.get("SOURCE_PARENT_GROUP_IDS", "")),
        bbox=bbox,
    )


def _parse_contenido(seccion: str) -> Dict[str, object]:
    """Bloques ``### NOMBRE`` con fences ``text`` (usado por PAGE_23)."""
    out: Dict[str, object] = {}
    m = re.search(r"^## TEXT_CONTENT[^\n]*\n(.*?)(?=\n## |\Z)", seccion, re.S | re.M)
    if not m:
        return out
    for bloque in re.split(r"\n(?=### )", m.group(1)):
        mb = re.match(r"### ([A-Z0-9_]+)\s*\n(.*)$", bloque.strip(), re.S)
        if not mb:
            continue
        nombre, cuerpo = mb.group(1), mb.group(2)
        sub = re.findall(r"^(TITLE|BODY):\n```text\n(.*?)\n```", cuerpo, re.S | re.M)
        if sub:
            out[nombre] = {k.lower(): v for k, v in sub}
        else:
            mt = re.search(r"```text\n(.*?)\n```", cuerpo, re.S)
            if mt:
                out[nombre] = mt.group(1)
    return out


def parse_especificacion(ruta: str = SPEC_MD) -> Dict[int, Pagina]:
    """Lee la especificación editorial corregida y devuelve las 30 páginas."""
    with open(ruta, encoding="utf-8") as fh:
        raw = fh.read()

    secciones = re.split(r"\n(?=# PAGE_\d+)", raw)
    paginas: Dict[int, Pagina] = {}
    for sec in secciones:
        mp = re.match(r"# PAGE_(\d+)", sec)
        if not mp:
            continue
        numero = int(mp.group(1))
        meta = _campos(sec.split("## COMPOSITION_DESCRIPTION")[0])
        desc = ""
        md = re.search(r"^## COMPOSITION_DESCRIPTION\n\n(.*?)\n\n", sec, re.S | re.M)
        if md:
            desc = " ".join(md.group(1).split())
        pag = Pagina(
            numero=numero,
            tipo=meta.get("PAGE_TYPE", "STANDARD"),
            master=meta.get("MASTER_PAGE", "MASTER_PAGE_STANDARD_ODD"),
            descripcion=desc,
            contenido=_parse_contenido(sec),
        )
        m_txt = re.search(r"^## TEXT_ELEMENTS[^\n]*\n(.*?)(?=\n## |\Z)", sec, re.S | re.M)
        if m_txt:
            for bloque in re.split(r"\n(?=### TEXT_ELEMENT_)", m_txt.group(1)):
                if not bloque.lstrip().startswith("### TEXT_ELEMENT_"):
                    continue
                el = _parse_texto(bloque)
                if el:
                    pag.textos.append(_normalizar_texto_local(el))
        m_vec = re.search(r"^## VECTOR_ELEMENTS[^\n]*\n(.*?)(?=\n## |\Z)", sec, re.S | re.M)
        if m_vec:
            for bloque in re.split(r"\n(?=### VECTOR_ELEMENT_)", m_vec.group(1)):
                if not bloque.lstrip().startswith("### VECTOR_ELEMENT_"):
                    continue
                el = _parse_vector(bloque)
                if el:
                    _normalizar_vector_local(el)
                    if el.tipo == "path" and el.bbox[2] == 0 and el.bbox[3] == 0:
                        el.bbox = _bbox_path(el.geom.get("d", ""), el.matriz)
                    pag.vectores.append(el)
        paginas[numero] = pag
    return paginas


# ---------------------------------------------------------------------------
# 5-bis. DEPURACIÓN DE TEXTO CONVERTIDO A CURVAS
#     El SVG de avance arrastra duplicados del wordmark institucional y del
#     subtítulo de portada dibujados como contornos. La regla de editabilidad
#     prohíbe texto en curvas, y la política de normalización obliga a eliminar
#     objetos residuales o duplicados: aquí se separan del dibujo legítimo.
# ---------------------------------------------------------------------------

_TOKENS_PATH = re.compile(
    r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
_ARIDAD = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2,
           "A": 7, "Z": 0}


def subpaths_absolutos(d: str) -> List[Tuple[List, Tuple[float, float, float, float]]]:
    """Divide un `d` en subtrazos independientes con coordenadas absolutas."""
    toks = _TOKENS_PATH.findall(d or "")
    i = 0
    cx = cy = sx = sy = 0.0
    cmd = None
    subs: List[List] = []
    cur: Optional[List] = None
    while i < len(toks):
        t = toks[i]
        if re.match(r"^[A-Za-z]$", t):
            cmd = t
            i += 1
        elif cmd is None:
            i += 1
            continue
        up = (cmd or "M").upper()
        rel = (cmd or "M").islower()
        if up == "Z":
            if cur is not None:
                cur.append(("Z", []))
            cx, cy = sx, sy
            continue
        n = _ARIDAD[up]
        vals: List[float] = []
        for _ in range(n):
            if i >= len(toks) or re.match(r"^[A-Za-z]$", toks[i]):
                break
            vals.append(float(toks[i]))
            i += 1
        if len(vals) < n:
            break
        if up == "M":
            x, y = (cx + vals[0], cy + vals[1]) if rel else (vals[0], vals[1])
            cur = [("M", [x, y])]
            subs.append(cur)
            cx = sx = x
            cy = sy = y
            cmd = "l" if rel else "L"      # los pares siguientes son linetos
        elif up == "L":
            x, y = (cx + vals[0], cy + vals[1]) if rel else (vals[0], vals[1])
            cur.append(("L", [x, y])); cx, cy = x, y
        elif up == "H":
            x = cx + vals[0] if rel else vals[0]
            cur.append(("L", [x, cy])); cx = x
        elif up == "V":
            y = cy + vals[0] if rel else vals[0]
            cur.append(("L", [cx, y])); cy = y
        elif up in ("C", "S", "Q"):
            p = [(cx + v if k % 2 == 0 else cy + v) if rel else v
                 for k, v in enumerate(vals)]
            cur.append((up, p)); cx, cy = p[-2], p[-1]
        elif up == "T":
            x, y = (cx + vals[0], cy + vals[1]) if rel else (vals[0], vals[1])
            cur.append(("T", [x, y])); cx, cy = x, y
        elif up == "A":
            x = cx + vals[5] if rel else vals[5]
            y = cy + vals[6] if rel else vals[6]
            cur.append(("A", vals[:5] + [x, y])); cx, cy = x, y
    salida = []
    for cmds in subs:
        xs: List[float] = []
        ys: List[float] = []
        for c, p in cmds:
            inicio = 5 if c == "A" else 0
            for k in range(inicio, len(p) - 1, 2):
                xs.append(p[k]); ys.append(p[k + 1])
        if xs:
            salida.append((cmds, (min(xs), min(ys), max(xs), max(ys))))
    return salida


def serializar_subpaths(subs: Sequence) -> str:
    partes = []
    for cmds, _ in subs:
        for c, p in cmds:
            partes.append("Z" if c == "Z"
                          else c + " " + ",".join(_fmt(v) for v in p))
    return " ".join(partes)


def _cluster_de_glifos(subs: Sequence) -> set:
    """Índices de subtrazos que forman una línea de texto vectorizado.

    Firma reconocible: muchos contornos pequeños alineados sobre una misma
    línea de base, contiguos horizontalmente y cubriendo un tramo largo.
    """
    por_base: Dict[float, List[int]] = {}
    cajas = {}
    for idx, (_, b) in enumerate(subs):
        alto, ancho = b[3] - b[1], b[2] - b[0]
        if 0.15 <= alto <= 5.0 and 0.1 <= ancho <= 8.0:
            por_base.setdefault(round(b[3], 1), []).append(idx)
            cajas[idx] = b
    fuera: set = set()
    for _, idxs in por_base.items():
        if len(idxs) < 7:
            continue
        bs = [cajas[i] for i in idxs]
        tramo = max(b[2] for b in bs) - min(b[0] for b in bs)
        if tramo < 20.0:
            continue
        xs = sorted(b[0] for b in bs)
        huecos = sorted(xs[i + 1] - xs[i] for i in range(len(xs) - 1))
        if huecos[len(huecos) // 2] > 5.0:
            continue
        fuera.update(idxs)
    return fuera


def depurar_texto_en_curvas(pag: Pagina) -> int:
    """Quita del dibujo los contornos que duplican texto vivo.

    * Escudos de encabezado anchos: se conserva sólo el emblema (x ≤ 37 mm);
      el wordmark `USACH` / `FACULTAD DE INGENIERÍA` y el lema existen ya como
      `<text>` editable del maestro de identidad.
    * Resto de dibujos: se eliminan las líneas de glifos vectorizados.
    """
    quitados = 0
    for v in pag.vectores:
        if v.tipo != "path" or not v.geom.get("d"):
            continue
        subs = subpaths_absolutos(v.geom["d"])
        if not subs:
            continue
        es_escudo = v.bbox[1] < 40.0 and v.bbox[2] > 60.0
        if es_escudo:
            conservados = [s for s in subs if s[1][2] <= 37.0]
        else:
            fuera = _cluster_de_glifos(subs)
            conservados = [s for i, s in enumerate(subs) if i not in fuera]
        if len(conservados) == len(subs):
            continue
        quitados += len(subs) - len(conservados)
        v.geom["d"] = serializar_subpaths(conservados)
        v.matriz = ""      # ya está en coordenadas absolutas de página
        xs = [c[1] for c in conservados]
        v.bbox = (min(b[0] for b in xs), min(b[1] for b in xs),
                  max(b[2] for b in xs) - min(b[0] for b in xs),
                  max(b[3] for b in xs) - min(b[1] for b in xs))
    return quitados


# ---------------------------------------------------------------------------
# 6. EMISIÓN DE SVG — componentes reutilizables
# ---------------------------------------------------------------------------

def _estilo_texto(familia: str, tam: float, peso: int, color: str,
                  estilo: str = "normal", anchor: Optional[str] = None,
                  letter_spacing: float = 0.0) -> str:
    partes = [
        f"font-family:'{familia}'",
        f"font-size:{_fmt(tam, 3)}px",
        f"font-weight:{peso}",
        f"fill:{color}",
    ]
    if estilo and estilo != "normal":
        partes.append(f"font-style:{estilo}")
    if anchor:
        partes.append(f"text-anchor:{anchor}")
    if letter_spacing:
        partes.append(f"letter-spacing:{_fmt(letter_spacing, 3)}px")
    return ";".join(partes)


def svg_texto(el: ElementoTexto, prefijo: str, sangria: str = "      ") -> str:
    """Serializa un objeto de texto como ``<text>`` con ``<tspan>`` editables."""
    base = _estilo_texto(el.familia, el.tam, el.peso, el.color, el.estilo,
                         el.anchor, el.letter_spacing)
    attrs = [f'id="{prefijo}{el.id}"', f'style="{base}"']
    if el.matriz and _matriz_str(_parse_matriz(el.matriz)):
        attrs.append(f'transform="{_matriz_str(_parse_matriz(el.matriz))}"')
    if el.role:
        attrs.append(f'data-role="{el.role}"')
    # Los <tspan> se emiten sin espacio en blanco entre etiquetas: cualquier
    # nodo de texto intermedio se convertiría en un glifo espurio situado en
    # el origen del objeto (Inkscape lo hace visible en la caja de selección).
    out = [f"{sangria}<text {' '.join(attrs)}>"]
    for i, r in enumerate(el.runs, 1):
        dif = []
        if abs(r.tam - el.tam) > 1e-6:
            dif.append(f"font-size:{_fmt(r.tam, 3)}px")
        if r.peso != el.peso:
            dif.append(f"font-weight:{r.peso}")
        if r.familia != el.familia:
            dif.append(f"font-family:'{r.familia}'")
        if r.color != el.color:
            dif.append(f"fill:{r.color}")
        if (r.anchor or None) != (el.anchor or None):
            dif.append(f"text-anchor:{r.anchor or 'start'}")
        est = f' style="{";".join(dif)}"' if dif else ""
        out.append(
            f'<tspan id="{prefijo}{el.id}_l{i:02d}" '
            f'x="{_fmt(r.x)}" y="{_fmt(r.y)}"{est}>{_escape(r.texto)}</tspan>'
        )
    out.append("</text>")
    return "".join(out)


def svg_vector(el: ElementoVector, prefijo: str, sangria: str = "      ") -> str:
    """Serializa geometría nativa (rect/circle/line/path) editable."""
    est = []
    for k in ("fill", "stroke", "stroke-width", "stroke-linecap",
              "stroke-linejoin", "stroke-dasharray", "opacity"):
        if k in el.estilo:
            est.append(f"{k}:{el.estilo[k]}")
    estilo = ";".join(est)
    g = el.geom
    if el.tipo == "rect":
        campos = ["x", "y", "width", "height", "rx", "ry"]
    elif el.tipo == "circle":
        campos = ["cx", "cy", "r"]
    elif el.tipo == "line":
        campos = ["x1", "y1", "x2", "y2"]
    else:
        campos = ["d"]
    attrs = [f'id="{prefijo}{el.id}"']
    for c in campos:
        if c in g and g[c] != "":
            v = g[c]
            attrs.append(f'{c}="{v if c == "d" else _fmt(_num(v))}"')
    if estilo:
        attrs.append(f'style="{estilo}"')
    m = _matriz_str(_parse_matriz(el.matriz))
    if m:
        attrs.append(f'transform="{m}"')
    return f"{sangria}<{el.tipo} {' '.join(attrs)} />"


def _agrupar_consecutivos(elementos: Iterable) -> List[Tuple[str, List]]:
    """Agrupa preservando el orden Z: bloques consecutivos con el mismo grupo."""
    bloques: List[Tuple[str, List]] = []
    for el in elementos:
        gr = getattr(el, "grupo", "cuerpo") or "cuerpo"
        if bloques and bloques[-1][0] == gr:
            bloques[-1][1].append(el)
        else:
            bloques.append((gr, [el]))
    return bloques


def svg_contenido_pagina(pag: Pagina, sangria: str = "    ") -> str:
    """Contenido de una página: vectores al fondo, textos siempre encima."""
    pref = f"p{pag.numero:02d}_"
    vistos: Dict[str, int] = {}

    def id_grupo(tipo: str, nombre: str) -> Tuple[str, str]:
        """Id único aunque un mismo grupo aparezca en varios tramos de la Z."""
        base = f"{pref}{tipo}_{_slug(nombre)}"
        vistos[base] = vistos.get(base, 0) + 1
        n = vistos[base]
        etiqueta = nombre if n == 1 else f"{nombre} ({n})"
        return (base if n == 1 else f"{base}_{n}"), etiqueta

    partes: List[str] = []
    if pag.vectores:
        partes.append(f'{sangria}<g id="{pref}vectores" '
                      f'inkscape:label="Vectores {pag.numero:02d}">')
        for gr, els in _agrupar_consecutivos(pag.vectores):
            gid, etiqueta = id_grupo("v", gr)
            partes.append(f'{sangria}  <g id="{gid}" '
                          f'inkscape:label="{etiqueta}">')
            for el in els:
                partes.append(svg_vector(el, pref, sangria + "    "))
            partes.append(f"{sangria}  </g>")
        partes.append(f"{sangria}</g>")
    if pag.textos:
        partes.append(f'{sangria}<g id="{pref}textos" '
                      f'inkscape:label="Textos {pag.numero:02d}">')
        for gr, els in _agrupar_consecutivos(pag.textos):
            gid, etiqueta = id_grupo("t", gr)
            partes.append(f'{sangria}  <g id="{gid}" '
                          f'inkscape:label="{etiqueta}">')
            for el in els:
                partes.append(svg_texto(el, pref, sangria + "    "))
            partes.append(f"{sangria}  </g>")
        partes.append(f"{sangria}</g>")
    return "\n".join(partes)


def _slug(nombre: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", nombre).strip("_").lower()
    return s or "grupo"


CABECERA_SVG = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Manual de Evaluación y Calificación del Desempeño Académico
     Facultad de Ingeniería · Universidad de Santiago de Chile
     Generado por generar_manual_svg.py — texto 100% editable, sin rasterizado. -->
<svg
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   version="1.1"
   width="{w}mm"
   height="{h}mm"
   viewBox="0 0 {w} {h}"
   id="manual_desempeno_final"
   sodipodi:docname="manual_desempeno_final.svg"
   inkscape:version="1.4">
  <defs id="defs_manual" />
  <sodipodi:namedview
     id="namedview_manual"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:document-units="mm"
     inkscape:pageopacity="0"
     inkscape:pagecheckerboard="0"
     inkscape:deskcolor="#d1d1d1"
     inkscape:showpageshadow="2"
     showgrid="false">
{paginas}
  </sodipodi:namedview>
"""


def construir_svg_multipagina(paginas: Dict[int, Pagina]) -> str:
    """Documento único con las 30 páginas A4 en secuencia editorial 01→30."""
    n = TOTAL_PAGINAS
    ancho_total = n * PAGE_W + (n - 1) * PAGE_GAP
    defs_pag = []
    cuerpo = []
    for i in range(1, n + 1):
        ox = (i - 1) * (PAGE_W + PAGE_GAP)
        defs_pag.append(
            f'    <inkscape:page x="{_fmt(ox)}" y="0" width="{_fmt(PAGE_W)}" '
            f'height="{_fmt(PAGE_H)}" id="page_{i:02d}" margin="0" bleed="0" />'
        )
        pag = paginas[i]
        cuerpo.append(
            f'  <g inkscape:groupmode="layer" inkscape:label="Página {i:02d}" '
            f'id="pagina_{i:02d}" transform="translate({_fmt(ox)},0)">'
        )
        cuerpo.append(svg_contenido_pagina(pag))
        cuerpo.append("  </g>")
    cab = CABECERA_SVG.format(w=_fmt(ancho_total), h=_fmt(PAGE_H),
                              paginas="\n".join(defs_pag))
    return cab + "\n".join(cuerpo) + "\n</svg>\n"


PLANTILLA_PAGINA = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:svg="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     version="1.1" width="210mm" height="297mm" viewBox="{vb}"
     id="pagina_{n:02d}">
  <rect x="0" y="0" width="210" height="297" style="fill:#ffffff;stroke:none"
        id="p{n:02d}_lienzo" />
{contenido}
</svg>
"""


def construir_svg_pagina(pag: Pagina) -> str:
    """SVG independiente de una página (usado para render y control visual)."""
    return PLANTILLA_PAGINA.format(vb=VIEWBOX_PAGINA, n=pag.numero,
                                   contenido=svg_contenido_pagina(pag))


# ---------------------------------------------------------------------------
# 7. VALIDACIÓN AUTOMÁTICA DE COMPOSICIÓN
#    Detecta desbordes laterales, invasión del pie y solapamientos de texto.
# ---------------------------------------------------------------------------

TOL_LATERAL = 0.6     # mm de tolerancia óptica
TOL_PIE = 0.6
GRUPOS_PIE = {"pie", "footer", "pie_pagina", "folio"}
ROLES_PIE = {"PAGE_NUMBER", "FOOTER_LOCATION_YEAR", "FOOTER_TEXT",
             "FOOTER_RULE", "FOOTER"}
GRUPOS_EXENTOS_LATERAL = {"fondo", "background"}
GRUPOS_ENCABEZADO = {"encabezado", "header"}
ROLES_ENCABEZADO = {"HEADER_IDENTITY", "HEADER_A", "HEADER_B"}
# El maestro par usa caja útil de 16–194 mm; el folio admite borde 190–195 mm.
LIMITE_DER_ENCABEZADO = 194.5
LIMITE_DER_FOLIO = 195.5
# Trazos decorativos claros de las ilustraciones: sangrado deliberado.
TRAZOS_DECORATIVOS = {"#bfd3eb", "#b5cce7", "#ddeaf8", "#dceaf8", "#d8e7f7",
                      "#bfd7f0", "#eef5fc", "#e8f2fc"}


def _es_pie(el) -> bool:
    """Un objeto pertenece al pie si su grupo o su rol editorial lo indican."""
    return (getattr(el, "grupo", "") in GRUPOS_PIE
            or getattr(el, "role", "") in ROLES_PIE)


def _es_fondo(v: "ElementoVector") -> bool:
    """Fondo de página o caja blanca auxiliar del encabezado."""
    if v.grupo in GRUPOS_EXENTOS_LATERAL:
        return True
    if v.tipo == "rect" and v.bbox[2] >= 200 and v.bbox[3] >= 285:
        return True
    return (v.tipo == "rect"
            and v.estilo.get("fill", "").lower() in ("#ffffff", "white")
            and v.estilo.get("stroke", "none") == "none")


GRUPOS_ILUSTRACION = {"ilustracion", "illustration", "figura", "grafico"}


def _es_decorativo(v: "ElementoVector") -> bool:
    """Trazo decorativo o ilustración con sangrado deliberado hacia el margen."""
    if v.estilo.get("stroke", "").lower() in TRAZOS_DECORATIVOS:
        return True
    if v.grupo in GRUPOS_ILUSTRACION:
        return True
    return v.tipo == "path" and v.bbox[2] > 120.0 and v.bbox[3] > 40.0


def _es_encabezado(el) -> bool:
    return (getattr(el, "grupo", "") in GRUPOS_ENCABEZADO
            or getattr(el, "role", "") in ROLES_ENCABEZADO)


def _limite_derecho(el) -> float:
    if getattr(el, "role", "") == "PAGE_NUMBER":
        return LIMITE_DER_FOLIO
    if _es_encabezado(el):
        return LIMITE_DER_ENCABEZADO
    return MARGEN_DER


def _es_filete_pie(v: "ElementoVector") -> bool:
    """Filete horizontal del pie: línea fina en la banda 276–294 mm."""
    if v.tipo not in ("line", "rect"):
        return False
    return v.bbox[3] <= 1.0 and 274.0 <= v.bbox[1] <= 294.0


@dataclass
class Hallazgo:
    pagina: int
    tipo: str
    objeto: str
    detalle: str

    def __str__(self) -> str:
        return f"P{self.pagina:02d}  {self.tipo:<14} {self.objeto:<28} {self.detalle}"


def _cajas_linea(el: ElementoTexto) -> List[Tuple[float, float, float, float, str]]:
    cajas = []
    for r in el.runs:
        if not r.texto.strip():
            continue
        w = r.ancho()
        # caja óptica real: altura de mayúscula sobre la línea de base y
        # descendente por debajo; evita falsos positivos por interlineado justo.
        cajas.append((r.x_izq(), r.y - r.tam * 0.71, w, r.tam * 0.94, r.texto))
    return cajas


def _solapan(a, b, min_area: float) -> float:
    ax, ay, aw, ah, _ = a
    bx, by, bw, bh, _ = b
    ix = min(ax + aw, bx + bw) - max(ax, bx)
    iy = min(ay + ah, by + bh) - max(ay, by)
    if ix <= 0 or iy <= 0:
        return 0.0
    area = ix * iy
    return area if area >= min_area else 0.0


def auditar(paginas: Dict[int, Pagina]) -> List[Hallazgo]:
    """Informe de composición sobre el modelo ya corregido."""
    hallazgos: List[Hallazgo] = []
    for n in sorted(paginas):
        pag = paginas[n]
        limite_pie = _limite_cuerpo(pag)
        cajas_pagina: List[Tuple[tuple, ElementoTexto]] = []
        for el in pag.textos:
            if el.familia not in FAMILIAS_PERMITIDAS:
                hallazgos.append(Hallazgo(n, "TIPOGRAFIA", el.id,
                                          f"familia no permitida: {el.familia}"))
            for r in el.runs:
                if not r.texto.strip():
                    continue
                xd = r.x_der()
                xi = r.x_izq()
                limite = _limite_derecho(el)
                if el.grupo not in GRUPOS_EXENTOS_LATERAL:
                    if xd > limite + TOL_LATERAL:
                        hallazgos.append(Hallazgo(
                            n, "DESBORDE_DER", el.id,
                            f"x_der={xd:.1f} > {limite} · «{r.texto[:38]}»"))
                    if xi < MARGEN_IZQ - 4.0:
                        hallazgos.append(Hallazgo(
                            n, "DESBORDE_IZQ", el.id,
                            f"x_izq={xi:.1f} · «{r.texto[:38]}»"))
                if not _es_pie(el) and r.y > limite_pie + TOL_PIE:
                    hallazgos.append(Hallazgo(
                        n, "INVADE_PIE", el.id,
                        f"y={r.y:.1f} > {limite_pie:.1f} · «{r.texto[:38]}»"))
                if r.y - r.tam < 4.0:
                    hallazgos.append(Hallazgo(
                        n, "FUERA_ARRIBA", el.id, f"y={r.y:.1f}"))
            for caja in _cajas_linea(el):
                cajas_pagina.append((caja, el))
        # --- solapamientos entre objetos de texto distintos ---------------
        for i in range(len(cajas_pagina)):
            ca, ea = cajas_pagina[i]
            for j in range(i + 1, len(cajas_pagina)):
                cb, eb = cajas_pagina[j]
                if ea is eb:
                    continue
                area = _solapan(ca, cb, 2.5)
                if area:
                    hallazgos.append(Hallazgo(
                        n, "SOLAPE", f"{ea.id}/{eb.id}",
                        f"{area:.1f}mm² · «{ca[4][:22]}» vs «{cb[4][:22]}»"))
        # --- filetes horizontales que cruzan texto ------------------------
        filetes = [v for v in pag.vectores
                   if v.tipo in ("line", "rect") and v.bbox[3] <= 1.2
                   and v.bbox[2] >= 20.0 and not _es_fondo(v)]
        opacos = [v for v in pag.vectores
                  if v.estilo.get("fill", "none") not in ("none", "")
                  and not _es_fondo(v) and v.bbox[2] < 60.0]
        for v in filetes:
            yv = v.bbox[1] + v.bbox[3] / 2.0
            for caja, el in cajas_pagina:
                x, y, w, h, texto = caja
                if not (y + 0.15 < yv < y + h - 0.15):
                    continue
                solape = min(x + w, v.x_max()) - max(x, v.x_min())
                if solape <= 0.45 * w:
                    continue
                # un nodo opaco (círculo/rect de un diagrama) puede tapar el
                # conector: en ese caso el cruce es intencionado
                if any(o.x_min() <= x and o.x_max() >= x + w
                       and o.y_min() <= yv <= o.y_max() for o in opacos):
                    continue
                if True:
                    hallazgos.append(Hallazgo(
                        n, "FILETE_CRUZA", f"{v.id}/{el.id}",
                        f"y={yv:.1f} atraviesa «{texto[:30]}»"))
                    break

        # --- vectores fuera de caja ---------------------------------------
        for v in pag.vectores:
            if (_es_fondo(v) or _es_pie(v) or _es_filete_pie(v)
                    or _es_decorativo(v) or _es_encabezado(v)):
                continue
            if v.bbox[2] <= 0 and v.bbox[3] <= 0:
                continue
            if v.y_max() > limite_pie + 1.5 and v.y_min() < 290:
                hallazgos.append(Hallazgo(
                    n, "VECTOR_PIE", v.id,
                    f"y_max={v.y_max():.1f} invade zona de pie"))
            if v.x_max() > MARGEN_DER + 2.5 and v.x_min() > 1:
                hallazgos.append(Hallazgo(
                    n, "VECTOR_DER", v.id, f"x_max={v.x_max():.1f}"))
    return hallazgos


def resumen_auditoria(hallazgos: Sequence[Hallazgo]) -> str:
    if not hallazgos:
        return "Sin hallazgos: composición dentro de márgenes y zonas seguras."
    por_tipo: Dict[str, int] = {}
    for h in hallazgos:
        por_tipo[h.tipo] = por_tipo.get(h.tipo, 0) + 1
    lineas = [f"{len(hallazgos)} hallazgos:"]
    for t, c in sorted(por_tipo.items(), key=lambda kv: -kv[1]):
        lineas.append(f"  · {t}: {c}")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 8. OPERADORES EDITORIALES REUTILIZABLES
#    Vocabulario común con el que se expresan los CORRECTION_OVERRIDE.
# ---------------------------------------------------------------------------

def objetos_de_grupo(pag: Pagina, *grupos: str) -> List:
    return [o for o in list(pag.vectores) + list(pag.textos) if o.grupo in grupos]


def objetos_por_id(pag: Pagina, *ids: str) -> List:
    conjunto = set(ids)
    return [o for o in list(pag.vectores) + list(pag.textos) if o.id in conjunto]


def mover(objetos: Iterable, dx: float = 0.0, dy: float = 0.0) -> int:
    n = 0
    for o in objetos:
        o.mover(dx, dy)
        n += 1
    return n


def _y_origen(o) -> float:
    """Ordenada de referencia de un objeto (primera línea de base o borde)."""
    if isinstance(o, ElementoTexto):
        return min(r.y for r in o.runs) if o.runs else 0.0
    return o.bbox[1]


def objetos_en_banda(pag: Pagina, y0: float, y1: float,
                     incluir_pie: bool = False) -> List:
    """Todos los objetos cuyo origen vertical cae en la banda [y0, y1]."""
    sel = []
    for o in list(pag.vectores) + list(pag.textos):
        if not incluir_pie and (_es_pie(o) or o.grupo in GRUPOS_EXENTOS_LATERAL):
            continue
        if y0 <= _y_origen(o) <= y1:
            sel.append(o)
    return sel


def bbox_objetos(objetos: Sequence) -> Tuple[float, float, float, float]:
    """Caja envolvente (x0, y0, x1, y1) de un conjunto heterogéneo."""
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for o in objetos:
        if isinstance(o, ElementoTexto):
            if not any(r.texto.strip() for r in o.runs):
                continue
            ax0, ax1 = o.x_min(), o.x_max()
            ay0, ay1 = o.y_min(), o.y_max()
        else:
            ax0, ay0 = o.bbox[0], o.bbox[1]
            ax1, ay1 = ax0 + o.bbox[2], ay0 + o.bbox[3]
        x0, y0 = min(x0, ax0), min(y0, ay0)
        x1, y1 = max(x1, ax1), max(y1, ay1)
    if x0 > x1:
        return (0.0, 0.0, 0.0, 0.0)
    return (x0, y0, x1, y1)


def distribuir_fila(pag: Pagina, grupos: Sequence[str],
                    x_izq: float = MARGEN_IZQ, x_der: float = MARGEN_DER) -> None:
    """Redistribuye horizontalmente módulos de una fila dentro del ancho útil.

    Cada módulo se traslada como un bloque rígido (nunca se deforma), de modo
    que iconos y textos conservan su proporción. Se usa para las filas de
    tarjetas/pasos que en el SVG de avance desbordan los márgenes.
    """
    bloques = [(g, objetos_de_grupo(pag, g)) for g in grupos]
    bloques = [(g, objs) for g, objs in bloques if objs]
    if not bloques:
        return
    cajas = [bbox_objetos(objs) for _, objs in bloques]
    anchos = [c[2] - c[0] for c in cajas]
    disponible = x_der - x_izq
    medianil = (disponible - sum(anchos)) / max(1, len(bloques) - 1)
    x = x_izq
    for (_, objs), caja, ancho in zip(bloques, cajas, anchos):
        mover(objs, dx=x - caja[0])
        x += ancho + medianil


def elevar_bloque(pag: Pagina, y0: float, y1: float, dy: float,
                  holgura: float = 4.0) -> float:
    """Eleva un bloque hasta ``dy`` mm sin invadir lo que queda por encima.

    Los ``CORRECTION_OVERRIDE`` expresan la elevación «respecto de la versión
    conflictiva»; aquí se aplica el máximo posible conservando una separación
    mínima con el objeto anterior, de modo que despejar el pie nunca genere
    una colisión nueva más arriba.
    """
    bloque = objetos_en_banda(pag, y0, y1)
    if not bloque:
        return 0.0
    techo = min(_techo_optico(o) for o in bloque)
    ids = {id(o) for o in bloque}
    anteriores = [o for o in list(pag.vectores) + list(pag.textos)
                  if id(o) not in ids and not _es_fondo_o_pie(o)
                  and _fondo_optico(o) <= techo + 0.01]
    tope = max((_fondo_optico(o) for o in anteriores), default=0.0)
    margen = techo - (tope + holgura)
    real = min(abs(dy), max(0.0, margen))
    if real > 0.01:
        mover(bloque, dy=-real)
    return -real


def _techo_optico(o) -> float:
    if isinstance(o, ElementoTexto):
        return min(r.y - r.tam * 0.71 for r in o.runs) if o.runs else 0.0
    return o.bbox[1]


def _fondo_optico(o) -> float:
    if isinstance(o, ElementoTexto):
        return max(r.y + r.tam * 0.27 for r in o.runs) if o.runs else 0.0
    return o.bbox[1] + o.bbox[3]


def _es_fondo_o_pie(o) -> bool:
    if isinstance(o, ElementoVector):
        return _es_fondo(o) or _es_pie(o)
    return _es_pie(o)


def apilar_bloques(pag: Pagina, grupos: Sequence[str], gap: float,
                   y_inicio: Optional[float] = None,
                   limite: Optional[float] = None) -> float:
    """Reapila verticalmente una serie de bloques con un ritmo constante.

    Es la forma de «compactar conservando el texto completo»: no se reduce
    cuerpo ni se eliminan contenidos, sólo se homogeneiza el espacio entre
    bloques. Si ``limite`` se indica, el interlineado entre bloques se reduce
    lo necesario para que el último cierre por encima de esa cota.
    """
    bloques = [(gr, objetos_de_grupo(pag, gr)) for gr in grupos]
    bloques = [(gr, objs) for gr, objs in bloques if objs]
    if not bloques:
        return 0.0
    alturas = []
    topes = []
    for _, objs in bloques:
        top = min(_techo_optico(o) for o in objs)
        bot = max(_fondo_optico(o) for o in objs)
        topes.append(top)
        alturas.append(bot - top)
    inicio = topes[0] if y_inicio is None else y_inicio
    if limite is not None:
        disponible = limite - inicio - sum(alturas)
        if len(bloques) > 1:
            gap = min(gap, disponible / (len(bloques) - 1))
    cursor = inicio
    desplazado = 0.0
    for (gr, objs), top, alto in zip(bloques, topes, alturas):
        mover(objs, dy=cursor - top)
        desplazado += abs(cursor - top)
        cursor += alto + gap
    return desplazado


def ajustar_a_ancho(elementos: Sequence[ElementoTexto], ancho_max: float,
                    tam_min: float = 1.78) -> float:
    """Reduce proporcionalmente el cuerpo hasta que el bloque quepa.

    Devuelve el tamaño resultante. Se aplica al conjunto para que títulos
    hermanos conserven la misma escala tipográfica.
    """
    elementos = [e for e in elementos if e.runs]
    if not elementos:
        return 0.0
    factor = 1.0
    for el in elementos:
        for r in el.runs:
            if not r.texto.strip():
                continue
            w = r.ancho()
            if w > ancho_max:
                factor = min(factor, ancho_max / w)
    if factor >= 0.999:
        return elementos[0].tam
    for el in elementos:
        nuevo = max(tam_min, round(el.tam * factor, 3))
        el.fijar_tam(nuevo)
    return elementos[0].tam


def reflujo(el: ElementoTexto, ancho_max: float,
            interlineado: Optional[float] = None,
            ancla: str = "primera") -> ElementoTexto:
    """Reparte el texto del objeto en las líneas necesarias para caber.

    ``ancla='primera'`` mantiene la primera línea de base (el bloque crece
    hacia abajo); ``ancla='ultima'`` mantiene la última (crece hacia arriba,
    útil cuando debajo hay contenido fijo).
    """
    if not el.runs:
        return el
    texto = " ".join(r.texto for r in el.runs if r.texto.strip())
    if interlineado is None:
        if len(el.runs) > 1:
            interlineado = abs(el.runs[1].y - el.runs[0].y)
        else:
            interlineado = round(el.tam * 1.25, 3)
    lineas = MEDIDOR.ajustar_lineas(texto, ancho_max, el.familia, el.tam, el.peso)
    y0 = el.runs[0].y if ancla == "primera" else \
        el.runs[-1].y - interlineado * (len(lineas) - 1)
    modelo = el.runs[0]
    el.runs = [
        Run(texto=linea, x=modelo.x, y=round(y0 + i * interlineado, 4),
            familia=el.familia, tam=el.tam, peso=el.peso, estilo=el.estilo,
            color=el.color, anchor=el.anchor, letter_spacing=el.letter_spacing)
        for i, linea in enumerate(lineas)
    ]
    return el


def escalar_zona(pag: Pagina, x0: float, y0: float, x1: float, y1: float,
                 factor: float, dy: float = 0.0,
                 excluir: Sequence[str] = ()) -> int:
    """Escala un conjunto (diagrama) alrededor de su propio centro."""
    sel = []
    for o in list(pag.vectores) + list(pag.textos):
        if o.id in excluir:
            continue
        if isinstance(o, ElementoTexto):
            if not any(r.texto.strip() for r in o.runs):
                continue
            ox0, oy0, ox1, oy1 = o.x_min(), o.y_min(), o.x_max(), o.y_max()
        else:
            ox0, oy0 = o.bbox[0], o.bbox[1]
            ox1, oy1 = ox0 + o.bbox[2], oy0 + o.bbox[3]
        if ox0 >= x0 and ox1 <= x1 and oy0 >= y0 and oy1 <= y1:
            sel.append(o)
    if not sel:
        return 0
    cx0, cy0, cx1, cy1 = bbox_objetos(sel)
    cx, cy = (cx0 + cx1) / 2.0, (cy0 + cy1) / 2.0
    for o in sel:
        o.escalar(factor, cx, cy)
        if dy:
            o.mover(0, dy)
    return len(sel)


def separar_solapes_verticales(pag: Pagina, grupo: str, holgura: float = 0.35,
                               limite: Optional[float] = None) -> int:
    """Reparte los ítems de una lista cuando el interlineado los deja tocándose.

    Los ítems se identifican por línea de base común (marca `•` y texto forman
    un solo ítem). Sólo se desplaza si el resultado cabe bajo ``limite``.
    """
    elementos = [t for t in pag.textos if t.grupo == grupo and t.runs
                 and any(r.texto.strip() for r in t.runs)]
    if len(elementos) < 2:
        return 0
    items: List[List[ElementoTexto]] = []
    for el in sorted(elementos, key=lambda t: min(r.y for r in t.runs)):
        base = min(r.y for r in el.runs)
        if items and abs(min(r.y for r in items[-1][0].runs) - base) < 0.25:
            items[-1].append(el)
        else:
            items.append([el])
    movidos = 0
    for i in range(1, len(items)):
        prev = items[i - 1]
        cur = items[i]
        fondo = max(max(r.y for r in e.runs) + e.tam * 0.27 for e in prev)
        techo = min(min(r.y for r in e.runs) - e.tam * 0.71 for e in cur)
        delta = (fondo + holgura) - techo
        if delta <= 0:
            continue
        cola = [e for grp in items[i:] for e in grp]
        if limite is not None:
            fondo_final = max(max(r.y for r in e.runs) for e in cola) + delta
            if fondo_final > limite:
                continue
        mover(cola, dy=delta)
        movidos += 1
    return movidos


def eliminar(pag: Pagina, *ids: str) -> int:
    """Suprime objetos residuales, duplicados o sin función editorial."""
    conjunto = set(ids)
    antes = len(pag.textos) + len(pag.vectores)
    pag.textos = [t for t in pag.textos if t.id not in conjunto]
    pag.vectores = [v for v in pag.vectores if v.id not in conjunto]
    return antes - (len(pag.textos) + len(pag.vectores))


def y_regla_pie(pag: Pagina) -> Optional[ElementoVector]:
    for v in pag.vectores:
        if v.tipo in ("line", "rect") and v.bbox[3] <= 1.2 and 265 <= v.bbox[1] <= 294:
            if v.bbox[2] > 120:
                return v
    return None


def normalizar_pie(pag: Pagina, y_regla: float, y_fecha: float,
                   y_folio: float, x0: float = MARGEN_IZQ,
                   x1: float = MARGEN_DER) -> None:
    """Deja el pie despejado según MASTER_FOOTER y el override de la página."""
    regla = y_regla_pie(pag)
    if regla is None:
        regla = ElementoVector(
            id=f"p{pag.numero:02d}_footer_rule",
            tipo="line",
            geom={"x1": x0, "y1": y_regla, "x2": x1, "y2": y_regla},
            estilo={"stroke": PRIMARY_BLUE, "stroke-width": "0.32"},
            grupo="pie",
            bbox=(x0, y_regla, x1 - x0, 0.0),
        )
        pag.vectores.append(regla)
    else:
        regla.mover(0, y_regla - regla.bbox[1])
        regla.grupo = "pie"
    for t in pag.textos:
        if t.role == "FOOTER_LOCATION_YEAR":
            t.mover(0, y_fecha - t.runs[0].y)
            t.grupo = "pie"
        elif t.role == "PAGE_NUMBER" and t.runs[0].y > 250:
            t.mover(0, y_folio - t.runs[0].y)
            t.grupo = "pie"


def clonar_identidad(origen: Pagina, destino: Pagina) -> None:
    """Restituye el maestro de identidad (escudo + USACH + Facultad + lema)."""
    import copy
    pref = f"p{destino.numero:02d}_"
    crest = next((v for v in origen.vectores if v.id.startswith("header_crest")), None)
    if crest is not None and not any(v.id.startswith(pref + "header_crest")
                                     for v in destino.vectores):
        nuevo = copy.deepcopy(crest)
        nuevo.id = pref + "header_crest"
        nuevo.grupo = "encabezado"
        destino.vectores.insert(1, nuevo)
    existentes = {t.role for t in destino.textos}
    if "HEADER_IDENTITY" in existentes:
        return
    for t in origen.textos:
        if t.role != "HEADER_IDENTITY":
            continue
        nuevo = copy.deepcopy(t)
        nuevo.id = pref + re.sub(r"[^a-zA-Z0-9]+", "_", t.runs[0].texto.lower())[:24]
        nuevo.grupo = "encabezado"
        destino.textos.insert(0, nuevo)


# ---------------------------------------------------------------------------
# 9. BIBLIOTECA DE COMPONENTES (COMPONENT_LIBRARY)
#    Constructores usados para componer la PAGE_23 recuperada.
# ---------------------------------------------------------------------------

def comp_texto(id_: str, x: float, y: float, lineas: Sequence[str],
               tam: float, peso: int = 400, familia: str = SANS,
               color: str = PRIMARY_BLUE, interlineado: Optional[float] = None,
               anchor: Optional[str] = None, role: str = "BODY_TEXT",
               grupo: str = "cuerpo") -> ElementoTexto:
    inter = interlineado if interlineado is not None else round(tam * 1.32, 3)
    runs = [Run(texto=t, x=x, y=round(y + i * inter, 4), familia=familia,
                tam=tam, peso=peso, color=color, anchor=anchor)
            for i, t in enumerate(lineas)]
    return ElementoTexto(id=id_, role=role, runs=runs, familia=familia, tam=tam,
                         peso=peso, color=color, anchor=anchor, grupo=grupo)


def comp_parrafo(id_: str, x: float, y: float, texto: str, ancho: float,
                 tam: float, peso: int = 400, familia: str = SANS,
                 interlineado: Optional[float] = None,
                 role: str = "BODY_TEXT", grupo: str = "cuerpo") -> ElementoTexto:
    """Párrafo justificado a la izquierda con reflujo medido por fuente real."""
    lineas = MEDIDOR.ajustar_lineas(" ".join(texto.split()), ancho, familia,
                                    tam, peso)
    return comp_texto(id_, x, y, lineas, tam, peso, familia,
                      interlineado=interlineado, role=role, grupo=grupo)


def comp_regla(id_: str, x1: float, y: float, x2: float,
               color: str = PRIMARY_BLUE, grosor: float = 0.32,
               grupo: str = "cuerpo") -> ElementoVector:
    return ElementoVector(
        id=id_, tipo="line",
        geom={"x1": x1, "y1": y, "x2": x2, "y2": y},
        estilo={"stroke": color, "stroke-width": str(grosor)},
        grupo=grupo, bbox=(x1, y, x2 - x1, 0.0))


def comp_encabezado_articulo(pref: str, x: float, y_num: float, numero: str,
                             titulo: str, y_titulo: float,
                             tam_num: float = 4.0, tam_titulo: float = 10.2,
                             ancho: float = ANCHO_UTIL,
                             acento: Optional[float] = None,
                             grupo: str = "cuerpo") -> List:
    """ARTICLE_HEADER: `Artículo NN.` + título de área + filete de acento."""
    objetos: List = []
    objetos.append(comp_texto(f"{pref}_num", x, y_num, [numero], tam_num,
                              peso=600, familia=SERIF, role="ARTICLE_HEADING",
                              grupo=grupo))
    lineas = MEDIDOR.ajustar_lineas(titulo, ancho, SERIF, tam_titulo, 600)
    objetos.append(comp_texto(f"{pref}_titulo", x, y_titulo, lineas,
                              tam_titulo, peso=600, familia=SERIF,
                              interlineado=round(tam_titulo * 1.18, 3),
                              role="DISPLAY_TITLE_L", grupo=grupo))
    if acento is not None:
        objetos.append(comp_regla(f"{pref}_acento", x, acento, x + 15.0,
                                  SECONDARY_BLUE, 0.8, grupo=grupo))
    return objetos


def comp_lista_bullets(pref: str, x: float, y: float, items: Sequence[str],
                       tam: float = 2.5, ancho: float = 80.0,
                       interlineado: float = 3.3, salto_item: float = 1.2,
                       sangria: float = 4.2, grupo: str = "cuerpo") -> List:
    """BULLET_LIST: marca y texto como objetos `<text>` independientes."""
    objetos: List = []
    cursor = y
    for i, item in enumerate(items, 1):
        lineas = MEDIDOR.ajustar_lineas(item, ancho - sangria, SANS, tam, 400)
        objetos.append(comp_texto(f"{pref}_mark_{i:02d}", x, cursor, ["•"],
                                  round(tam * 1.02, 3), role="BULLET_OR_CONNECTOR_LABEL",
                                  grupo=grupo))
        objetos.append(comp_texto(f"{pref}_text_{i:02d}", x + sangria, cursor,
                                  lineas, tam, interlineado=interlineado,
                                  role="BODY_TEXT", grupo=grupo))
        cursor += interlineado * len(lineas) + salto_item
    return objetos


def comp_tarjeta_actividad(pref: str, x: float, y: float, ancho: float,
                           alto: float, titulo: str, items: Sequence[str],
                           padding: float = 4.0, radio: float = 3.0,
                           tam_titulo: float = 2.85, tam_cuerpo: float = 2.45,
                           interlineado: float = 3.25) -> List:
    """AREA_ACTIVITY_CARD: rect editable + título + lista interna."""
    grupo = pref
    objetos: List = [ElementoVector(
        id=f"{pref}_box", tipo="rect",
        geom={"x": x, "y": y, "width": ancho, "height": alto,
              "rx": radio, "ry": radio},
        estilo={"fill": BACKGROUND_WHITE, "stroke": SECONDARY_BLUE,
                "stroke-width": "0.28"},
        grupo=grupo, bbox=(x, y, ancho, alto))]
    xi = x + padding
    ancho_util = ancho - 2 * padding
    y_titulo = y + padding + tam_titulo + 1.4
    lineas_titulo = MEDIDOR.ajustar_lineas(titulo, ancho_util, SANS,
                                           tam_titulo, 700)
    objetos.append(comp_texto(f"{pref}_titulo", xi, y_titulo, lineas_titulo,
                              tam_titulo, peso=700, interlineado=3.4,
                              role="HEADING_OR_LABEL", grupo=grupo))
    y_regla = y_titulo + 3.4 * (len(lineas_titulo) - 1) + 2.6
    objetos.append(comp_regla(f"{pref}_regla", xi, y_regla, x + ancho - padding,
                              RULE_BLUE, 0.16, grupo=grupo))
    objetos.extend(comp_lista_bullets(
        pref, xi, y_regla + 5.0, items, tam=tam_cuerpo, ancho=ancho_util,
        interlineado=interlineado, salto_item=1.0, sangria=3.6, grupo=grupo))
    return objetos


def comp_estrella(id_: str, cx: float, cy: float, r: float,
                  color: str = PRIMARY_BLUE, grupo: str = "cuerpo") -> ElementoVector:
    """Estrella de cinco puntas como `path` editable (ICON_SYSTEM)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        radio = r if i % 2 == 0 else r * 0.42
        pts.append((cx + radio * math.cos(ang), cy + radio * math.sin(ang)))
    d = "M " + " L ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in pts) + " Z"
    return ElementoVector(id=id_, tipo="path", geom={"d": d},
                          estilo={"fill": color, "stroke": "none"},
                          grupo=grupo,
                          bbox=(cx - r, cy - r, 2 * r, 2 * r))


def comp_triangulo(id_: str, cx: float, cy: float, r: float,
                   color: str = PRIMARY_BLUE,
                   grupo: str = "cuerpo") -> ElementoVector:
    pts = [(cx + r * math.cos(-math.pi / 2 + i * 2 * math.pi / 3),
            cy + r * math.sin(-math.pi / 2 + i * 2 * math.pi / 3))
           for i in range(3)]
    d = "M " + " L ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in pts) + " Z"
    return ElementoVector(id=id_, tipo="path", geom={"d": d},
                          estilo={"fill": color, "stroke": "none"},
                          grupo=grupo,
                          bbox=(cx - r, cy - r, 2 * r, 2 * r))


def comp_circulo(id_: str, cx: float, cy: float, r: float, relleno: bool,
                 color: str = PRIMARY_BLUE,
                 grupo: str = "cuerpo") -> ElementoVector:
    estilo = ({"fill": color, "stroke": "none"} if relleno
              else {"fill": "none", "stroke": color, "stroke-width": "0.45"})
    return ElementoVector(id=id_, tipo="circle",
                          geom={"cx": cx, "cy": cy, "r": r},
                          estilo=estilo, grupo=grupo,
                          bbox=(cx - r, cy - r, 2 * r, 2 * r))


def _items_desde_bloque(texto: str) -> List[str]:
    """Convierte un bloque `• …` multilínea del Markdown en items limpios."""
    items: List[str] = []
    actual: List[str] = []
    for linea in (texto or "").split("\n"):
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("•"):
            if actual:
                items.append(" ".join(actual))
            actual = [linea.lstrip("•").strip()]
        else:
            actual.append(linea)
    if actual:
        items.append(" ".join(actual))
    return items


def construir_pagina_23(pag: Pagina, donante: Pagina) -> None:
    """Compone la PAGE_23 recuperada (`p23_corregido_preview.pdf`).

    El folio 23 no existe físicamente en el SVG de avance; la especificación
    corregida lo reincorpora con contenido verificado. Se reconstruye con la
    biblioteca de componentes, respetando `MASTER_PAGE_STANDARD_ODD`, la
    retícula fija de cuatro columnas del Artículo 43 y el cierre del
    Artículo 44 con sus tres grupos.
    """
    c = pag.contenido
    pag.vectores = [ElementoVector(
        id="p23_fondo", tipo="rect",
        geom={"x": 0, "y": 0, "width": PAGE_W, "height": PAGE_H},
        estilo={"fill": BACKGROUND_WHITE, "stroke": "none"},
        grupo="fondo", bbox=(0.0, 0.0, PAGE_W, PAGE_H))]
    pag.textos = []

    # -- maestro de identidad + filete de encabezado ------------------------
    clonar_identidad(donante, pag)
    pag.vectores.append(comp_regla("p23_header_rule", MARGEN_IZQ, 33.84,
                                   MARGEN_DER, PRIMARY_BLUE, 0.32,
                                   grupo="encabezado"))

    # -- ZONA A · Artículo 43 ----------------------------------------------
    enc43 = (c.get("ARTICLE_43_HEADING") or "Artículo 43.\nAsistencia técnica")
    num43, _, tit43 = enc43.partition("\n")
    for obj in comp_encabezado_articulo("p23_a43", MARGEN_IZQ, 45.5,
                                        num43.strip(), tit43.strip(), 58.7,
                                        acento=66.4, grupo="articulo_43"):
        (pag.vectores if isinstance(obj, ElementoVector) else pag.textos).append(obj)
    pag.textos.append(comp_parrafo(
        "p23_a43_cuerpo", MARGEN_IZQ, 78.0, c.get("ARTICLE_43_BODY", ""),
        ANCHO_UTIL, 3.0, interlineado=4.6, grupo="articulo_43"))
    pag.textos.append(comp_texto(
        "p23_a43_lead", MARGEN_IZQ, 99.0,
        [" ".join(c.get("ARTICLE_43_LEAD", "").split())], 2.85, peso=700,
        role="EMPHASIS_OR_LABEL", grupo="articulo_43"))

    # -- ZONA B · retícula fija de 4 tarjetas ------------------------------
    xs = [18.0, 62.5, 107.0, 151.5]
    for i, x in enumerate(xs, 1):
        datos = c.get(f"CARD_43_{i:02d}") or {}
        titulo = " ".join(str(datos.get("title", "")).split())
        items = _items_desde_bloque(str(datos.get("body", "")))
        for obj in comp_tarjeta_actividad(f"p23_card_43_{i}", x, 105.0, 40.5,
                                          55.0, titulo, items):
            (pag.vectores if isinstance(obj, ElementoVector) else pag.textos).append(obj)

    # filete de cierre del Artículo 43, como en las páginas 21 y 24
    pag.vectores.append(comp_regla("p23_a43_cierre", MARGEN_IZQ, 169.0,
                                   MARGEN_DER, PRIMARY_BLUE, 0.26,
                                   grupo="articulo_43"))

    # -- ZONA C · Artículo 44 ----------------------------------------------
    enc44 = (c.get("ARTICLE_44_HEADING") or "Artículo 44.\nAdministración académica")
    num44, _, tit44 = enc44.partition("\n")
    for obj in comp_encabezado_articulo("p23_a44", MARGEN_IZQ, 177.0,
                                        num44.strip(), tit44.strip(), 186.6,
                                        tam_titulo=7.8, grupo="articulo_44"):
        (pag.vectores if isinstance(obj, ElementoVector) else pag.textos).append(obj)
    pag.textos.append(comp_parrafo(
        "p23_a44_cuerpo", MARGEN_IZQ, 194.5, c.get("ARTICLE_44_BODY", ""),
        ANCHO_UTIL, 3.18, interlineado=4.9, grupo="articulo_44"))
    pag.textos.append(comp_texto(
        "p23_a44_lead", MARGEN_IZQ, 233.0,
        [" ".join(c.get("ARTICLE_44_LEAD", "").split())], 2.85, peso=700,
        role="EMPHASIS_OR_LABEL", grupo="articulo_44"))
    for obj in comp_lista_bullets(
            "p23_a44_grupos", MARGEN_IZQ, 241.0,
            _items_desde_bloque(c.get("ARTICLE_44_GROUPS", "")),
            tam=3.0, ancho=ANCHO_UTIL, interlineado=4.4, salto_item=4.1,
            sangria=6.0, grupo="articulo_44"):
        pag.textos.append(obj)

    # -- MASTER_FOOTER ------------------------------------------------------
    pag.textos.append(comp_texto("p23_footer_city", MARGEN_IZQ, 290.0,
                                 ["Santiago, Chile · 2026"], 3.05,
                                 role="FOOTER_LOCATION_YEAR", grupo="pie"))
    pag.textos.append(comp_texto("p23_footer_page", MARGEN_DER, 292.0, ["23"],
                                 7.4, peso=600, familia=SERIF, anchor="end",
                                 role="PAGE_NUMBER", grupo="pie"))
    pag.vectores.append(comp_regla("p23_footer_rule", MARGEN_IZQ, 283.0,
                                   MARGEN_DER, PRIMARY_BLUE, 0.32, grupo="pie"))


# ---------------------------------------------------------------------------
# 10. CORRECTION_OVERRIDE — MANDATORY
#     Una función por página, en el orden y con el alcance que fija el
#     Markdown corregido. Estas correcciones tienen precedencia sobre las
#     coordenadas heredadas del SVG de avance.
# ---------------------------------------------------------------------------

def _p01(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Portada: título principal refluido a cuatro líneas, 14.0 / peso 600."""
    titulo = next((t for t in pag.textos if t.role == "DISPLAY_TITLE_XL"), None)
    if titulo is None:
        return
    lineas = ["Manual de", "Evaluación y Calificación",
              "del Desempeño", "Académico"]
    ys = [70.0, 84.2, 98.4, 112.6]
    titulo.familia, titulo.peso = SERIF, 600
    titulo.fijar_tam(14.0)
    titulo.runs = [Run(texto=t, x=19.0, y=y, familia=SERIF, tam=14.0, peso=600,
                       color=titulo.color) for t, y in zip(lineas, ys)]


def _p04(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Dos columnas; el último bloque de definiciones se eleva si invade el pie."""
    limite = _limite_cuerpo(pag)
    bloque = [t for t in pag.textos
              if not _es_pie(t) and t.runs and t.y_max() > limite]
    if bloque:
        mover(bloque, dy=-12.0)
    _folios_serif(pag)


def _p06(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Artículos 7–11 compactados con la progresión documentada."""
    normalizar_pie(pag, 284.0, 291.0, 293.0)
    # Compactación con ritmo uniforme: se conserva todo el texto y se evita
    # que los separadores queden sobre los títulos, cosa que sí ocurriría con
    # la progresión fija −4/−8/−12/−18/−25 aplicada literalmente.
    base = objetos_de_grupo(pag, "article-6")
    y0 = max(_fondo_optico(o) for o in base) if base else 112.0
    apilar_bloques(pag, [f"article-{i}" for i in range(7, 12)], gap=2.70,
                   y_inicio=y0 + 2.70, limite=_limite_cuerpo(pag))
    # separador redundante bajo el último artículo: se suprime si toca el pie
    for v in list(pag.vectores):
        if v.id.endswith("separator") and v.bbox[1] > _limite_cuerpo(pag):
            eliminar(pag, v.id)


def _p08(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Etapas 3 y 4: los dos títulos comparten escala y respetan x=192."""
    titulos = [pag.texto("article_15_title"), pag.texto("article_16_title")]
    titulos = [t for t in titulos if t]
    if titulos:
        ancho = min(MARGEN_DER - t.runs[0].x for t in titulos)
        ajustar_a_ancho(titulos, ancho, 5.4)


def _p09(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Restituye MASTER_PAGE_STANDARD_ODD: el encabezado ausente es un error."""
    clonar_identidad(doc[17], pag)


def _p10(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Título principal ≤10.0 y rótulos 4.1/4.2 normalizados a serif."""
    titulo = pag.texto("main_title-52")
    if titulo:
        titulo.fijar_tam(10.0)
        ajustar_a_ancho([titulo], MARGEN_DER - titulo.runs[0].x, 9.0)
    for id_ in ("section_41-3", "section_42-8", "logic_title", "criteria_title"):
        el = pag.texto(id_)
        if el:
            el.familia = SERIF
            for r in el.runs:
                r.familia = SERIF


def _p11(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Proceso secuencial de 5 pasos ajustado al ancho útil, sin deformar."""
    distribuir_fila(pag, [f"process_{i}" for i in range(1, 6)])
    for i in range(1, 6):
        el = pag.texto(f"card_title_{i}")
        if el and el.x_max() - el.x_min() > 28.0:
            el.fijar_tam(2.20)


def _p12(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Fila de modificaciones dentro del margen y título del Art. 26 refluido."""
    distribuir_fila(pag, [f"modification_{i}" for i in range(1, 7)])
    titulo = pag.texto("article26_title")
    if titulo:
        reflujo(titulo, MARGEN_DER - titulo.runs[0].x,
                interlineado=round(titulo.tam * 1.22, 3), ancla="ultima")
    nota = pag.texto("section_b_note")
    if nota:
        nota.mover(0, -5.0)
    normalizar_pie(pag, 280.0, 288.0, 291.0)


def _p14(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Callout de síntesis elevado; tabla semántica y dos columnas intactas."""
    titulo = pag.texto("t31")
    if titulo:
        reflujo(titulo, MARGEN_DER - titulo.runs[0].x,
                interlineado=round(titulo.tam * 1.35, 3))
    callout = pag.texto("t46")
    if callout:
        mover(objetos_en_banda(pag, callout.y_min() - 4.0, 275.0), dy=-7.0)


def _p16(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Escala de calificación: marcas de nivel como iconografía vectorial.

    ★ ● ▲ ○ y ∑ no existen en `Noto Sans` ni en `Noto Serif Display`; usar una
    tercera familia está prohibido. Los marcadores pasan a ICON_SYSTEM (`path`
    y `circle` editables) y el sumatorio se resuelve con la Σ griega, que sí
    forma parte del juego de caracteres del sistema.
    """
    formula = pag.texto("t6-2")
    if formula:
        for r in formula.runs:
            r.texto = r.texto.replace("\u2211", "\u03a3")
    marcas = {
        "t12-70": ("estrella", 2.15),
        "t15-7": ("circulo_lleno", 1.75),
        "t18-8": ("triangulo", 2.05),
        "t21-6": ("circulo_vacio", 1.75),
    }
    for id_, (forma, radio) in marcas.items():
        el = pag.texto(id_)
        if el is None:
            continue
        cx = el.runs[0].x
        cy = el.runs[0].y - el.tam * 0.36
        nombre = f"p16_nivel_{forma}"
        if forma == "estrella":
            icono = comp_estrella(nombre, cx, cy, radio)
        elif forma == "triangulo":
            icono = comp_triangulo(nombre, cx, cy, radio)
        else:
            icono = comp_circulo(nombre, cx, cy, radio,
                                 relleno=(forma == "circulo_lleno"))
        eliminar(pag, id_)
        pag.vectores.append(icono)


def _p17(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Rúbrica General: título refluido, diagrama al 82 % y callouts separados."""
    titulo = pag.texto("t23-21")
    if titulo:
        reflujo(titulo, MARGEN_DER - titulo.runs[0].x,
                interlineado=round(titulo.tam * 0.98, 3))
    escalar_zona(pag, 106.0, 138.0, 200.0, 246.0, 0.82, dy=-5.0)
    for id_ in ("t32-9", "t33-9"):
        el = pag.texto(id_)
        if el:
            el.mover(0, 6.0)


def _p18(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Apertura del Título VII: se elimina el encabezado largo duplicado."""
    duplicado = next((t for t in pag.textos
                      if t.role == "HEADER_IDENTITY"
                      and "MANUAL DE EVALUACIÓN" in t.texto_plano().upper()), None)
    if duplicado is not None:
        eliminar(pag, duplicado.id)
    titulo = next((t for t in pag.textos if t.role == "DISPLAY_TITLE_XL"), None)
    if titulo:
        titulo.familia = SERIF
        for r in titulo.runs:
            r.familia = SERIF


def _p19(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Tarjeta final elevada sólo si invade el pie; altura mínima resguardada."""
    caja = next((v for v in pag.vectores if v.id == "card_7_box"), None)
    limite = _limite_cuerpo(pag)
    if caja is not None:
        if caja.y_max() > limite:
            mover(objetos_de_grupo(pag, "card_7"), dy=-(caja.y_max() - limite) - 1.0)
        alto_disponible = limite - caja.bbox[1] - 1.0
        if caja.bbox[3] < 25.0 and alto_disponible > caja.bbox[3]:
            caja.alto(round(min(25.0, alto_disponible), 2))
    for grupo in sorted({t.grupo for t in pag.textos if t.grupo.startswith("card_")}):
        caja = next((v for v in pag.vectores
                     if v.grupo == grupo and v.tipo == "rect"), None)
        separar_solapes_verticales(
            pag, grupo, limite=(caja.y_max() - 2.0) if caja else None)
    normalizar_pie(pag, 279.0, 287.0, 290.0)


def _p21(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Lista `Proyectos VIME` compactada sólo si invade la fila inferior."""
    caja = next((v for v in pag.vectores if v.id == "extension_card_1_box"), None)
    if caja is None:
        return
    items = [t for t in pag.textos if t.grupo == "extension_card_1"
             and t.role == "BODY_TEXT"]
    if not items:
        return
    fondo = max(t.y_max() for t in items)
    exceso = fondo - (caja.y_max() - 3.0)
    if exceso > 0:
        base = min(t.runs[0].y for t in items)
        factor = max(0.82, 1.0 - exceso / max(1.0, fondo - base))
        for t in items + [t for t in pag.textos if t.grupo == "extension_card_1"
                          and t.role == "BULLET_OR_CONNECTOR_LABEL"]:
            for r in t.runs:
                r.y = round(base + (r.y - base) * factor, 4)


def _p22(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Cinco grupos de Educación continua: etiquetas ajustadas al ancho útil."""
    cajas = {v.grupo: v for v in pag.vectores if v.tipo == "rect"
             and v.id.startswith("card_") and "_box" in v.id}
    for t in pag.textos:
        caja = cajas.get(t.grupo)
        if caja is None or t.role not in ("EMPHASIS_OR_LABEL", "HEADING_OR_LABEL"):
            continue
        disponible = caja.x_max() - 4.0 - t.runs[0].x
        if t.x_max() > caja.x_max() - 3.0:
            reflujo(t, disponible, interlineado=round(t.tam * 0.98, 3))


def _p24(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Artículo 45 elevado 8 mm y su fila de tarjetas 10 mm; pie despejado."""
    elevar_bloque(pag, 200.0, 256.0, 8.0)
    tarjetas = objetos_de_grupo(pag, *[f"perf_card_{i}" for i in range(1, 6)])
    if tarjetas:
        y_top = min(_techo_optico(o) for o in tarjetas)
        elevar_bloque(pag, y_top - 0.5, y_top + 30.0, 12.0)
    normalizar_pie(pag, 282.0, 289.0, 292.0)


def _p26(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Artículo 49: título de la columna derecha refluido dentro del margen."""
    titulo = pag.texto("t12-75")
    if titulo:
        reflujo(titulo, MARGEN_DER - titulo.runs[0].x,
                interlineado=round(titulo.tam * 1.3, 3))


def _p27(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Artículo 55 y apertura del Título X elevados; pie con filete propio."""
    titulo = pag.texto("t4-05")
    if titulo:
        ajustar_a_ancho([titulo], MARGEN_DER - titulo.runs[0].x, 9.0)
    elevar_bloque(pag, 190.0, 240.0, 7.0)
    # El objetivo de ≈18 mm se acota automáticamente: la lista de efectos del
    # Artículo 55, ya elevada, fija el techo disponible para el Título X.
    elevar_bloque(pag, 240.0, 286.0, 18.0, holgura=5.0)
    normalizar_pie(pag, 284.0, 291.0, 293.0)


def _p28(pag: Pagina, doc: Dict[int, Pagina]) -> None:
    """Artículo 60 elevado 10 mm; matriz 2×5 de requisitos intacta."""
    elevar_bloque(pag, 260.0, 282.0, 10.0)
    normalizar_pie(pag, 285.0, 291.0, 293.0)


CORRECCIONES: Dict[int, Callable[[Pagina, Dict[int, Pagina]], None]] = {
    1: _p01, 4: _p04, 6: _p06, 8: _p08, 9: _p09, 10: _p10, 11: _p11,
    12: _p12, 14: _p14, 16: _p16, 17: _p17, 18: _p18, 19: _p19, 21: _p21, 22: _p22,
    24: _p24, 26: _p26, 27: _p27, 28: _p28,
}


# ---------------------------------------------------------------------------
# 11. NORMALIZACIONES GLOBALES + ORQUESTACIÓN
# ---------------------------------------------------------------------------

def _contenedor(pag: Pagina, el: ElementoTexto) -> Optional[ElementoVector]:
    """Tarjeta o caja que encierra al objeto de texto, si existe."""
    x0, x1 = el.x_min(), el.x_max()
    y0, y1 = el.y_min(), el.y_max()
    mejor = None
    for v in pag.vectores:
        if v.tipo != "rect" or _es_fondo(v):
            continue
        if (v.x_min() <= x0 + 0.6 and v.x_max() >= x1 - 0.6
                and v.y_min() <= y0 + 0.6 and v.y_max() >= y1 - 0.6):
            if mejor is None or v.bbox[2] * v.bbox[3] < mejor.bbox[2] * mejor.bbox[3]:
                mejor = v
    return mejor


def espacio_libre_debajo(pag: Pagina, el: ElementoTexto,
                         holgura: float = 0.8) -> float:
    """Milímetros disponibles bajo un bloque de texto antes de chocar."""
    if not el.runs:
        return 0.0
    x0, x1 = el.x_min(), el.x_max()
    ancho = max(0.1, x1 - x0)
    fondo = _fondo_optico(el)
    # Referencia: cualquier objeto que empiece por debajo de la PRIMERA línea
    # del bloque limita su crecimiento, aunque hoy solape con las siguientes.
    fondo_primera = el.runs[0].y + el.tam * 0.27
    tope = _limite_cuerpo(pag)
    caja = _contenedor(pag, el)
    if caja is not None:
        tope = min(tope, caja.y_max() - 1.5)
    for otro in list(pag.textos) + list(pag.vectores):
        if otro is el or _es_fondo_o_pie(otro):
            continue
        if isinstance(otro, ElementoVector) and otro is caja:
            continue
        if isinstance(otro, ElementoTexto):
            if not otro.runs or not any(r.texto.strip() for r in otro.runs):
                continue
            ox0, ox1 = otro.x_min(), otro.x_max()
        else:
            ox0, ox1 = otro.x_min(), otro.x_max()
        solape = min(x1, ox1) - max(x0, ox0)
        if solape < 0.3 * ancho:
            continue
        techo = _techo_optico(otro)
        if techo > fondo_primera + 0.05:
            tope = min(tope, techo)
    return max(0.0, tope - fondo - holgura)


def airear_interlineado(paginas: Dict[int, Pagina], minimo_em: float = 1.06,
                        objetivo_em: float = 1.22) -> int:
    """Abre el interlineado de los bloques heredados con líneas superpuestas.

    El sistema tipográfico del manual define interlineados de ~1,2–1,3 em
    (`TYPOGRAPHY`), pero el SVG de avance conserva bloques con separaciones
    inferiores al cuerpo, donde ascendentes y descendentes se tocan. Se abre
    cada bloque hasta el objetivo sólo con el espacio realmente disponible
    bajo él, de modo que la corrección nunca genera un desborde nuevo.
    """
    corregidos = 0
    for n in sorted(paginas):
        pag = paginas[n]
        for el in sorted(pag.textos, key=lambda t: -_fondo_optico(t)):
            if len(el.runs) < 2:
                continue
            seps = [b.y - a.y for a, b in zip(el.runs, el.runs[1:])]
            if not seps or min(seps) <= 0:
                continue
            sep = min(seps)
            if sep >= el.tam * minimo_em - 0.02:
                continue
            deseada = el.tam * objetivo_em
            libre = espacio_libre_debajo(pag, el)
            huecos = len(el.runs) - 1
            extra = min(deseada - sep, libre / huecos)
            if extra <= 0.02:
                continue
            nueva = sep + extra
            factor = nueva / sep
            y0 = el.runs[0].y
            for r in el.runs[1:]:
                r.y = round(y0 + (r.y - y0) * factor, 4)
            corregidos += 1
    return corregidos


def _items_por_linea_base(textos: Sequence[ElementoTexto]) -> List[List[ElementoTexto]]:
    """Agrupa marca `•` y texto de un mismo ítem por su línea de base."""
    items: List[List[ElementoTexto]] = []
    for el in sorted(textos, key=lambda t: (min(r.y for r in t.runs),
                                            t.x_min())):
        base = min(r.y for r in el.runs)
        if items and abs(min(r.y for r in items[-1][0].runs) - base) < 0.25:
            items[-1].append(el)
        else:
            items.append([el])
    return items


def _columnas(items: Sequence[Sequence[ElementoTexto]]) -> List[List[Sequence]]:
    """Separa los ítems en columnas por solape horizontal (transitivo)."""
    cajas = [(min(e.x_min() for e in it), max(e.x_max() for e in it))
             for it in items]
    columnas: List[List[int]] = []
    rangos: List[List[float]] = []
    for i, (x0, x1) in enumerate(cajas):
        destino = None
        for j, (rx0, rx1) in enumerate(rangos):
            if min(x1, rx1) - max(x0, rx0) > 0.5:
                destino = j
                break
        if destino is None:
            columnas.append([i])
            rangos.append([x0, x1])
        else:
            columnas[destino].append(i)
            rangos[destino][0] = min(rangos[destino][0], x0)
            rangos[destino][1] = max(rangos[destino][1], x1)
    return [[items[i] for i in sorted(col, key=lambda k: min(
        r.y for r in items[k][0].runs))] for col in columnas]


def _abrir_item(item: Sequence[ElementoTexto], em: float) -> None:
    for el in item:
        if len(el.runs) < 2:
            continue
        seps = [b.y - a.y for a, b in zip(el.runs, el.runs[1:])]
        sep = min(seps)
        if sep <= 0 or sep >= el.tam * em - 0.02:
            continue
        factor = (el.tam * em) / sep
        y0 = el.runs[0].y
        for r in el.runs[1:]:
            r.y = round(y0 + (r.y - y0) * factor, 4)


def _alto_item(item: Sequence[ElementoTexto]) -> Tuple[float, float]:
    return (min(_techo_optico(e) for e in item),
            max(_fondo_optico(e) for e in item))


def reajustar_listas(paginas: Dict[int, Pagina], objetivo_em: float = 1.24,
                     gap_em: float = 0.80, minimo_em: float = 0.99) -> int:
    """Devuelve a las listas de tarjeta el ritmo del sistema tipográfico.

    Muchas listas heredadas del SVG de avance tienen el interlineado por
    debajo del cuerpo (líneas que se tocan) mientras la tarjeta queda medio
    vacía. Aquí se reabre el interlineado y se reparte el espacio libre entre
    los ítems de una misma columna, sin tocar el texto ni el cuerpo, y sólo
    si el resultado sigue cabiendo dentro de la tarjeta.
    """
    ajustadas = 0
    for n in sorted(paginas):
        pag = paginas[n]
        grupos: Dict[str, List[ElementoTexto]] = {}
        for t in pag.textos:
            if t.runs and any(r.texto.strip() for r in t.runs) and not _es_pie(t):
                grupos.setdefault(t.grupo, []).append(t)
        for grupo, textos in grupos.items():
            # sólo módulos con identidad propia (tarjetas, pasos, filas): el
            # cajón genérico «cuerpo» no delimita ninguna lista
            if grupo in ("cuerpo", "") or len(textos) < 3:
                continue
            caja = next((v for v in pag.vectores
                         if v.grupo == grupo and v.tipo == "rect"
                         and not _es_fondo(v)
                         and all(v.x_min() <= t.x_min() + 0.6
                                 and v.x_max() >= t.x_max() - 0.6
                                 and v.y_min() <= t.y_min() + 0.6
                                 and v.y_max() >= t.y_max() - 0.6
                                 for t in textos)), None)
            if caja is None:
                continue
            for columna in _columnas(_items_por_linea_base(textos)):
                if len(columna) < 2:
                    continue
                apretado = any(
                    (b.y - a.y) < el.tam * minimo_em - 0.02
                    for it in columna for el in it
                    for a, b in zip(el.runs, el.runs[1:]) if b.y > a.y)
                if not apretado:
                    continue
                limite = caja.y_max() - 1.6
                inicio = _alto_item(columna[0])[0]
                for em, gem in ((objetivo_em, gap_em), (1.16, 0.62),
                                (1.08, 0.48), (1.0, 0.36)):
                    prueba = [[(e, [r.y for r in e.runs]) for e in it]
                              for it in columna]
                    for it in columna:
                        _abrir_item(it, em)
                    alturas = [(_alto_item(it)[1] - _alto_item(it)[0])
                               for it in columna]
                    tam = max(e.tam for it in columna for e in it)
                    gap = tam * gem
                    total = inicio + sum(alturas) + gap * (len(columna) - 1)
                    if total <= limite:
                        cursor = inicio
                        for it, alto in zip(columna, alturas):
                            techo = _alto_item(it)[0]
                            mover(it, dy=cursor - techo)
                            cursor += alto + gap
                        ajustadas += 1
                        break
                    for it in prueba:            # descartar el intento
                        for e, ys in it:
                            for r, y in zip(e.runs, ys):
                                r.y = y
    return ajustadas


def _limite_cuerpo(pag: Pagina) -> float:
    """Línea a partir de la cual empieza la zona reservada del pie."""
    regla = y_regla_pie(pag)
    if regla is not None:
        return regla.bbox[1] - 1.2
    return CUERPO_BOTTOM_SEGURO


def _folios_serif(pag: Pagina) -> None:
    """Todos los folios en Noto Serif Display; ninguna tercera serif."""
    for t in pag.textos:
        if t.role == "PAGE_NUMBER":
            t.familia = SERIF
            for r in t.runs:
                r.familia = SERIF


def _marcar_pie(pag: Pagina) -> None:
    for t in pag.textos:
        if t.role in ROLES_PIE and t.runs and t.runs[0].y > 250:
            t.grupo = "pie"
    regla = y_regla_pie(pag)
    if regla is not None:
        regla.grupo = "pie"


def aplicar_correcciones(paginas: Dict[int, Pagina]) -> None:
    """Aplica la POLÍTICA DE NORMALIZACIÓN Y PRECEDENCIA del Markdown."""
    for n in sorted(paginas):
        _folios_serif(paginas[n])
        _marcar_pie(paginas[n])
        depurar_texto_en_curvas(paginas[n])
    # PAGE_23 se reconstruye antes que el resto para poder validarla igual
    if 23 in paginas:
        construir_pagina_23(paginas[23], paginas[17])
    for n in sorted(CORRECCIONES):
        if n in paginas:
            CORRECCIONES[n](paginas[n], paginas)
    reajustar_listas(paginas)
    airear_interlineado(paginas)
    for n in sorted(paginas):
        _marcar_pie(paginas[n])


# ---------------------------------------------------------------------------
# 12. RENDER Y EXPORTACIÓN
# ---------------------------------------------------------------------------

def exportar_previews(paginas: Dict[int, Pagina], destino: str = DIR_PREVIEW,
                      dpi: int = 110) -> List[str]:
    """Renderiza cada página a PNG para control visual."""
    try:
        import cairosvg
    except ImportError:                       # pragma: no cover
        print("  · cairosvg no disponible: se omiten previews PNG")
        return []
    os.makedirs(destino, exist_ok=True)
    salidas = []
    for n in sorted(paginas):
        svg = construir_svg_pagina(paginas[n])
        ruta = os.path.join(destino, f"pagina_{n:02d}.png")
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=ruta, dpi=dpi)
        salidas.append(ruta)
    return salidas


def exportar_pdf(paginas: Dict[int, Pagina], destino: str = SALIDA_PDF) -> Optional[str]:
    """PDF de 30 páginas A4 con el texto vectorial (sin rasterizado)."""
    try:
        import cairosvg
    except ImportError:                       # pragma: no cover
        print("  · cairosvg no disponible: se omite el PDF")
        return None
    paginas_pdf = []
    for n in sorted(paginas):
        svg = construir_svg_pagina(paginas[n])
        paginas_pdf.append(cairosvg.svg2pdf(bytestring=svg.encode("utf-8")))
    try:
        from pypdf import PdfWriter, PdfReader
        import io
        escritor = PdfWriter()
        for datos in paginas_pdf:
            escritor.append(PdfReader(io.BytesIO(datos)))
        with open(destino, "wb") as fh:
            escritor.write(fh)
        return destino
    except ImportError:                       # pragma: no cover
        print("  · pypdf no disponible: se omite el PDF combinado")
        return None


# ---------------------------------------------------------------------------
# 13. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------

def construir_documento() -> Dict[int, Pagina]:
    """Pipeline completo: especificación → correcciones → páginas listas."""
    paginas = parse_especificacion()
    aplicar_correcciones(paginas)
    verificar_secuencia(paginas)
    return paginas


def verificar_secuencia(paginas: Dict[int, Pagina]) -> None:
    faltan = [i for i in range(1, TOTAL_PAGINAS + 1) if i not in paginas]
    if faltan:
        raise SystemExit(f"Faltan páginas en la secuencia editorial: {faltan}")
    vacias = [i for i, p in paginas.items() if not p.textos and not p.vectores]
    if vacias:
        raise SystemExit(f"Páginas sin contenido: {vacias}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-pdf", action="store_true", help="no generar el PDF")
    ap.add_argument("--no-preview", action="store_true", help="no generar PNGs")
    ap.add_argument("--auditar", action="store_true",
                    help="imprimir el informe completo de composición")
    args = ap.parse_args(argv)

    print("→ Leyendo especificación editorial corregida…")
    paginas = construir_documento()
    print(f"  {len(paginas)} páginas · "
          f"{sum(len(p.textos) for p in paginas.values())} objetos de texto · "
          f"{sum(len(p.vectores) for p in paginas.values())} objetos vectoriales")

    print("→ Escribiendo SVG multipágina…")
    svg = construir_svg_multipagina(paginas)
    with open(SALIDA_SVG, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"  {SALIDA_SVG} ({len(svg)/1024:.0f} KB)")

    print("→ Auditoría de composición…")
    hallazgos = auditar(paginas)
    print("  " + resumen_auditoria(hallazgos).replace("\n", "\n  "))
    if args.auditar:
        for h in hallazgos:
            print("   ", h)

    if not args.no_preview:
        print("→ Renderizando previews PNG…")
        rutas = exportar_previews(paginas)
        print(f"  {len(rutas)} páginas en {DIR_PREVIEW}/")

    if not args.no_pdf:
        print("→ Exportando PDF…")
        ruta = exportar_pdf(paginas)
        if ruta:
            print(f"  {ruta} ({os.path.getsize(ruta)/1024:.0f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
