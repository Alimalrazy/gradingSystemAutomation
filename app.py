import streamlit as st
import os
from gemini_grader import GeminiGrader
import time

# Set page configuration
st.set_page_config(
    page_title="AI Answer Grader",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
        color: #1f77b4;
    }
    .grade-display {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .grade-excellent {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .grade-good {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 2px solid #b8daff;
    }
    .grade-average {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .grade-poor {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .feedback-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_grade_class(grade):
    """Return CSS class based on grade"""
    if grade >= 8:
        return "grade-excellent"
    elif grade >= 6:
        return "grade-good"
    elif grade >= 4:
        return "grade-average"
    else:
        return "grade-poor"

def get_grade_emoji(grade):
    """Return emoji based on grade"""
    if grade >= 9:
        return "🏆"
    elif grade >= 8:
        return "🌟"
    elif grade >= 6:
        return "👍"
    elif grade >= 4:
        return "👌"
    else:
        return "📚"

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI Answer Grader with Gemini</h1>", 
                unsafe_allow_html=True)
    
    # Sidebar for API key management
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key is now hardcoded in gemini_grader.py, no input needed here
        st.info("API key is configured internally. No input needed.")
        
        st.markdown("---")
        
        # Information section
        st.header("📋 How to Use")
        st.markdown("""
        1. Enter your Google API key above
        2. Input the question in the first text area
        3. Input the answer in the second text area
        4. Click 'Grade Answer' to get your score
        5. Review the detailed feedback
        """)
        
        st.markdown("---")
        
        # Grading criteria
        st.header("📊 Grading Criteria")
        st.markdown("""
        **Scores are based on:**
        - Accuracy & Correctness
        - Completeness
        - Clarity & Organization
        - Relevance
        - Depth of Understanding
        """)
        
        st.markdown("---")
        
        # Get API key link
        st.markdown("""
        **Need an API key?**
        
        Get your free Google API key from:
        [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Question input
        st.header("❓ Question")
        question = st.text_area(
            "Enter the question here:",
            height=150,
            placeholder="Example: What is the capital of France and what are its major landmarks?",
            help="Enter the question that needs to be answered"
        )
        
        # Actual Answer input
        st.header("📚 Actual Answer")
        actual_answer = st.text_area(
            "Enter the actual correct answer here:",
            height=200,
            placeholder="Example: The capital of France is Paris. Some major landmarks include the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral...",
            help="Enter the correct answer against which the student's answer will be graded"
        )

        # Student's Answer input
        st.header("✍️ Student's Answer")
        student_answer = st.text_area(
            "Enter the student's answer here:",
            height=200,
            placeholder="Example: Paris is the capital of France. The Eiffel Tower is a famous landmark there.",
            help="Enter the student's response that needs to be graded"
        )
        
        # Grade button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            grade_button = st.button(
                "🎯 Grade Answer",
                use_container_width=True,
                type="primary"
            )
    
    with col2:
        # Display area for results
        st.header("📈 Results")
        
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            grade = result['grade']
            feedback = result['feedback']
            
            # Display grade
            grade_class = get_grade_class(grade)
            grade_emoji = get_grade_emoji(grade)
            
            st.markdown(f"""
            <div class="grade-display {grade_class}">
                {grade_emoji} {grade}/10
            </div>
            """, unsafe_allow_html=True)
            
            # Display feedback
            st.markdown(f"""
            <div class="feedback-box">
                <strong>📝 Detailed Feedback:</strong><br>
                {feedback}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <strong>🚀 Ready to Grade!</strong><br>
                Enter a question and answer, then click "Grade Answer" to see results here.
            </div>
            """, unsafe_allow_html=True)
    
    # Process grading when button is clicked
    if grade_button:
        if not question.strip():
            st.error("❌ Please enter a question!")
        elif not actual_answer.strip():
            st.error("❌ Please enter the actual correct answer!")
        elif not student_answer.strip():
            st.error("❌ Please enter the student's answer!")
        else:
            try:
                # Show progress
                with st.spinner("🤔 AI is analyzing the answer..."):
                    # Initialize grader
                    grader = GeminiGrader()
                    
                    # Test connection first
                    connection_success, error_msg = grader.test_connection()
                    if not connection_success:
                        st.error(f"❌ {error_msg}")
                        return
                    
                    # Grade the answer
                    result = grader.grade_answer(question, actual_answer, student_answer)
                    
                    # Store result in session state
                    st.session_state.last_result = result
                    
                    # Show success message
                    st.success("✅ Answer graded successfully!")
                    
                    # Rerun to display results
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please check your API key and internet connection.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Built with ❤️ using Streamlit and Google Gemini AI<br>
        <em>Powered by AI for intelligent answer evaluation</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()