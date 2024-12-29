import os
from flask import Blueprint, request, jsonify, render_template
from groq import Groq
from fpdf import FPDF
from PIL import Image
from datetime import datetime
import base64
import io
import tempfile
import shutil
import uuid
from dotenv import load_dotenv  # Import dotenv to load the .env file

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Check if the API key is present
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in the environment variables.")

bp = Blueprint('complaint', __name__)

TEMP_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_img')
if not os.path.exists(TEMP_IMG_DIR):
    os.makedirs(TEMP_IMG_DIR)

class ComplaintPDF(FPDF):
    def header(self):
        # Add header details for the PDF
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Government Service Complaint', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Add footer details for the PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, 'This is an official complaint document', 0, 0, 'R')

class GroqDynamicComplaintGenerator:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)  # Use the API key from environment

    def generate_complaint_and_pdf(self, name, email, department, subject, complaint, images=None):
        try:
            # Format the complaint
            formatted_complaint = self.format_complaint(name, email, department, subject, complaint)
            # Generate PDF based on formatted content
            pdf_data = self.generate_pdf(formatted_complaint, department, subject, name, email, images)
            return formatted_complaint, pdf_data
        except Exception as e:
            print(f"Error in generating complaint and PDF: {str(e)}")
            raise

    def format_complaint(self, name, email, department, subject, complaint):
        prompt = f"""
        Format this as a formal complaint letter to an Indian government department.
        Include all relevant details and maintain a professional tone.

        Department: {department}
        Name: {name}
        Email: {email}
        Subject: {subject}
        Complaint: {complaint}

        Please include:
        1. Proper letter formatting with date and reference number
        2. Clear statement of the issue
        3. Specific request for action
        4. Timeline expectations
        5. Contact information
        """

        try:
            # Making the API call to Groq
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}]
            )

            # The response might be a Python object, not an HTTP response with status code
            if 'choices' in response:
                return response['choices'][0]['message']['content']
            else:
                raise ValueError(f"Unexpected response from Groq API: {response}")

        except Exception as e:
            print(f"Error formatting complaint: {str(e)}")
            # Fallback template in case of error
            ref_number = f"COMP/{datetime.now().strftime('%Y%m%d')}/{hash(subject) % 1000:03d}"
            return f"""
            Reference Number: {ref_number}
            Date: {datetime.now().strftime('%d-%m-%Y')}

            To,
            The {department},
            Government of India

            Subject: {subject}

            Dear Sir/Madam,

            I, {name}, wish to bring to your attention a matter of concern regarding the following issue:

            {complaint}

            I request your immediate attention to this matter and expect a resolution within the standard 
            timeline of 15 working days as per government guidelines.

            You may contact me for any clarification at:
            Email: {email}

            I look forward to your prompt action on this matter.

            Thanking you,

            Yours faithfully,
            {name}
            """



    def process_image(self, image_data):
        try:
            # Convert binary data into an image object
            image = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA (if present) to RGB
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Save the processed image in a temporary file for use in the PDF
            temp_image_path = os.path.join(TEMP_IMG_DIR, f'temp_{uuid.uuid4()}.jpg')
            image.save(temp_image_path, 'JPEG')
            
            return temp_image_path
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

    # Adjustments in generate_pdf function to ensure proper base64 output:
    def generate_pdf(self, formatted_complaint, department, subject, name, email, images=None):
        pdf = ComplaintPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        try:
            # Add header information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Department: {department}', 0, 1)
            pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d-%m-%Y")}', 0, 1)
            pdf.cell(0, 10, f'Reference: COMP/{datetime.now().strftime("%Y%m%d")}/{hash(subject) % 1000:03d}', 0, 1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

            # Add complaint content
            pdf.set_font('Arial', '', 12)

            paragraphs = formatted_complaint.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    pdf.multi_cell(0, 10, paragraph.strip())
                    pdf.ln(5)

            # Add images if provided
            if images:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Supporting Documents', 0, 1, 'C')
                pdf.ln(5)

                for idx, image in enumerate(images):
                    try:
                        temp_image_path = self.process_image(image)
                        if temp_image_path:
                            pdf.image(temp_image_path, x=10, y=None, w=190)
                            pdf.ln(5)
                            pdf.cell(0, 10, f'Supporting Document {idx + 1}', 0, 1, 'C')
                            os.remove(temp_image_path)  # Clean up temporary file
                    except Exception as e:
                        print(f"Error processing image {idx}: {str(e)}")

            # Generate PDF and check if it's valid
            pdf_data = pdf.output(dest='S').encode('latin1')

            if not pdf_data:
                raise Exception("PDF generation failed: No data returned.")

            # Return the PDF in base64 format
            return base64.b64encode(pdf_data).decode('utf-8')

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise



@bp.route('/complaint')
def index():
    return render_template('complaint_form.html')

@bp.route('/format_complaint', methods=['POST'])
def format_complaint():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        subject = request.form.get('subject')
        complaint = request.form.get('complaint')
        
        # Handle multiple images
        images = []
        for key in request.files:
            file = request.files[key]
            if file and file.filename:
                images.append(file.read())
        
        complaint_generator = GroqDynamicComplaintGenerator()
        formatted_content, pdf_base64 = complaint_generator.generate_complaint_and_pdf(
            name=name,
            email=email,
            department=department,
            subject=subject,
            complaint=complaint,
            images=images
        )
        
        return jsonify({
            'formatted_content': formatted_content,
            'pdf_base64': pdf_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import base64
from flask import request, jsonify
import os
from datetime import datetime

PDF_STORAGE_DIR = os.path.join(os.getcwd(), 'WE 2', 'app', 'complaint_pdfs')

# Ensure the PDF storage directory exists
if not os.path.exists(PDF_STORAGE_DIR):
    os.makedirs(PDF_STORAGE_DIR)

@bp.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    try:
        # Get the base64 PDF and other form data
        pdf_base64 = request.form.get('pdf_base64')
        if not pdf_base64:
            return jsonify({'error': 'pdf_base64 is missing'}), 400

        # Debugging: Check if pdf_base64 is received correctly
        print(f"Received pdf_base64: {pdf_base64[:100]}...")  # Print the first 100 characters to avoid printing too much

        # Decode the PDF base64 string
        pdf_data = base64.b64decode(pdf_base64)

        # Save the PDF file to the server
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        pdf_filename = f"complaint_{timestamp}.pdf"
        pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)

        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)

        # Handle other form data as needed (e.g., save to database)

        # Return success message with the tracking number or any other info
        tracking_number = f"TRK{timestamp}"
        return jsonify({
            'message': 'Complaint submitted successfully!',
            'tracking_number': tracking_number,
            'pdf_filename': pdf_filename
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@bp.route('/check_status/<tracking_number>', methods=['GET'])
def check_status(tracking_number):
    return jsonify({
        'tracking_number': tracking_number,
        'status': 'Under Review',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
