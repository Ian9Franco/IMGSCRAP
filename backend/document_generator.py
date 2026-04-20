import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_property_doc(path, title, description, details_list):
    """
    Generates a Word document with the property details.
    """
    try:
        doc = Document()
        
        # Title
        title_para = doc.add_heading(title, 0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Space
        doc.add_paragraph()
        
        # Details (Features)
        if details_list:
            doc.add_heading('Características Principales', level=1)
            for detail in details_list:
                doc.add_paragraph(detail, style='List Bullet')
        
        # Space
        doc.add_paragraph()
        
        # Description
        if description:
            doc.add_heading('Descripción', level=1)
            desc_para = doc.add_paragraph(description)
            desc_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
        # Save document
        filename = os.path.join(path, "copy_propiedad.docx")
        doc.save(filename)
        return True, filename
    except Exception as e:
        print(f"Error generating document: {e}")
        return False, str(e)
