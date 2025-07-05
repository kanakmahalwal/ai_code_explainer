import streamlit as st
import requests
import json
import re
from datetime import datetime

# Try to import Groq, handle if not installed
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    st.error("⚠️ Groq package not installed. Please install it using: pip install groq")
    st.stop()

# Set your Groq API key here
GROQ_API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

# Page configuration
st.set_page_config(
    page_title="AI Code Explainer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
    }
    
    .code-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #334155;
        position: relative;
        overflow: hidden;
    }
    
    .code-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .explanation-container {
        background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #0ea5e9;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .explanation-container::before {
        content: '🤖';
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 1.5rem;
        opacity: 0.3;
    }
    
    .language-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .example-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .example-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stats-container {
        display: flex;
        gap: 2rem;
        margin: 2rem 0;
        justify-content: center;
    }
    
    .stat-item {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        min-width: 120px;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .complexity-selector {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .history-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        border-color: #667eea;
        transform: translateX(4px);
    }
    
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        margin: 0 4px;
        animation: loading 1.4s infinite both;
    }
    
    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes loading {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a67d8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'explanation_history' not in st.session_state:
    st.session_state.explanation_history = []
if 'total_explanations' not in st.session_state:
    st.session_state.total_explanations = 0
if 'favorite_language' not in st.session_state:
    st.session_state.favorite_language = "Python"

def initialize_groq_client():
    """Initialize Groq client with hardcoded API key"""
    if GROQ_API_KEY == "your_groq_api_key_here":
        return None
    try:
        client = Groq(api_key=GROQ_API_KEY)
        return client
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        return None

def detect_language(code):
    """Enhanced language detection with more patterns"""
    code_lower = code.lower()
    
    # Python indicators
    if any(keyword in code for keyword in ['def ', 'import ', 'print(', 'if __name__', 'elif ', 'from ', 'range(', 'len(']):
        return 'Python'
    
    # JavaScript indicators
    elif any(keyword in code for keyword in ['function ', 'console.log', 'const ', 'let ', 'var ', '=>', 'document.', 'window.']):
        return 'JavaScript'
    
    # TypeScript indicators
    elif any(keyword in code for keyword in ['interface ', 'type ', ': string', ': number', ': boolean']):
        return 'TypeScript'
    
    # Java indicators
    elif any(keyword in code for keyword in ['public class', 'public static void', 'System.out.print', 'private ', 'protected ']):
        return 'Java'
    
    # C++ indicators
    elif any(keyword in code for keyword in ['#include', 'cout <<', 'cin >>', 'std::', 'namespace ']):
        return 'C++'
    
    # C indicators
    elif any(keyword in code for keyword in ['#include <stdio.h>', 'printf(', 'scanf(', 'malloc(']):
        return 'C'
    
    # C# indicators
    elif any(keyword in code for keyword in ['using System', 'Console.WriteLine', 'public static void Main']):
        return 'C#'
    
    # PHP indicators
    elif any(keyword in code for keyword in ['<?php', '$_', 'echo ', 'function ', '->']) and '$' in code:
        return 'PHP'
    
    # Ruby indicators
    elif any(keyword in code for keyword in ['def ', 'end', 'puts ', 'require ', '.each']):
        return 'Ruby'
    
    # Go indicators
    elif any(keyword in code for keyword in ['package main', 'func main', 'import ', 'fmt.Print']):
        return 'Go'
    
    # Rust indicators
    elif any(keyword in code for keyword in ['fn main', 'let mut', 'println!', 'use std::']):
        return 'Rust'
    
    # HTML indicators
    elif any(keyword in code for keyword in ['<html>', '<div>', '<body>', '<head>', '<!DOCTYPE']):
        return 'HTML'
    
    # CSS indicators
    elif '{' in code and '}' in code and ':' in code and not any(keyword in code for keyword in ['if', 'for', 'while', 'function']):
        return 'CSS'
    
    # SQL indicators
    elif any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert ', 'update ', 'delete ']):
        return 'SQL'
    
    return 'Unknown'

def explain_code(client, code, language, complexity_level):
    """Send code to Groq API for explanation"""
    
    complexity_prompts = {
        "🌱 Beginner": "Explain this code in very simple terms, as if teaching a complete beginner. Use everyday language, avoid technical jargon, and use analogies when helpful.",
        "🚀 Intermediate": "Explain this code with moderate technical detail, suitable for someone with basic programming knowledge. Include key concepts and best practices.",
        "🔥 Advanced": "Provide a detailed technical explanation of this code, including advanced concepts, patterns, performance considerations, and potential optimizations."
    }
    
    prompt = f"""
    You are an expert programming tutor with a friendly, encouraging teaching style. {complexity_prompts[complexity_level]}

    Programming Language: {language}
    
    Code to explain:
    ```{language.lower()}
    {code}
    ```
    
    Please provide:
    1. **Overview**: A brief summary of what this code does
    2. **Step-by-step breakdown**: Walk through the code line by line or block by block
    3. **Key concepts**: Explain any important programming concepts used
    4. **Best practices**: Mention any good coding practices demonstrated
    5. **Potential improvements**: Suggest any improvements or point out potential issues (if any)
    
    Format your response with clear sections and use emojis to make it engaging. Make it educational and encouraging!
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful, encouraging programming tutor who explains code clearly with enthusiasm and makes learning fun."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=2000,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error explaining code: {str(e)}"

def save_to_history(code, language, explanation):
    """Save explanation to history"""
    st.session_state.explanation_history.insert(0, {
        'code': code[:100] + "..." if len(code) > 100 else code,
        'full_code': code,
        'language': language,
        'explanation': explanation,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Keep only last 10 explanations
    if len(st.session_state.explanation_history) > 10:
        st.session_state.explanation_history = st.session_state.explanation_history[:10]
    
    st.session_state.total_explanations += 1
    st.session_state.favorite_language = language

def get_example_code(language):
    """Get example code for different languages"""
    examples = {
        "Python": """def calculate_fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number\"\"\"
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b

# Example usage
result = calculate_fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")""",
        
        "JavaScript": """function createCounter() {
    let count = 0;
    
    return {
        increment: () => ++count,
        decrement: () => --count,
        getValue: () => count,
        reset: () => count = 0
    };
}

// Example usage
const counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.increment()); // 2
console.log(counter.getValue());  // 2""",
        
        "Java": """public class BankAccount {
    private double balance;
    private String accountNumber;
    
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }
    
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println("Deposited: $" + amount);
        }
    }
    
    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            System.out.println("Withdrawn: $" + amount);
            return true;
        }
        return false;
    }
    
    public double getBalance() {
        return balance;
    }
}"""
    }
    
    return examples.get(language, examples["Python"])

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 AI Code Explainer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform complex code into clear, understandable explanations ✨</p>', unsafe_allow_html=True)
    
    # Check if API key is set
    if GROQ_API_KEY == "your_groq_api_key_here":
        st.markdown('<div class="warning-message">⚠️ Please set your Groq API key in the code (line 17) to enable explanations</div>', unsafe_allow_html=True)
        st.markdown("Get your free API key from: https://console.groq.com/keys")
        st.code("GROQ_API_KEY = 'your_actual_api_key_here'", language="python")
        return
    
    # Initialize Groq client
    client = initialize_groq_client()
    
    if not client:
        st.markdown('<div class="error-message">❌ Failed to initialize Groq client. Please check your API key.</div>', unsafe_allow_html=True)
        return
    
    # Stats section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-item">
            <div class="stat-number">{st.session_state.total_explanations}</div>
            <div class="stat-label">Code Explanations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-item">
            <div class="stat-number">{len(st.session_state.explanation_history)}</div>
            <div class="stat-label">Recent History</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-item">
            <div class="stat-number">{st.session_state.favorite_language}</div>
            <div class="stat-label">Recent Language</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔍 Code Explainer", "📚 Examples", "📜 History"])
    
    with tab1:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Enter Your Code")
            
            # Code input
            code_input = st.text_area(
                "Paste your code here:",
                height=300,
                placeholder="# Paste your code here...\n# I'll explain it in simple terms!\n\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
                help="Paste any code snippet you want explained",
                key="code_input"
            )
            
            # Language detection
            if code_input.strip():
                detected_language = detect_language(code_input)
                st.markdown(f'<div class="language-badge">🔍 Detected: {detected_language}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### ⚙️ Settings")
            
            # Complexity level selector
            complexity_level = st.selectbox(
                "Choose explanation level:",
                ["🌱 Beginner", "🚀 Intermediate", "🔥 Advanced"],
                index=0,
                help="Select how detailed you want the explanation"
            )
            
            # Language override
            language_override = st.selectbox(
                "Override language (optional):",
                ["Auto-detect", "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "PHP", "Ruby", "Go", "Rust", "HTML", "CSS", "SQL"],
                index=0
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Explain button
        if code_input.strip():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Explain My Code", type="primary", use_container_width=True):
                    # Determine language
                    if language_override == "Auto-detect":
                        final_language = detect_language(code_input)
                    else:
                        final_language = language_override
                    
                    # Show loading animation
                    with st.spinner('🧠 Analyzing your code...'):
                        explanation = explain_code(client, code_input, final_language, complexity_level)
                        
                        if not explanation.startswith("Error"):
                            # Save to history
                            save_to_history(code_input, final_language, explanation)
                            
                            # Display explanation
                            st.markdown('<div class="explanation-container">', unsafe_allow_html=True)
                            st.markdown(f"### 🤖 Code Explanation - {final_language}")
                            st.markdown(explanation)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Success message
                            st.markdown('<div class="success-message">✅ Code explained successfully! Check the History tab to see all your explanations.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-message">{explanation}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🎯 Try These Examples")
        
        col1, col2, col3 = st.columns(3)
        
        example_languages = ["Python", "JavaScript", "Java"]
        
        for i, lang in enumerate(example_languages):
            with [col1, col2, col3][i]:
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown(f"#### {lang} Example")
                
                example_code = get_example_code(lang)
                st.code(example_code[:150] + "..." if len(example_code) > 150 else example_code, language=lang.lower())
                
                if st.button(f"📋 Use {lang} Example", key=f"example_{lang}", use_container_width=True):
                    st.session_state.selected_example = example_code
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Load selected example
        if hasattr(st.session_state, 'selected_example'):
            st.markdown('<div class="success-message">✅ Example loaded! Go to the Code Explainer tab to see it.</div>', unsafe_allow_html=True)
            st.session_state.code_input = st.session_state.selected_example
            delattr(st.session_state, 'selected_example')
    
    with tab3:
        st.markdown("### 📜 Your Explanation History")
        
        if st.session_state.explanation_history:
            for i, item in enumerate(st.session_state.explanation_history):
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{item['language']}** - {item['timestamp']}")
                    st.code(item['code'], language=item['language'].lower())
                
                with col2:
                    if st.button("📖 View", key=f"history_{i}"):
                        st.session_state.selected_history = item
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear history button
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.explanation_history = []
                st.session_state.total_explanations = 0
                st.rerun()
        else:
            st.markdown('<div class="warning-message">📝 No explanations yet. Go to the Code Explainer tab to get started!</div>', unsafe_allow_html=True)
    
    # Display selected history item
    if hasattr(st.session_state, 'selected_history'):
        st.markdown("---")
        st.markdown("### 📖 Detailed View")
        
        item = st.session_state.selected_history
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown(f"**Code ({item['language']}):**")
            st.code(item['full_code'], language=item['language'].lower())
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="explanation-container">', unsafe_allow_html=True)
            st.markdown("**Explanation:**")
            st.markdown(item['explanation'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("❌ Close Detailed View"):
            delattr(st.session_state, 'selected_history')
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; margin-top: 2rem;">
        <p>🧠 <strong>AI Code Explainer</strong> - Making code understanding accessible to everyone</p>
        <p>Built with ❤️ using Streamlit & Groq AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()