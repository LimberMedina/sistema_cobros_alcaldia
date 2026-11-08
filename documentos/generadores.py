
import calendar
import os
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    Image as ReportLabImage,
)


MESES = [
    "",
    "ENERO", "FEBRERO", "MARZO", "ABRIL",
    "MAYO", "JUNIO", "JULIO", "AGOSTO",
    "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE",
    "DICIEMBRE"
]


def nombre_mes(mes):
    return MESES[mes]


def datos_solicitud(perfil, mes, anio, fecha, desde=None, hasta=None):
    mes_nombre = nombre_mes(mes)

    periodo = f"mes de {mes_nombre} del {anio}"

    if desde and hasta:
        periodo += (
            f", por el período comprendido entre "
            f"el {desde.strftime('%d/%m/%Y')} y "
            f"el {hasta.strftime('%d/%m/%Y')}"
        )

    introduccion = (
        "Muy respetuosamente me dirijo a usted, al mismo tiempo "
        "saludarle esperando que se encuentre muy bien de salud "
        "y deseándole éxitos en las labores que desempeña "
        "en bien de nuestro municipio."
    )

    motivo = (
        "El motivo de la presente es para solicitarle a su "
        f"autoridad la cancelación del sueldo correspondiente al {periodo}. "
        f"Como es de su conocimiento, desempeño el cargo de {perfil.cargo}."
    )

    anexos = [
        f"Informe individual de las actividades realizadas en el mes de {mes_nombre}.",
        "Fotocopia simple de contrato.",
        "Fotocopia simple de carnet de identidad.",
        "Fotocopia simple de NIT.",
    ]

    return {
        "lugar_fecha": (
            f"{perfil.ciudad}, {fecha.day:02d} de "
            f"{MESES[fecha.month].capitalize()} del {fecha.year}"
        ),
        "referencia": (
            f"SOLICITUD DE CANCELACIÓN DE SUELDO "
            f"DEL MES DE {mes_nombre} DEL {anio}"
        ),
        "introduccion": introduccion,
        "motivo": motivo,
        "anexos": anexos,
    }


def configurar_word(documento):
    seccion = documento.sections[0]
    seccion.page_height = Inches(11)
    seccion.page_width = Inches(8.5)
    seccion.top_margin = Inches(0.8)
    seccion.bottom_margin = Inches(0.7)
    seccion.left_margin = Inches(0.9)
    seccion.right_margin = Inches(0.8)

    estilo = documento.styles["Normal"]
    estilo.font.name = "Arial"
    estilo.font.size = Pt(11)


def agregar_parrafo(documento, texto, negrita=False, alineacion=None):
    p = documento.add_paragraph()
    if alineacion is not None:
        p.alignment = alineacion

    run = p.add_run(texto)
    run.bold = negrita
    return p


def carta_word(perfil, mes, anio, fecha, desde=None, hasta=None):
    datos = datos_solicitud(
        perfil, mes, anio, fecha, desde, hasta
    )

    doc = Document()
    configurar_word(doc)

    agregar_parrafo(
        doc,
        datos["lugar_fecha"],
        alineacion=WD_ALIGN_PARAGRAPH.RIGHT
    )

    doc.add_paragraph("")

    campos = [
        ("A:", perfil.destinatario, perfil.cargo_destinatario),
        ("VÍA:", perfil.via_1, perfil.cargo_via_1),
        ("VÍA:", perfil.via_2, perfil.cargo_via_2),
        ("DE:", perfil.nombre_completo, perfil.cargo),
    ]

    for etiqueta, nombre, cargo in campos:
        if nombre:
            parrafo = doc.add_paragraph()
            parrafo.add_run(etiqueta).bold = True
            parrafo.add_run(f" {nombre}")
            if cargo:
                parrafo_cargo = doc.add_paragraph()
                parrafo_cargo.add_run(f"     {cargo}").bold = True

    doc.add_paragraph("")

    agregar_parrafo(
        doc,
        "REF: " + datos["referencia"],
        negrita=True
    )

    doc.add_paragraph("")

    for texto in [datos["introduccion"], datos["motivo"]]:
        agregar_parrafo(
            doc,
            texto,
            alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY
        )

    agregar_parrafo(
        doc,
        "En la presente solicitud de pago, y en orden del "
        f"INSTRUCTIVO Nº{perfil.numero_instructivo} "
        "adjunto los siguientes documentos:"
    )

    for anexo in datos["anexos"]:
        doc.add_paragraph(anexo, style="List Bullet")

    agregar_parrafo(
        doc,
        "Sin otro en particular me despido con las "
        "consideraciones más distinguidas."
    )

    agregar_parrafo(doc, "Atentamente:")
    doc.add_paragraph("\n")

    agregar_parrafo(
        doc,
        perfil.nombre_completo,
        True,
        WD_ALIGN_PARAGRAPH.CENTER
    )
    agregar_parrafo(
        doc,
        perfil.cargo,
        True,
        WD_ALIGN_PARAGRAPH.CENTER
    )

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def dias_informe(actividades, mes, anio):
    ultimo_dia = calendar.monthrange(anio, mes)[1]

    agrupadas = {}

    for actividad in actividades:
        imagen = None
        if actividad.imagen:
            try:
                ruta_imagen = actividad.imagen.path
            except (AttributeError, ValueError):
                ruta_imagen = None

            if ruta_imagen and os.path.isfile(ruta_imagen):
                imagen = ruta_imagen

        agrupadas.setdefault(actividad.fecha, []).append(
            (
                actividad.descripcion,
                imagen,
            )
        )

    filas = []

    for dia in range(1, ultimo_dia + 1):
        fecha = date(anio, mes, dia)
        detalles = agrupadas.get(fecha, [])

        if not detalles:
            if fecha.weekday() == 5:
                detalles = [("SÁBADO", None)]
            elif fecha.weekday() == 6:
                detalles = [("DOMINGO", None)]
            else:
                detalles = [("SIN ACTIVIDADES REGISTRADAS", None)]

        filas.append((fecha, detalles))

    return filas


