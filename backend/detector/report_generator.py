import os
import tempfile
import datetime
import base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.units import inch

def generate_pdf_report(result_data, metadata=None):
    if metadata is None:
        metadata = {}
        
    filename = metadata.get("filename", "Unknown File")
    date_str = metadata.get("date", "")
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    analyst_name = metadata.get("analyst_name", "")
    if not analyst_name: analyst_name = "N/A"
    case_id = metadata.get("case_id", "")
    if not case_id: case_id = "N/A"
    notes = metadata.get("notes", "")

    fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    doc = SimpleDocTemplate(
        temp_pdf_path,
        pagesize=letter,
        rightMargin=inch, leftMargin=inch,
        topMargin=inch, bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        alignment=1, # Center
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        alignment=1,
        spaceAfter=40
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#003366'),
        spaceBefore=15,
        spaceAfter=10
    )
    normal_style = styles['Normal']
    
    elements = []

    is_forged = result_data.get("is_forged", False)
    confidence_score = result_data.get("confidence_score", 0.0)

    # PAGE 1: Cover
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("Digital Forensic Analysis Report", title_style))
    elements.append(Paragraph("Image Forgery Detection — SIFT + ELA Method", subtitle_style))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Details table
    cover_details = [
        ["Date and Time of Analysis:", date_str],
        ["File Analysed:", filename],
        ["Analyst Name:", analyst_name],
        ["Case ID:", case_id],
    ]
    t_cover = Table(cover_details, colWidths=[2.5*inch, 3.5*inch])
    t_cover.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
    ]))
    elements.append(t_cover)
    
    elements.append(Spacer(1, 1*inch))
    
    # Verdict box
    verdict_text = "FORGED" if is_forged else "AUTHENTIC"
    verdict_color = colors.HexColor('#CC0000') if is_forged else colors.HexColor('#006600')
    
    verdict_style = ParagraphStyle(
        'VerdictStyle',
        fontSize=36,
        textColor=verdict_color,
        alignment=1,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph(verdict_text, verdict_style))
    
    conf_style = ParagraphStyle(
        'ConfStyle',
        fontSize=16,
        alignment=1,
        spaceBefore=10
    )
    elements.append(Paragraph(f"Confidence Score: {confidence_score:.2f}%", conf_style))
    
    elements.append(PageBreak())

    # PAGE 2: Technical Details
    elements.append(Paragraph("Technical Details", title_style))
    
    elements.append(Paragraph("Detection Method", section_style))
    elements.append(Paragraph("<b>Scale-Invariant Feature Transform (SIFT):</b> Used to detect identical keypoint clusters within the image, which strongly indicates a copy-move forgery. SIFT is robust against rotation, scaling, and minor distortions.", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Error Level Analysis (ELA):</b> Highlights areas of the image that are at different compression levels. Resaved modified regions often exhibit higher error levels compared to the untouched background.", normal_style))
    
    elements.append(Paragraph("Detection Results Table", section_style))
    
    results_data = [
        ["Parameter", "Value", "Status"],
        ["Keypoints Detected", str(result_data.get("keypoints_detected", "N/A")), "Info"],
        ["Keypoints Matched", str(result_data.get("keypoints_matched", 0)), "Critical" if result_data.get("keypoints_matched", 0) > 0 else "Normal"],
        ["RANSAC Inliers", str(result_data.get("ransac_inliers", "N/A")), "Info"],
        ["ELA Mean Score", f"{result_data.get('ela_mean_score', 0):.2f}", "Info"],
        ["ELA Suspicious Flag", str(result_data.get("ela_suspicious", False)), "Alert" if result_data.get("ela_suspicious") else "Normal"],
        ["Confidence Score", f"{confidence_score:.2f}%", "Alert" if confidence_score > 50 else "Normal"],
    ]
    if "risk_level" in result_data:
        results_data.append(["Risk Level", result_data.get("risk_level", "NONE"), "Alert" if result_data.get("risk_level") in ["HIGH", "CRITICAL"] else "Normal"])

    t_results = Table(results_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(t_results)
    
    elements.append(PageBreak())

    # Helper function for images
    def create_image_element(b64_str, max_width=6.5*inch, max_height=3.5*inch):
        try:
            img_data = base64.b64decode(b64_str)
            fd_img, tmp_img = tempfile.mkstemp(suffix=".png")
            os.write(fd_img, img_data)
            os.close(fd_img)
            img = RLImage(tmp_img)
            aspect = img.imageWidth / float(img.imageHeight)
            if img.imageWidth > max_width:
                img.drawWidth = max_width
                img.drawHeight = max_width / aspect
            if img.drawHeight > max_height:
                img.drawHeight = max_height
                img.drawWidth = max_height * aspect
            return img, tmp_img
        except Exception as e:
            print(f"[Report] Error loading image: {e}")
            return Paragraph("Image not available.", normal_style), None

    temp_images = []

    # PAGE 3: Visual Evidence
    elements.append(Paragraph("Visual Evidence", title_style))
    
    cap_style = ParagraphStyle('Cap', parent=normal_style, alignment=1, spaceBefore=5, spaceAfter=20, fontName='Helvetica-Oblique')

    has_visuals = False
    
    if result_data.get("original_image_base64"):
        img_elem, tmp_img = create_image_element(result_data["original_image_base64"])
        if tmp_img: temp_images.append(tmp_img)
        elements.append(img_elem)
        elements.append(Paragraph("Original Image", cap_style))
        has_visuals = True

    if result_data.get("annotated_image_base64"):
        img_elem, tmp_img = create_image_element(result_data["annotated_image_base64"])
        if tmp_img: temp_images.append(tmp_img)
        elements.append(img_elem)
        elements.append(Paragraph("Annotated Image with Bounding Boxes", cap_style))
        has_visuals = True

    # Check for ELA heatmap (can be ela_image_base64 or heatmap_base64)
    if result_data.get("heatmap_base64"):
        img_elem, tmp_img = create_image_element(result_data["heatmap_base64"])
        if tmp_img: temp_images.append(tmp_img)
        elements.append(img_elem)
        elements.append(Paragraph("ELA Heatmap", cap_style))
        has_visuals = True
    elif result_data.get("ela_image_base64"):
        img_elem, tmp_img = create_image_element(result_data["ela_image_base64"])
        if tmp_img: temp_images.append(tmp_img)
        elements.append(img_elem)
        elements.append(Paragraph("ELA Heatmap", cap_style))
        has_visuals = True

    if not has_visuals:
        elements.append(Paragraph("No visual evidence available in the analysis result.", normal_style))

    elements.append(PageBreak())

    # PAGE 4: Findings and Regions
    elements.append(Paragraph("Findings and Regions", title_style))
    
    regions = result_data.get("regions", [])
    if regions:
        elements.append(Paragraph("Detected Suspicious Regions", section_style))
        region_data = [["X", "Y", "Width", "Height", "Label"]]
        for idx, r in enumerate(regions):
            region_data.append([str(r.get("x", "")), str(r.get("y", "")), str(r.get("w", "")), str(r.get("h", "")), f"Region {idx+1}"])
        
        t_regions = Table(region_data, colWidths=[1.2*inch]*5)
        t_regions.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ]))
        elements.append(t_regions)
    else:
        elements.append(Paragraph("No specific suspicious regions bounding boxes detected.", normal_style))
        
    elements.append(Spacer(1, 20))

    if result_data.get("document_flags"):
        elements.append(Paragraph("Document Flags", section_style))
        for flag in result_data.get("document_flags"):
            elements.append(Paragraph(f"• {flag}", normal_style))
        elements.append(Spacer(1, 20))

    elements.append(Paragraph("Risk Assessment", section_style))
    summary_text = result_data.get("summary", "No assessment available.")
    
    if summary_text:
        elements.append(Paragraph(summary_text, normal_style))
        
    if notes:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Analyst Notes:</b>", normal_style))
        elements.append(Paragraph(notes, normal_style))
    
    elements.append(PageBreak())

    # PAGE 5: Disclaimer
    elements.append(Paragraph("Disclaimer", title_style))
    
    disc_style = ParagraphStyle(
        'DiscStyle',
        parent=normal_style,
        fontSize=12,
        spaceAfter=15,
        alignment=1
    )
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("This report is generated automatically using algorithmic analysis.", disc_style))
    elements.append(Paragraph("Results should be verified by a certified digital forensics expert.", disc_style))
    elements.append(Paragraph("Not admissible as sole evidence in legal proceedings.", disc_style))
    
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("Tool Name: Digital Forensics Report Generator", disc_style))
    elements.append(Paragraph("Version: 1.0.0", disc_style))
    elements.append(Paragraph(f"Date Generated: {date_str}", disc_style))

    # Header and footer
    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(inch, letter[1] - 0.5 * inch, "Digital Forensics Report Generator")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {page_num}")
        canvas.restoreState()

    try:
        doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    except Exception as e:
        print(f"[Report] Error building PDF doc: {e}")
        # Build without images if there is an issue with images being too large or something
        pass
    
    # cleanup temp images
    for tmp in temp_images:
        try:
            os.remove(tmp)
        except:
            pass
            
    return temp_pdf_path
