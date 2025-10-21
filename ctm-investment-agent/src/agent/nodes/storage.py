# src/agent/nodes/storage.py
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import re

from ..state import ProjectState

# --- IMPORTACIONES DE REPORTLAB ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

REPORTS_DIR = "reports"

# ============================================================================
# COLORES CORPORATIVOS COTECMAR
# ============================================================================
COTECMAR_BLUE = colors.HexColor('#0066CC')
COTECMAR_DARK_BLUE = colors.HexColor('#003366')
COTECMAR_GRAY = colors.HexColor('#4A4A4A')
COTECMAR_LIGHT_GRAY = colors.HexColor('#E8E8E8')

# ============================================================================
# CONFIGURACIÓN DE ESTILOS
# ============================================================================
def get_styles():
    """Crea una hoja de estilos personalizada con identidad COTECMAR."""
    styles = getSampleStyleSheet()
    
    # Título Principal (H1)
    if 'CotecmarH1' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarH1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=COTECMAR_DARK_BLUE,
            spaceAfter=16,
            spaceBefore=12,
            alignment=TA_LEFT,
        ))
    
    # Subtítulo (H2)
    if 'CotecmarH2' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=COTECMAR_BLUE,
            spaceAfter=12,
            spaceBefore=10,
            alignment=TA_LEFT,
        ))
    
    # Subtítulo menor (H3)
    if 'CotecmarH3' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarH3',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=COTECMAR_GRAY,
            spaceAfter=8,
            spaceBefore=8,
            alignment=TA_LEFT,
        ))
    
    # Texto del cuerpo
    if 'CotecmarBody' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            spaceBefore=4,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#333333'),
        ))
    
    # Bullets
    if 'CotecmarBullet' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarBullet',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3,
            textColor=colors.HexColor('#333333'),
        ))
    
    # Metadatos
    if 'CotecmarMetadata' not in styles:
        styles.add(ParagraphStyle(
            name='CotecmarMetadata',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=9,
            textColor=COTECMAR_GRAY,
            spaceAfter=4,
        ))
    
    return styles

# ============================================================================
# PARSER DE MARKDOWN - LIMPIO Y SIN DUPLICADOS
# ============================================================================
def parse_markdown_to_flowables(text: str, styles: dict):
    """Convierte Markdown a Flowables de ReportLab."""
    flowables = []
    lines = text.split('\n')
    
    in_list = False
    content_started = False
    
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        
        if not line_stripped:
            if in_list:
                flowables.append(Spacer(1, 0.1*cm))
            continue

        # IGNORAR las primeras líneas que contienen metadatos redundantes
        if not content_started:
            # Saltar líneas que contengan información de portada
            if any(keyword in line_stripped for keyword in [
                'ANÁLISIS DE OPORTUNIDAD ESPECÍFICA',
                'PROPUESTA CONCEPTUAL',
                'Proyecto:',
                'Oportunidad Analizada:',
                'Fecha de Generación:'
            ]):
                continue
            
            # Si encontramos un encabezado real (##), empezamos el contenido
            if line_stripped.startswith('##') or line_stripped.startswith('# '):
                content_started = True
                # Continuar procesando esta línea

        # Convertir markdown a HTML
        line_stripped = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_stripped)
        line_stripped = re.sub(r'(?<!\*)\*(?!\*)([^\*]+)\*(?!\*)', r'<i>\1</i>', line_stripped)

        # Procesar encabezados
        if line_stripped.startswith('# '):
            if in_list:
                flowables.append(Spacer(1, 0.3*cm))
                in_list = False
            flowables.append(Spacer(1, 0.3*cm))
            flowables.append(Paragraph(line_stripped[2:], styles['CotecmarH1']))
            flowables.append(Spacer(1, 0.2*cm))
            
        elif line_stripped.startswith('## '):
            if in_list:
                flowables.append(Spacer(1, 0.2*cm))
                in_list = False
            flowables.append(Spacer(1, 0.2*cm))
            flowables.append(Paragraph(line_stripped[3:], styles['CotecmarH2']))
            flowables.append(Spacer(1, 0.15*cm))
            
        elif line_stripped.startswith('### '):
            if in_list:
                flowables.append(Spacer(1, 0.15*cm))
                in_list = False
            flowables.append(Spacer(1, 0.15*cm))
            flowables.append(Paragraph(line_stripped[4:], styles['CotecmarH3']))
            flowables.append(Spacer(1, 0.1*cm))
            
        elif line_stripped.startswith('---'):
            if in_list:
                in_list = False
            flowables.append(Spacer(1, 0.4*cm))
            line_table = Table([['']], colWidths=[17*cm])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 1, COTECMAR_BLUE),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            flowables.append(line_table)
            flowables.append(Spacer(1, 0.4*cm))
            
        elif line_stripped.startswith('* ') or line_stripped.startswith('- '):
            bullet_text = line_stripped[2:]
            flowables.append(Paragraph(
                f'<font color="{COTECMAR_BLUE}">●</font> {bullet_text}', 
                styles['CotecmarBullet']
            ))
            in_list = True
            
        else:
            if content_started:  # Solo agregar texto si ya empezó el contenido real
                if in_list:
                    flowables.append(Spacer(1, 0.15*cm))
                    in_list = False
                flowables.append(Paragraph(line_stripped, styles['CotecmarBody']))
    
    return flowables

