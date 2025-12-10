import streamlit as st
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

def create_overlay(header_path, project_name, location):
    packet = io.BytesIO()
    # Create a new PDF with Reportlab
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Draw header image
    # X=0, Y=687 (points), Resize to 612x106 points
    if os.path.exists(header_path):
        c.drawImage(header_path, 0, 687, width=612, height=106)
    
    # Draw text
    # Project Name at X=386, Y=759 (raised 2 points)
    c.setFont("Helvetica", 10)
    c.drawString(386, 759, project_name)
    
    # Location at X=386, Y=744 (raised 2 points)
    c.drawString(386, 744, location)
    
    c.save()
    packet.seek(0)
    return packet

def main():
    st.title("Quote Stamper")
    st.write("Upload a Vendor PDF to overlay company header and project info.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    with st.form("quote_info"):
        project_name = st.text_input("Project Name")
        location = st.text_input("Location")
        quote_number = st.text_input("Quote Number")
        quote_date = st.text_input("Quote Date")
        
        submitted = st.form_submit_button("Generate Quote")

    if submitted and uploaded_file is not None:
        if not project_name or not quote_number:
            st.error("Please fill in all required fields.")
            return

        # Read your existing PDF
        existing_pdf = PdfReader(uploaded_file)
        output = PdfWriter()

        # Create the overlay
        overlay_pdf_stream = create_overlay("header.png", project_name, location)
        overlay_pdf = PdfReader(overlay_pdf_stream)
        
        # Merge overlay with the first page
        page = existing_pdf.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)
        
        # Add the rest of the pages
        for i in range(1, len(existing_pdf.pages)):
            output.add_page(existing_pdf.pages[i])
            
        # Write to a stream for download
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        
        file_name = f"ADS MSRP Quote_{quote_number}_{project_name}_{quote_date}.pdf"
        
        st.download_button(
            label="Download Stamped Quote",
            data=output_stream,
            file_name=file_name,
            mime="application/pdf"
        )
    elif submitted and uploaded_file is None:
        st.warning("Please upload a PDF file.")

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "ADS2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password instruction, try again.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if __name__ == "__main__":
    if check_password():
        main()