def informe_word(perfil, mes, anio, actividades, incluir_fotos=False):
    doc = Document()
    configurar_word(doc)

    titulo = (
        "INFORME DE ACTIVIDADES REALIZADAS DEL "
        f"MES DE {nombre_mes(mes)} DEL {anio}"
    )

    agregar_parrafo(
        doc,
        titulo,
        True,
        WD_ALIGN_PARAGRAPH.CENTER
    )

    doc.add_paragraph("")

    tabla = doc.add_table(rows=1, cols=3 if incluir_fotos else 2)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER

    encabezado = tabla.rows[0].cells
    encabezado[0].text = "FECHA"
    encabezado[1].text = "DETALLE"
    if incluir_fotos:
        encabezado[2].text = "FOTO"

    encabezado[0].width = Inches(1.25)
    encabezado[1].width = Inches(4.35 if incluir_fotos else 5.55)
    if incluir_fotos:
        encabezado[2].width = Inches(1.2)

    for celda in encabezado:
        for p in celda.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(185, 85, 35)

    for fecha, detalles in dias_informe(
        actividades, mes, anio
    ):
        celdas = tabla.add_row().cells

        celdas[0].text = fecha.strftime("%d/%m/%Y")
        celdas[1].text = ""
        if incluir_fotos:
            celdas[2].text = ""

        for indice, (detalle, imagen) in enumerate(detalles):
            if indice == 0:
                parrafo = celdas[1].paragraphs[0]
            else:
                parrafo = celdas[1].add_paragraph()

            parrafo.add_run("• " + detalle)

            if incluir_fotos and imagen:
                parrafo_foto = celdas[2].paragraphs[0]
                parrafo_foto.alignment = WD_ALIGN_PARAGRAPH.CENTER
                parrafo_foto.add_run().add_picture(
                    imagen,
                    width=Inches(1.0),
                )

        # Resaltado tenue de fines de semana sin actividades
        if fecha.weekday() >= 5 and detalles in (
            [("SÁBADO", None)], [("DOMINGO", None)]
        ):
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn

            for celda in celdas:
                tc_pr = celda._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:fill"), "F6D0B9")
                tc_pr.append(shd)

    doc.add_paragraph("\n")

    agregar_parrafo(
        doc,
        perfil.nombre_completo,
        True,
        WD_ALIGN_PARAGRAPH.CENTER
    )
    agregar_parrafo(
        doc,
        perfil.cargo,
        True,
        WD_ALIGN_PARAGRAPH.CENTER
    )

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def estilos_pdf():
    normal = ParagraphStyle(
        "NormalPersonalizado",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    justificado = ParagraphStyle(
        "JustificadoPersonalizado",
        parent=normal,
        alignment=TA_JUSTIFY,
    )

    centrado = ParagraphStyle(
        "CentradoPersonalizado",
        parent=normal,
        alignment=TA_CENTER
    )

    titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=centrado,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16
    )

    return normal, justificado, centrado, titulo


def construir_pdf(elementos):
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    documento.build(elementos)
    buffer.seek(0)
    return buffer


