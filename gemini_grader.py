import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

class GeminiGrader:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini API
        api_key = "AIzaSyC35mil4vDAAmBkEVFVGyY8XEA5qGP3HSs" # Directly set the API key
        # No need to check for environment variable or raise error here as it's hardcoded
        
        genai.configure(api_key=api_key)
        
        # Initialize the model (try multiple model names for compatibility)
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.model = genai.GenerativeModel('gemini-1.0-pro')
    
    def grade_answer(self, question, actual_answer, student_answer):
        """
        Grade a student's answer based on a question and the actual correct answer using Gemini model
        
        Args:
            question (str): The question to be answered
            actual_answer (str): The correct answer to the question
            student_answer (str): The student's answer
            
        Returns:
            dict: Contains grade (int) and feedback (str)
        """
        try:
            # Create a comprehensive prompt for grading
            prompt = f"""
            You are an expert grader and educator. Please evaluate the student's answer based on the given question and the actual correct answer.

            QUESTION:
            {question}

            ACTUAL CORRECT ANSWER:
            {actual_answer}

            STUDENT'S ANSWER:
            {student_answer}

            GRADING CRITERIA:
            Please grade the student's answer on a scale of 0-10 based on:
            1. Accuracy and correctness of the student's answer compared to the actual answer
            2. Completeness of the student's answer in addressing the question and covering key points from the actual answer
            3. Clarity and organization of the student's answer
            4. Relevance of the student's answer to the question
            5. Depth of understanding demonstrated by the student

            IMPORTANT: Please provide your response in this exact format:
            GRADE: [number from 0-10]
            FEEDBACK: [Your detailed feedback explaining the grade, highlighting strengths and weaknesses compared to the actual answer]

            Be fair but thorough in your evaluation.
            """
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            if response.text:
                return self._parse_response(response.text)
            else:
                return {
                    "grade": 0,
                    "feedback": "Error: No response generated from the model"
                }
                
        except Exception as e:
            return {
                "grade": 0,
                "feedback": f"Error occurred during grading: {str(e)}"
            }
    
    def _parse_response(self, response_text):
        """
        Parse the Gemini response to extract grade and feedback
        
        Args:
            response_text (str): Raw response from Gemini
            
        Returns:
            dict: Contains grade (int) and feedback (str)
        """
        try:
            # Extract grade using regex
            grade_match = re.search(r'GRADE:\s*(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
            if grade_match:
                grade = float(grade_match.group(1))
                # Ensure grade is within 0-10 range
                grade = max(0, min(10, grade))
                grade = int(round(grade))
            else:
                # If no grade found, try to extract any number from the response
                numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', response_text)
                if numbers:
                    # Take the first number that's reasonable for a grade
                    for num in numbers:
                        num_val = float(num)
                        if 0 <= num_val <= 10:
                            grade = int(round(num_val))
                            break
                    else:
                        grade = 5  # Default grade if no suitable number found
                else:
                    grade = 5  # Default grade
            
            # Extract feedback
            feedback_match = re.search(r'FEEDBACK:\s*(.*)', response_text, re.IGNORECASE | re.DOTALL)
            if feedback_match:
                feedback = feedback_match.group(1).strip()
            else:
                # If no feedback section found, use the entire response as feedback
                feedback = response_text.strip()
            
            return {
                "grade": grade,
                "feedback": feedback
            }
            
        except Exception as e:
            return {
                "grade": 5,
                "feedback": f"Error parsing response: {str(e)}\n\nRaw response: {response_text}"
            }
    
    def test_connection(self):
        """
        Test if the Gemini API connection is working
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            # Test with a simple prompt
            test_response = self.model.generate_content("Say 'Hello' in one word")
            if test_response.text and len(test_response.text.strip()) > 0:
                return True, "Connection successful"
            else:
                return False, "No response received from API"
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return False, "Invalid API key. Please check your API key."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return False, "API quota exceeded. Please check your usage limits."
            elif "permission" in error_msg.lower():
                return False, "Permission denied. Please check if your API key has access to Gemini models."
            else:
                return False, f"Connection failed: {error_msg}"