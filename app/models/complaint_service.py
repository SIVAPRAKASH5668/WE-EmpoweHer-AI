from groq import Groq
import os
from fpdf import FPDF
from datetime import datetime

class GroqDynamicComplaintGenerator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def generate_complaint_and_pdf(self, name, email, subject, complaint):
        # Format the complaint using Groq API
        formatted_complaint = self.format_complaint(name, email, subject, complaint)
        
        # Generate PDF using the formatted content
        pdf_path = self.generate_pdf(formatted_complaint, subject, name, email)
        
        return formatted_complaint, pdf_path

    def format_complaint(self, name, email, subject, complaint):
        # Create the prompt for the Groq model
        prompt = f"""
        Please format the following complaint in a professional manner:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        Complaint: {complaint}
        
        Please maintain a formal tone and structure the complaint properly.
        """
        
        try:
            # Request formatted complaint from Groq model
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback formatting if Groq API fails
            return f"""
            Date: {datetime.now().strftime('%Y-%m-%d')}
            
            Subject: {subject}
            
            Dear Sir/Madam,
            
            I, {name}, would like to bring to your attention the following matter:
            
            {complaint}
            
            I look forward to your response regarding this matter.
            
            Sincerely,
            {name}
            {email}
            """

    def generate_pdf(self, formatted_complaint, subject, name, email):
        # Create a PDF from the formatted complaint content
        pdf = FPDF()
        pdf.add_page()
        
        # Add header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Complaint Report', 0, 1, 'C')
        pdf.line(10, 30, 200, 30)
        
        # Add complaint details
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Subject: {subject}', 0, 1)
        pdf.cell(0, 10, f'Name: {name}', 0, 1)
        pdf.cell(0, 10, f'Email: {email}', 0, 1)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
        
        # Add the formatted complaint content
        pdf.multi_cell(0, 10, formatted_complaint)
        
        # Define an absolute path for the PDF file
        base_path = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base_path, '..', 'temp', f'complaint_{hash(formatted_complaint)}.pdf')
        
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        # Save the PDF
        pdf.output(pdf_path)
        
        print(f"pdf is saved to {pdf_path}")
        return pdf_path