# ============================================================================
# PLANTILLA SIMPLIFICADA - LOGO PEQUEÑO SIN SOBREPOSICIÓN
# ============================================================================
def page_template(canvas, doc):
    """Dibuja solo el logo discreto y el footer, sin sobreponerse al contenido."""
    canvas.saveState()
    
    # --- LOGO EN ESQUINA SUPERIOR DERECHA ---
    logo_path = Path(__file__).parent.parent / 'static' / 'CotecmarLogo.png'
    
    if logo_path.is_file():
        try:
            # Logo pequeño en la esquina, por encima del área de contenido
            canvas.drawImage(
                str(logo_path), 
                doc.width + doc.leftMargin - 2*cm,  # Posición desde la derecha
                doc.height + doc.bottomMargin + 0.5*cm,  # Por encima del contenido
                width=2*cm, 
                height=0.7*cm,
                preserveAspectRatio=True, 
                mask='auto'
            )
        except Exception as e:
            print(f"   ⚠️ No se pudo cargar el logo: {e}")

    # --- FOOTER SIMPLE ---
    # Línea decorativa
    canvas.setStrokeColor(COTECMAR_BLUE)
    canvas.setLineWidth(1)
    canvas.line(
        doc.leftMargin, 
        doc.bottomMargin - 0.5*cm, 
        doc.width + doc.leftMargin, 
        doc.bottomMargin - 0.5*cm
    )
    
    # Información del footer
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(COTECMAR_GRAY)
    canvas.drawString(
        doc.leftMargin, 
        doc.bottomMargin - 0.8*cm, 
        "Corporación de Ciencia y Tecnología para el Desarrollo de la Industria Naval, Marítima y Fluvial - COTECMAR"
    )
    
    canvas.setFont('Helvetica', 7)
    canvas.drawString(
        doc.leftMargin, 
        doc.bottomMargin - 1.05*cm, 
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
    )
    
    # Número de página
    canvas.setFont('Helvetica-Bold', 9)
    canvas.setFillColor(COTECMAR_BLUE)
    canvas.drawRightString(
        doc.width + doc.leftMargin, 
        doc.bottomMargin - 0.8*cm, 
        f"Página {canvas.getPageNumber()}"
    )
    
    canvas.restoreState()

# ============================================================================
# FUNCIÓN PRINCIPAL - SIN PÁGINA DE PRESENTACIÓN
# ============================================================================
def save_report_as_pdf(state: ProjectState) -> Dict[str, Any]:
    """Guarda el reporte como PDF profesional SIN página de presentación."""
    print("\n" + "="*80)
    print("NODO: Guardando Reporte como PDF")
    print("="*80)

    report_content = state.get("improvement_report")
    if not report_content:
        print("   ⚠️ No hay contenido de reporte para guardar")
        return {}
    
    report_type = state.get("report_type", "general")
    subfolder = os.path.join(REPORTS_DIR, report_type)
    
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
        print(f"   📁 Directorio creado: {subfolder}")
    
    # Nombre del archivo
    file_prefix = "Reporte_General" if report_type == "general" else f"Analisis_Oportunidad_{state.get('action_input', 'idx')}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    thread_id_short = state.get("thread_id", "unknown")[:8]
    file_name = f"{file_prefix}_{thread_id_short}_{timestamp}.pdf"
    file_path = os.path.join(subfolder, file_name)

    try:
        # Crear documento con márgenes ajustados
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            topMargin=2.5*cm,  # Margen superior reducido
            bottomMargin=2.5*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )

        # Metadatos
        doc.project_title = state.get("project_title", "Sin título")
        doc.report_type = report_type
        doc.author = "COTECMAR"
        doc.title = file_prefix

        # Generar estilos
        print("   🎨 Generando estilos...")
        styles = get_styles()
        
        # Crear historia - SOLO CONTENIDO, SIN PORTADA
        story = []
        
        # Contenido directo (sin portada)
        print("   📝 Parseando contenido...")
        story.extend(parse_markdown_to_flowables(report_content, styles))

        # Construir PDF
        print("   🔨 Construyendo PDF...")
        doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
        
        print(f"   ✅ Reporte guardado exitosamente")
        print(f"   📍 {file_path}")

        # Actualizar estado
        existing_paths = state.get("report_paths", [])
        updated_paths = existing_paths + [file_path]
        
        return {
            "report_paths": updated_paths,
            "improvement_report": None,
            "report_type": None,
            "messages": [{
                "role": "assistant",
                "content": f"✅ Reporte PDF generado exitosamente:\n`{file_path}`"
            }]
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "messages": [{
                "role": "assistant",
                "content": f"❌ Error al generar el PDF: {str(e)}"
            }]
        }