def carta_pdf(perfil, mes, anio, fecha, desde=None, hasta=None):
    datos = datos_solicitud(
        perfil, mes, anio, fecha, desde, hasta
    )

    normal, justificado, centrado, titulo = estilos_pdf()
    elementos = []

    elementos.append(
        Paragraph(
            escape(datos["lugar_fecha"]),
            ParagraphStyle(
                "Derecha",
                parent=normal,
                alignment=2
            )
        )
    )

    elementos.append(Spacer(1, 20))

    campos = [
        ("A:", perfil.destinatario, perfil.cargo_destinatario),
        ("VÍA:", perfil.via_1, perfil.cargo_via_1),
        ("VÍA:", perfil.via_2, perfil.cargo_via_2),
        ("DE:", perfil.nombre_completo, perfil.cargo),
    ]

    for etiqueta, nombre, cargo in campos:
        if nombre:
            elementos.append(
                Paragraph(
                    f"<b>{escape(etiqueta)}</b> {escape(nombre)}",
                    normal
                )
            )
            if cargo:
                elementos.append(
                    Paragraph(f"<b>{escape(cargo)}</b>", normal)
                )

    elementos.append(Spacer(1, 12))

    elementos.append(
        Paragraph(
            "<b>REF: " + escape(datos["referencia"]) + "</b>",
            normal
        )
    )

    elementos.append(Spacer(1, 12))

    for texto in [datos["introduccion"], datos["motivo"]]:
        elementos.append(Paragraph(escape(texto), justificado))

    elementos.append(
        Paragraph(
            "En la presente solicitud de pago, y en orden "
            f"del INSTRUCTIVO Nº{escape(perfil.numero_instructivo)} "
            "adjunto los siguientes documentos:",
            normal
        )
    )

    for anexo in datos["anexos"]:
        elementos.append(
            Paragraph("&#8226; " + escape(anexo), normal)
        )

    elementos.append(
        Paragraph(
            "Sin otro en particular me despido con las "
            "consideraciones más distinguidas.",
            normal
        )
    )

    elementos.append(Paragraph("Atentamente:", normal))
    elementos.append(Spacer(1, 50))

    elementos.append(
        Paragraph(
            f"<b>{escape(perfil.nombre_completo)}</b>",
            centrado
        )
    )
    elementos.append(
        Paragraph(f"<b>{escape(perfil.cargo)}</b>", centrado)
    )

    return construir_pdf(elementos)


def informe_pdf(perfil, mes, anio, actividades, incluir_fotos=False):
    normal, justificado, centrado, titulo = estilos_pdf()

    elementos = [
        Paragraph(
            "INFORME DE ACTIVIDADES REALIZADAS DEL "
            f"MES DE {nombre_mes(mes)} DEL {anio}",
            titulo
        ),
        Spacer(1, 20)
    ]

    estilo_detalle = ParagraphStyle(
        "Detalle",
        parent=normal,
        fontSize=9,
        leading=13,
        spaceAfter=3
    )

    encabezados = [
        Paragraph("<b>FECHA</b>", centrado),
        Paragraph("<b>DETALLE</b>", centrado),
    ]
    if incluir_fotos:
        encabezados.append(Paragraph("<b>FOTO</b>", centrado))
    filas = [encabezados]

    for fecha, detalles in dias_informe(
        actividades, mes, anio
    ):
        contenido = [
            Paragraph("&#8226; " + escape(d), estilo_detalle)
            for d, _ in detalles
        ]

        fila = [
            Paragraph(
                fecha.strftime("%d/%m/%Y"),
                estilo_detalle
            ),
            contenido,
        ]
        if incluir_fotos:
            fotos = [
                ReportLabImage(
                    imagen,
                    width=2.4 * cm,
                    height=2.4 * cm,
                    kind="proportional",
                )
                for _, imagen in detalles
                if imagen
            ]
            fila.append(fotos)
        filas.append(fila)

    anchos = [3 * cm, 14 * cm]
    if incluir_fotos:
        anchos = [3 * cm, 10 * cm, 4 * cm]
    tabla = Table(
        filas,
        colWidths=anchos,
        repeatRows=1,
        hAlign="CENTER"
    )

    estilos_tabla = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#B95523")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]

    for indice, (fecha, detalles) in enumerate(
        dias_informe(actividades, mes, anio), start=1
    ):
        if fecha.weekday() >= 5 and detalles in (
            [("SÁBADO", None)], [("DOMINGO", None)]
        ):
            estilos_tabla.append(
                (
                    "BACKGROUND",
                    (0, indice),
                    (-1, indice),
                    colors.HexColor("#F6D0B9")
                )
            )

    tabla.setStyle(TableStyle(estilos_tabla))

    elementos.append(tabla)
    elementos.append(Spacer(1, 50))

    elementos.append(
        KeepTogether([
            Paragraph(
                f"<b>{escape(perfil.nombre_completo)}</b>",
                centrado
            ),
            Paragraph(
                f"<b>{escape(perfil.cargo)}</b>",
                centrado
            )
        ])
    )

    return construir_pdf(elementos)
