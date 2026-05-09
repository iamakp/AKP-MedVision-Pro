import streamlit as st

def apply_modern_ui():
    """
    Applies Glassmorphism and Modern Medical UI to the Streamlit app.
    """
    st.markdown("""
        <style>
        /* Main Background with Deep Medical Blue Gradient */
        .stApp {
            background: radial-gradient(circle at top, #0a192f, #020c1b);
            color: #e6f1ff;
        }
        
        /* Modern Glass Cards (Glassmorphism Effect) */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(0, 198, 255, 0.15);
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px -10px rgba(2, 12, 27, 0.7);
        }
        
        /* Neon Glow Title (Gradient Text) */
        .neon-title {
            font-family: 'Helvetica', sans-serif;
            font-size: 38px;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
            text-shadow: 0px 0px 15px rgba(0, 210, 255, 0.2);
        }

        /* Professional Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 12, 27, 0.95);
            border-right: 1px solid rgba(0, 198, 255, 0.1);
        }

        /* Modern Gradient Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            color: white;
            border: none;
            padding: 12px 0px;
            border-radius: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0px 0px 20px rgba(0, 210, 255, 0.5);
            transform: translateY(-2px);
        }
        
        /* Personalized Chat Bubbles */
        .chat-bubble { 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 12px; 
            font-size: 14px; 
            border: 1px solid rgba(0,198,255,0.1); 
        }
        .user-bubble { 
            background: rgba(0, 210, 255, 0.1); 
            border-left: 5px solid #00d2ff; 
        }
        .ai-bubble { 
            background: rgba(58, 123, 213, 0.1); 
            border-left: 5px solid #3a7bd5; 
        }

        /* Custom scrollbar for a cleaner look */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #020c1b;
        }
        ::-webkit-scrollbar-thumb {
            background: #00d2ff;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def header_component():
    """
    Renders the main neon header of the application.
    """
    st.markdown('<div class="neon-title">AI-Powered Multi-Disease Detection System</div>', unsafe_allow_html=True)