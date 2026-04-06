from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def create_presentation():
    # 1. Initialize presentation
    prs = Presentation()

    # ---------------------------------------------------------
    # Diapositiva 1: El Propósito (El Problema y la Solución)
    # ---------------------------------------------------------
    # Usar un layout en blanco (index 6 suele ser blank en la plantilla por defecto)
    blank_slide_layout = prs.slide_layouts[6]
    slide1 = prs.slides.add_slide(blank_slide_layout)

    # Fondo blanco (por defecto en el blank layout suele ser blanco, pero aseguramos)
    background1 = slide1.background
    fill1 = background1.fill
    fill1.solid()
    fill1.fore_color.rgb = RGBColor(255, 255, 255)

    # Agregar caja de texto en el centro
    # Centrar horizontal y verticalmente usando dimensiones de la diapositiva
    # Diapositiva por defecto: 10 pulgadas de ancho por 7.5 pulgadas de alto
    left = Inches(1)
    top = Inches(3)
    width = Inches(8)
    height = Inches(1.5)

    txBox1 = slide1.shapes.add_textbox(left, top, width, height)
    tf1 = txBox1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "DATOS TRANSACCIONALES CRUDOS   ➔   ⚙️   ➔   DECISIONES ESTRATÉGICAS RENTABLES"
    p.alignment = PP_ALIGN.CENTER
    p.font.bold = True
    p.font.size = Pt(24)
    p.font.color.rgb = RGBColor(0, 0, 0)
    p.font.name = 'Arial'


    # ---------------------------------------------------------
    # Diapositiva 2: La Metodología (Los 5 Pasos)
    # ---------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)

    background2 = slide2.background
    fill2 = background2.fill
    fill2.solid()
    fill2.fore_color.rgb = RGBColor(250, 250, 250) # Gris muy claro

    # Título superior
    title_box2 = slide2.shapes.add_textbox(Inches(1), Inches(0.5), Inches(8), Inches(1))
    tf_title2 = title_box2.text_frame
    p_title2 = tf_title2.paragraphs[0]
    p_title2.text = "ESTRUCTURA METODOLÓGICA"
    p_title2.alignment = PP_ALIGN.CENTER
    p_title2.font.bold = True
    p_title2.font.size = Pt(36)
    p_title2.font.name = 'Arial'

    # Texto central: lista numerada
    content_box2 = slide2.shapes.add_textbox(Inches(1.5), Inches(2), Inches(7), Inches(4.5))
    tf_content2 = content_box2.text_frame
    tf_content2.word_wrap = True

    steps = [
        "1. Diagnóstico: Auditoría de bases de datos y mapeo de procesos.",
        "2. Estructuración: Diseño dimensional y proceso ETL.",
        "3. Formulación: Modelado matemático de KPIs operativos.",
        "4. Desarrollo Visual: Tablero de Control interactivo (BI).",
        "5. Evaluación Económica: Viabilidad financiera (VAN y TIR)."
    ]

    for i, step in enumerate(steps):
        if i == 0:
            p2 = tf_content2.paragraphs[0]
        else:
            p2 = tf_content2.add_paragraph()
            p2.space_before = Pt(14)

        p2.text = step
        p2.font.size = Pt(24)
        p2.font.name = 'Arial'
        p2.font.color.rgb = RGBColor(50, 50, 50)


    # ---------------------------------------------------------
    # Diapositiva 3: El Ancla (Las Contribuciones)
    # ---------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)

    # Fondo azul marino oscuro
    background3 = slide3.background
    fill3 = background3.fill
    fill3.solid()
    fill3.fore_color.rgb = RGBColor(10, 25, 60) # Azul marino oscuro

    # Título superior
    title_box3 = slide3.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
    tf_title3 = title_box3.text_frame
    p_title3 = tf_title3.paragraphs[0]
    p_title3.text = "CONTRIBUCIONES DEL PROYECTO"
    p_title3.alignment = PP_ALIGN.CENTER
    p_title3.font.bold = True
    p_title3.font.size = Pt(40)
    p_title3.font.color.rgb = RGBColor(255, 255, 255)
    p_title3.font.name = 'Arial'

    # Texto central
    content_box3 = slide3.shapes.add_textbox(Inches(1.5), Inches(3), Inches(7), Inches(3))
    tf_content3 = content_box3.text_frame
    tf_content3.word_wrap = True

    contributions = [
        "I. Arquitectura de Datos Saneada",
        "II. Motor de KPIs Operativos",
        "III. Viabilidad Financiera Demostrada"
    ]

    for i, contrib in enumerate(contributions):
        if i == 0:
            p3 = tf_content3.paragraphs[0]
        else:
            p3 = tf_content3.add_paragraph()
            p3.space_before = Pt(30)

        p3.text = contrib
        p3.alignment = PP_ALIGN.CENTER
        p3.font.bold = True
        p3.font.size = Pt(28)
        p3.font.color.rgb = RGBColor(255, 255, 255)
        p3.font.name = 'Arial'

    # 4. Save presentation
    prs.save('Presentacion_BI.pptx')
    print("Archivo 'Presentacion_BI.pptx' generado exitosamente.")

if __name__ == '__main__':
    create_presentation()
