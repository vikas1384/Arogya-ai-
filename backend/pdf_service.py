import os
from typing import List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from models import Session, Message, HealthGuide, LanguageEnum

class PDFService:
    def __init__(self):
        # Create reports directory if it doesn't exist
        self.reports_dir = "/app/backend/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB'),
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.HexColor('#A23B72'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Warning style
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Traditional remedy style
        self.styles.add(ParagraphStyle(
            name='TraditionalRemedy',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#F18F01'),
            fontName='Helvetica',
            spaceAfter=8
        ))

    def generate_health_report(
        self, 
        session: Session, 
        health_guide: HealthGuide, 
        messages: Optional[List[Message]] = None,
        include_chat_history: bool = False
    ) -> str:
        """Generate comprehensive health report PDF"""
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dr_arogya_health_report_{session.id}_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Add header
        story.extend(self._create_header(session, health_guide))
        
        # Add main health guide sections
        story.extend(self._create_health_guide_content(health_guide))
        
        # Add traditional remedies section
        if health_guide.traditional_remedies:
            story.extend(self._create_traditional_remedies_section(health_guide))
        
        # Add chat history if requested
        if include_chat_history and messages:
            story.extend(self._create_chat_history_section(messages))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        return filename

    def _create_header(self, session: Session, health_guide: HealthGuide) -> List:
        """Create PDF header section"""
        
        content = []
        
        # Title
        title = "Dr. Arogya - Health Consultation Report" if health_guide.language == LanguageEnum.ENGLISH else "डॉ. आरोग्य - स्वास्थ्य सलाह रिपोर्ट"
        content.append(Paragraph(title, self.styles['CustomTitle']))
        content.append(Spacer(1, 20))
        
        # Report details table
        report_data = [
            ["Session ID:", session.id],
            ["Generated On:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["Language:", session.language.value.title() if session.language else "English"],
            ["Consultation Stage:", session.current_stage.value.replace('_', ' ').title()]
        ]
        
        table = Table(report_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 30))
        
        return content

    def _create_health_guide_content(self, health_guide: HealthGuide) -> List:
        """Create main health guide content sections"""
        
        content = []
        
        # Symptom Summary
        content.append(Paragraph("🩺 Understanding Your Symptoms", self.styles['SectionHeader']))
        content.append(Paragraph(health_guide.symptom_summary, self.styles['CustomBodyText']))
        content.append(Spacer(1, 15))
        
        # Possible Conditions
        content.append(Paragraph("🔍 Potential Areas for Your Doctor to Explore", self.styles['SectionHeader']))
        for condition in health_guide.possible_conditions:
            content.append(Paragraph(f"• {condition}", self.styles['CustomBodyText']))
        content.append(Spacer(1, 15))
        
        # OTC Recommendations  
        content.append(Paragraph("💊 Over-the-Counter Care Suggestions", self.styles['SectionHeader']))
        for recommendation in health_guide.otc_recommendations:
            content.append(Paragraph(f"• {recommendation}", self.styles['CustomBodyText']))
        content.append(Spacer(1, 15))
        
        # Warning Signs
        content.append(Paragraph("⚠️ Important Warning Signs", self.styles['SectionHeader']))
        content.append(Paragraph(
            "Please seek immediate medical attention if you experience any of the following:",
            self.styles['Warning']
        ))
        for warning in health_guide.warning_signs:
            content.append(Paragraph(f"• {warning}", self.styles['Warning']))
        content.append(Spacer(1, 15))
        
        # Dietary Advice
        content.append(Paragraph("🥗 Nutritional Recommendations", self.styles['SectionHeader']))
        for advice in health_guide.dietary_advice:
            content.append(Paragraph(f"• {advice}", self.styles['CustomBodyText']))
        content.append(Spacer(1, 15))
        
        # Lifestyle Tips
        content.append(Paragraph("🌤️ Lifestyle Modifications", self.styles['SectionHeader']))
        for tip in health_guide.lifestyle_tips:
            content.append(Paragraph(f"• {tip}", self.styles['CustomBodyText']))
        content.append(Spacer(1, 15))
        
        # When to See Doctor
        content.append(Paragraph("🆘 When to Seek Medical Care", self.styles['SectionHeader']))
        for guideline in health_guide.when_to_see_doctor:
            content.append(Paragraph(f"• {guideline}", self.styles['CustomBodyText']))
        content.append(Spacer(1, 20))
        
        return content

    def _create_traditional_remedies_section(self, health_guide: HealthGuide) -> List:
        """Create traditional remedies section"""
        
        content = []
        
        title = "🌿 दादी माँ के नुस्खे (Traditional Grandmother's Remedies)" if health_guide.language == LanguageEnum.ENGLISH else "🌿 पारंपरिक घरेलू नुस्खे"
        content.append(Paragraph(title, self.styles['SectionHeader']))
        
        content.append(Paragraph(
            "These time-tested traditional remedies have been passed down through generations. "
            "While they may provide comfort, they should complement, not replace, medical treatment.",
            self.styles['CustomBodyText']
        ))
        content.append(Spacer(1, 12))
        
        for remedy in health_guide.traditional_remedies:
            # Remedy name
            content.append(Paragraph(f"<b>{remedy.name}</b>", self.styles['TraditionalRemedy']))
            
            # Ingredients
            ingredients_text = "Ingredients: " + ", ".join(remedy.ingredients)
            content.append(Paragraph(ingredients_text, self.styles['CustomBodyText']))
            
            # Preparation
            content.append(Paragraph(f"<b>Preparation:</b> {remedy.preparation}", self.styles['CustomBodyText']))
            
            # Usage
            content.append(Paragraph(f"<b>Usage:</b> {remedy.usage}", self.styles['CustomBodyText']))
            
            # Benefits
            content.append(Paragraph(f"<b>Benefits:</b> {remedy.benefits}", self.styles['CustomBodyText']))
            
            content.append(Spacer(1, 10))
        
        return content

    def _create_chat_history_section(self, messages: List[Message]) -> List:
        """Create chat history section"""
        
        content = []
        
        content.append(PageBreak())
        content.append(Paragraph("💬 Conversation Summary", self.styles['SectionHeader']))
        content.append(Paragraph(
            "This section contains a summary of your conversation with Dr. Arogya for your doctor's reference.",
            self.styles['BodyText']
        ))
        content.append(Spacer(1, 15))
        
        # Create conversation table
        chat_data = [["Time", "Speaker", "Message"]]
        
        for message in messages:
            time_str = message.timestamp.strftime("%H:%M")
            speaker = "You" if message.sender == "user" else "Dr. Arogya"
            
            # Truncate long messages
            message_text = message.content[:200] + "..." if len(message.content) > 200 else message.content
            
            chat_data.append([time_str, speaker, message_text])
        
        table = Table(chat_data, colWidths=[1*inch, 1.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        return content

    def _create_footer(self) -> List:
        """Create PDF footer section"""
        
        content = []
        
        content.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer = """
        <b>IMPORTANT MEDICAL DISCLAIMER</b><br/><br/>
        This report is generated by Dr. Arogya, an AI health assistant, and is intended for informational purposes only. 
        It does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare 
        professionals for medical concerns. In case of medical emergencies, contact your local emergency services immediately.<br/><br/>
        
        <b>About Dr. Arogya:</b> An AI-powered health companion designed to help you prepare for medical consultations 
        and provide supportive health information. This system combines modern AI technology with traditional 
        wellness wisdom to support your healthcare journey.<br/><br/>
        
        Generated by Arogya AI - Your Digital Health Companion
        """
        
        content.append(Paragraph(disclaimer, self.styles['BodyText']))
        
        return content

    def get_report_path(self, filename: str) -> str:
        """Get full path to generated report"""
        return os.path.join(self.reports_dir, filename)

    def cleanup_old_reports(self, days_old: int = 7):
        """Clean up reports older than specified days"""
        
        try:
            import glob
            import time
            
            current_time = time.time()
            
            for filepath in glob.glob(os.path.join(self.reports_dir, "*.pdf")):
                creation_time = os.path.getctime(filepath)
                
                if (current_time - creation_time) > (days_old * 24 * 3600):
                    os.remove(filepath)
                    print(f"Cleaned up old report: {filepath}")
                    
        except Exception as e:
            print(f"Error cleaning up reports: {e}")