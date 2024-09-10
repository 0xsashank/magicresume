import gradio as gr
import numpy as np
import os
from dotenv import load_dotenv
try:
    from openai import OpenAI
except ImportError:
    print("Error: The 'openai' package is not installed. Please run 'pip install openai' to install it.")
    exit(1)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import time

load_dotenv()  # Load environment variables from .env file

class ResumeAI:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.resume_database = self.load_resume_database()
        self.api_key = os.getenv('OPENAI_API_KEY')

    def load_resume_database(self):
        # Placeholder: In a real implementation, load from a database
        return [
            {"content": "Experienced software engineer with expertise in Python and machine learning.",
             "tone": "professional"},
            {"content": "Creative problem-solver who increased team productivity by 30% through innovative solutions.",
             "tone": "achievement-oriented"},
            {"content": "Passionate coder turning caffeine into code since 2010.",
             "tone": "creative"}
        ]

    def generate_resume(self, resume_points, job_description):
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        client = OpenAI(api_key=self.api_key)  # Create OpenAI client with API key

        job_embedding = self.embedding_model.encode([job_description])[0]
        point_embeddings = self.embedding_model.encode(resume_points)

        similarities = cosine_similarity([job_embedding], point_embeddings)[0]
        top_indices = np.argsort(similarities)[-5:]  # Top 5 for MVP
        relevant_points = [resume_points[i] for i in reversed(top_indices)]

        example_resumes = self.retrieve_relevant_resumes(job_embedding)

        variants = []
        for tone in ["professional", "achievement-oriented", "creative"]:
            prompt = self.create_prompt(relevant_points, job_description, example_resumes, tone)
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Changed to gpt-4o-mini as requested
                    messages=[
                        {"role": "system", "content": "You are an expert resume writer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                variant = response.choices[0].message.content.strip()
                variants.append(variant)
            except Exception as e:
                variants.append(f"An error occurred: {str(e)}")

        return variants

    def retrieve_relevant_resumes(self, job_embedding):
        resume_embeddings = self.embedding_model.encode([r['content'] for r in self.resume_database])
        similarities = cosine_similarity([job_embedding], resume_embeddings)[0]
        top_index = np.argmax(similarities)
        return [self.resume_database[top_index]]

    def create_prompt(self, points, job_description, examples, tone):
        example = examples[0]['content']
        points_text = "\n".join(f"- {point}" for point in points)
        return f"""Given the following information:

Job Description:
{job_description}

Relevant Resume Points:
{points_text}

Example Resume in {tone} tone:
{example}

Please generate a concise, {tone}-style resume based on the provided information. The resume should be tailored to the job description while highlighting the most relevant points from the candidate's experience. Ensure the resume is well-structured and easy to read.
"""

    def summarize_relevant_skills(self, job_description):
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        client = OpenAI(api_key=self.api_key)
        prompt = f"""Conduct a thorough analysis of the following job description to extract the most important skills and qualifications:

Job Description:
{job_description}

Please provide your analysis in the following format:

1. Skills Assessment:
   - List up to 7 skills explicitly mentioned in the job description.
   - For each skill, provide a brief quote or reference from the job description that mentions this skill.
   - Categorize each skill as either Technical, Soft, or Domain-Specific.

2. Qualifications Summary:
   - List any specific qualifications, certifications, or education requirements explicitly mentioned.
   - Provide a direct quote for each qualification requirement.
   - Indicate whether each is described as mandatory or preferred in the job description.

3. Top 5 Critical Components:
   - Based on frequency of mention and emphasis in the job description, list the 5 most critical skills or qualifications for this role.
   - For each, provide a brief explanation referencing specific parts of the job description that highlight its importance.

Ensure your analysis is based solely on information explicitly stated in the job description, avoiding any assumptions or inferences not directly supported by the text."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in job analysis and resume writing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred while summarizing relevant skills: {str(e)}"

resume_ai = ResumeAI()

def generate_resumes(resume_points, job_description):
    if not resume_points.strip() or not job_description.strip():
        return "Please provide both resume points and a job description.", "", "", ""
    
    resume_points_list = [point.strip() for point in resume_points.split('\n') if point.strip()]
    if len(resume_points_list) < 3:
        return "Please provide at least 3 resume points.", "", "", ""

    try:
        relevant_skills = resume_ai.summarize_relevant_skills(job_description)
        variants = resume_ai.generate_resume(resume_points_list, job_description)
        return relevant_skills, variants[0], variants[1], variants[2]
    except ValueError as e:
        return str(e), "", "", ""
    except Exception as e:
        error_message = f"An error occurred while generating resumes: {str(e)}"
        return error_message, "", "", ""

iface = gr.Interface(
    fn=generate_resumes,
    inputs=[
        gr.Textbox(lines=10, label="Resume Points (one per line)"),
        gr.Textbox(lines=5, label="Job Description")
    ],
    outputs=[
        gr.Textbox(label="Relevant Skills"),
        gr.Textbox(label="Professional Resume"),
        gr.Textbox(label="Achievement-Oriented Resume"),
        gr.Textbox(label="Creative Resume")
    ],
    title="AI Resume Generator MVP",
    description="Generate tailored resumes based on your experience and job description. Please provide your OpenAI API key."
)

if __name__ == "__main__":
    iface.launch()