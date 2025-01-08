from flask import Flask, request, jsonify, render_template
import json
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)

# Load the multilingual sentence transformer model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Load the dataset
with open('women_laws.json', 'r', encoding='utf-8') as f:
    law_data = json.load(f)

class LawChatbot:
    def __init__(self, law_data):
        self.law_data = law_data
        self.current_language = 'en'
        self.context = {}
        
    def set_language(self, language):
        self.current_language = language
        
    def preprocess_law_data(self):
        """Prepare the context for the current language"""
        context = ""
        for law in self.law_data:
            # Add title and description
            title = law['title'].get(self.current_language, "")
            description = law['description'].get(self.current_language, "")
            context += f"{title}\n{description}\n"
            
            # Add rights
            rights = law['rights'].get(self.current_language, [])
            for right in rights:
                context += f"- {right}\n"
            
            # Add penalties
            penalties = law['penalties'].get(self.current_language, {})
            context += f"Penalties:\n"
            context += f"- Imprisonment: {penalties.get('imprisonment', 'N/A')}\n"
            context += f"- Fine: {penalties.get('fine', 'N/A')}\n"
            
        return context
    
    def get_most_relevant_info(self, query):
        """Find the most relevant information for the query"""
        query_embedding = model.encode(query, convert_to_tensor=True)
        
        best_match = None
        highest_score = -1
        
        for law in self.law_data:
            # Create embeddings for different parts of the law
            title = law['title'].get(self.current_language, "")
            description = law['description'].get(self.current_language, "")
            rights = " ".join(law['rights'].get(self.current_language, []))
            penalties = law['penalties'].get(self.current_language, {})
            penalty_text = f"{penalties.get('imprisonment', '')} {penalties.get('fine', '')}"
            
            # Combine all text
            full_text = f"{title} {description} {rights} {penalty_text}"
            text_embedding = model.encode(full_text, convert_to_tensor=True)
            
            # Calculate similarity
            similarity = util.pytorch_cos_sim(query_embedding, text_embedding)
            score = similarity.item()
            
            if score > highest_score:
                highest_score = score
                best_match = {
                    'title': title,
                    'description': description,
                    'rights': law['rights'].get(self.current_language, []),
                    'penalties': law['penalties'].get(self.current_language, {})
                }
        
        return best_match, highest_score
    
    def generate_response(self, query):
        best_match, confidence = self.get_most_relevant_info(query)
        
        if confidence < 0.3:
            return {
                'response': "I'm sorry, I couldn't find specific information about that. Could you please rephrase your question?",
                'confidence': confidence
            }
            
        # Determine query type and format response accordingly
        query_lower = query.lower()
        
        if 'penalty' in query_lower or 'punishment' in query_lower:
            response = f"The penalties include:\n- Imprisonment: {best_match['penalties'].get('imprisonment', 'N/A')}\n- Fine: {best_match['penalties'].get('fine', 'N/A')}"
        elif 'right' in query_lower:
            response = "The rights include:\n" + "\n".join(f"- {right}" for right in best_match['rights'])
        else:
            response = f"{best_match['description']}\n\nKey rights include:\n" + "\n".join(f"- {right}" for right in best_match['rights'])
            
        return {
            'response': response,
            'confidence': confidence
        }

chatbot = LawChatbot(law_data)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data['query']
    language = data['language']
    
    chatbot.set_language(language)
    response = chatbot.generate_response(query)
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
