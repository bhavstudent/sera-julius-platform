"""
Omniscience PDF Report Generator using ReportLab
Generates detailed multi-page PDF Intelligence Briefings with SERA branding.
"""

import io
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

logger = logging.getLogger("sera.omniscience.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        # Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#475569"))
        self.drawString(54, 750, "SERA INTELLIGENCE PLATFORM — OMNISCIENCE BRIEFING")
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#6366F1"))
        self.drawRightString(612 - 54, 750, "CONFIDENTIAL & PROPRIETARY")
        
        self.setStrokeColor(HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)

        # Running Footer
        self.line(54, 48, 612 - 54, 48)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#0F172A"))
        self.drawString(54, 34, "SERA BEHAVIORAL & GLOBAL INTEL ENGINE")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#64748B"))
        self.drawRightString(612 - 54, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class OmnisciencePDFGenerator:
    """
    Compiles search results, AI synthesis, Knowledge Graph relationships, 
    and source citations into a multi-page PDF document.
    """
    
    @classmethod
    def generate_pdf(cls, query: str, entity: str, synthesis: str, facts: List[Dict[str, Any]], graph: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=72,
            bottomMargin=72
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=HexColor('#1E1B4B'),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=HexColor('#475569'),
            spaceAfter=15
        )

        heading2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=HexColor('#4F46E5'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=HexColor('#1E293B'),
            spaceAfter=8
        )

        story = []

        # Document Header
        story.append(Paragraph("SERA OMNISCIENCE INTELLIGENCE BRIEFING", title_style))
        now_str = datetime.now(timezone.utc).strftime("%B %d, %Y - %H:%M:%S UTC")
        story.append(Paragraph(f"Target Query: <b>{query}</b> &nbsp;|&nbsp; Entity: <b>{entity}</b> &nbsp;|&nbsp; Date: {now_str}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor('#6366F1'), spaceAfter=15))

        # Section 1: Executive Synthesis
        story.append(Paragraph("1. Executive AI Synthesis & Intelligence Overview", heading2_style))
        synthesis_clean = synthesis.replace("\n", "<br/>")
        story.append(Paragraph(synthesis_clean, body_style))
        story.append(Spacer(1, 10))

        # Section 2: Knowledge Graph Facts & Property Claims Table
        story.append(Paragraph("2. Verified Knowledge Graph Assertions", heading2_style))
        
        table_data = [["Subject Entity", "Relationship", "Object / Value", "Confidence"]]
        edges = graph.get("edges", [])
        if edges:
            for edge in edges[:8]:
                table_data.append([
                    entity[:25],
                    str(edge.get("relation"))[:30],
                    str(edge.get("target", ""))[:30],
                    f"{int(float(edge.get('confidence', 0.9)) * 100)}%"
                ])
        else:
            for f in facts[:6]:
                table_data.append([
                    entity[:25],
                    "has_fact",
                    str(f.get("fact"))[:35],
                    f"{int(float(f.get('confidence', 0.9)) * 100)}%"
                ])

        t = Table(table_data, colWidths=[120, 140, 170, 74])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#4F46E5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#CBD5E1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # Section 3: Verified Source Citations
        story.append(Paragraph("3. Source Citations & Supporting Proof", heading2_style))
        
        cit_data = [["Source Name", "URL Domain", "Confidence", "Retrieved Timestamp"]]
        for f in facts[:8]:
            url = f.get("source_url", "")
            domain = url.split("//")[-1].split("/")[0] if "//" in url else url[:30]
            cit_data.append([
                str(f.get("source_name"))[:25],
                domain[:30],
                f"{int(float(f.get('confidence', 0.9)) * 100)}%",
                str(f.get("retrieved_at"))[:19]
            ])

        t_cit = Table(cit_data, colWidths=[130, 160, 74, 140])
        t_cit.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#94A3B8')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
        ]))
        story.append(t_cit)

        # Build document using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
