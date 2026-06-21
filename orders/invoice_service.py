import io
from decimal import Decimal
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_invoice_pdf(order):
    """
    Generates a professional tax-compliant PDF invoice in memory using ReportLab.
    Returns the raw PDF bytes.
    """
    buffer = io.BytesIO()
    
    # Page setup - 0.5 inch margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Palette
    brand_dark = colors.HexColor("#1e293b")
    brand_blue = colors.HexColor("#4f46e5")
    text_dark = colors.HexColor("#0f172a")
    text_muted = colors.HexColor("#64748b")
    bg_light = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#e2e8f0")
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=brand_dark
    )
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=brand_blue,
        alignment=2 # Right aligned
    )
    header_left = ParagraphStyle(
        'HeaderLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_muted
    )
    header_right = ParagraphStyle(
        'HeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        alignment=2 # Right aligned
    )
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=text_dark
    )
    total_lbl = ParagraphStyle(
        'TotalLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=text_dark,
        alignment=2
    )
    total_val = ParagraphStyle(
        'TotalVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=brand_blue,
        alignment=2
    )
    footer_text = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=text_muted,
        alignment=1 # Centered
    )

    # 1. Header Grid (Brand Left, Invoice Info Right)
    brand_logo = "⚡ <b>PremiumShop AI</b>"
    logo_para = Paragraph(f"<font color='#4f46e5' size='22'>{brand_logo}</font>", title_style)
    meta_para = Paragraph("<b>TAX INVOICE / BILL OF SUPPLY</b>", subtitle_style)
    
    header_data = [
        [logo_para, meta_para]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 4 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    
    # 2. Party details grid (Vendor details Left, Invoice details Right)
    vendor_details = """
    <b>Sold By:</b>
    PremiumShop AI India Private Limited
    Outer Ring Road, Devarabisanahalli,
    Bangalore, Karnataka - 560103, India
    <b>GSTIN:</b> 29AAACP9999A1Z1
    """
    
    # Extract recipient name & contact from address snapshot
    shipping_address_clean = order.shipping_address_snapshot
    
    invoice_meta = f"""
    <b>Invoice Number:</b> INV-{order.order_number}
    <b>Order Number:</b> {order.order_number}
    <b>Order Date:</b> {order.created_at.strftime('%d-%b-%Y %I:%M %p')}
    <b>Payment Method:</b> {order.get_payment_method_display()}
    <b>Payment Status:</b> {order.get_payment_status_display()}
    """
    
    details_data = [
        [Paragraph(vendor_details.replace('\n', '<br/>'), header_left), Paragraph(invoice_meta.replace('\n', '<br/>'), header_right)]
    ]
    details_table = Table(details_data, colWidths=[3.75 * inch, 3.75 * inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 1, border_color),
        ('LINEABOVE', (0,0), (-1,-1), 1, border_color),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 12))
    
    # Shipping info header
    shipping_header_data = [
        [Paragraph("<b>Shipping / Billing Address:</b>", table_cell_bold), ""]
    ]
    shipping_header_table = Table(shipping_header_data, colWidths=[7.5 * inch, 0])
    shipping_header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(shipping_header_table)
    
    shipping_para_data = [
        [Paragraph(shipping_address_clean.replace('\n', '<br/>'), header_left)]
    ]
    shipping_table = Table(shipping_para_data, colWidths=[7.5 * inch])
    shipping_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (-1,-1), 0.5, border_color),
        ('LINERIGHT', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(shipping_table)
    story.append(Spacer(1, 15))
    
    # 3. Items list table
    items_header = [
        Paragraph("Description", table_hdr),
        Paragraph("Qty", table_hdr),
        Paragraph("Unit Price (Net)", table_hdr),
        Paragraph("GST Rate", table_hdr),
        Paragraph("Tax Amount", table_hdr),
        Paragraph("Total Price", table_hdr)
    ]
    
    table_rows = [items_header]
    
    total_tax_sum = Decimal('0.00')
    
    for idx, item in enumerate(order.items.all(), 1):
        # Assuming tax is 18% GST (inclusive). Calculate net price and tax amount.
        total_price = Decimal(str(item.price)) * item.quantity
        gst_multiplier = Decimal('1.18')
        net_unit_price = Decimal(str(item.price)) / gst_multiplier
        net_total = net_unit_price * item.quantity
        tax_amount = total_price - net_total
        
        total_tax_sum += tax_amount
        
        desc_text = f"<b>{item.product.name}</b>"
        if item.variant:
            desc_text += f"<br/><font color='#64748b' size='7.5'>Variant: {item.variant.name}: {item.variant.value}</font>"
        
        row = [
            Paragraph(desc_text, table_cell),
            Paragraph(str(item.quantity), table_cell),
            Paragraph(f"₹{net_unit_price:.2f}", table_cell),
            Paragraph("18% (GST)", table_cell),
            Paragraph(f"₹{tax_amount:.2f}", table_cell),
            Paragraph(f"₹{total_price:.2f}", table_cell_bold)
        ]
        table_rows.append(row)
        
    # Col widths summing up to 7.5 inches (540 pt)
    # Col widths: Description(3.25), Qty(0.5), Unit Price(1.0), GST Rate(0.8), Tax Amount(1.0), Total Price(1.0)
    col_widths = [3.25 * inch, 0.5 * inch, 1.0 * inch, 0.8 * inch, 1.0 * inch, 0.95 * inch]
    
    items_table = Table(table_rows, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_dark),
        ('ALIGN', (1,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    # 4. Totals Grid (CGST/SGST itemized breakdown)
    # CGST (9%) + SGST (9%)
    cgst_tax = total_tax_sum / Decimal('2.00')
    sgst_tax = total_tax_sum / Decimal('2.00')
    
    totals_rows = [
        [Paragraph("Subtotal (incl. tax):", total_lbl), Paragraph(f"₹{order.subtotal:.2f}", total_val)],
        [Paragraph("CGST (9.0%):", total_lbl), Paragraph(f"₹{cgst_tax:.2f}", total_val)],
        [Paragraph("SGST (9.0%):", total_lbl), Paragraph(f"₹{sgst_tax:.2f}", total_val)],
    ]
    
    if order.discount > 0:
        totals_rows.append([Paragraph("Discount Applied:", total_lbl), Paragraph(f"- ₹{order.discount:.2f}", total_val)])
    
    totals_rows.append([Paragraph("Shipping Charge:", total_lbl), Paragraph(f"₹{order.shipping_charge:.2f}", total_val)])
    totals_rows.append([Paragraph("<b>Grand Total:</b>", total_lbl), Paragraph(f"<b>₹{order.total:.2f}</b>", total_val)])
    
    totals_table = Table(totals_rows, colWidths=[5.5 * inch, 2.0 * inch])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 35))
    
    # 5. Bottom Legal Notice & Signature Simulation
    story.append(Paragraph("This is a computer-generated tax invoice. No signature is required.", footer_text))
    
    # Build Document
    doc.build(story)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
