import streamlit as st
from google import genai
import re

# Page Config
st.set_page_config(page_title="Grade 12 Math Quiz", layout="centered")

st.title("🔢 Grade 12 Interactive Math Quiz")
st.info("CDM ပညာရေးအတွက် အထောက်အကူပြု (New Curriculum)")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    chapter = st.selectbox("Select Chapter:", [
        "Chapter 1: Complex Numbers",
        "Chapter 2: Mathematical Induction",
        "Chapter 3: Analytical Solid Geometry",
        "Chapter 4: Vector Algebra",
        "Chapter 5: Permutation and Combination"
    ])
    generate_btn = st.button("Generate New Quiz")

# Initialize Session State (မေးခွန်းများ သိမ်းဆည်းရန်)
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None

# Gemini AI အသုံးပြု၍ မေးခွန်းထုတ်ခြင်း
if generate_btn and api_key:
    client = genai.Client(api_key=api_key)
    
    # AI ကို ပေးမယ့် Instruction
    system_prompt = f"""
    Generate 1 MCQ for Grade 12 Math {chapter}. 
    Strictly follow this format:
    Question: [The question text here using LaTeX]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    Correct: [Only the Letter A, B, C, or D]
    Explanation: [Short explanation in Burmese]
    """
    
    with st.spinner("မေးခွန်းအသစ် ထုတ်နေသည်..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt
            )
            st.session_state.quiz_data = response.text
            st.session_state.user_answer = None # အဖြေဟောင်းကို ဖျက်ရန်
        except Exception as e:
            st.error(f"Error: {e}")

# Quiz ကို Display လုပ်ခြင်း
if st.session_state.quiz_data:
    raw_text = st.session_state.quiz_data
    
    # Regular Expression ဖြင့် မေးခွန်းနှင့် အဖြေများကို ခွဲထုတ်ခြင်း
    q_match = re.search(r"Question: (.*)", raw_text)
    a_match = re.search(r"A\) (.*)", raw_text)
    b_match = re.search(r"B\) (.*)", raw_text)
    c_match = re.search(r"C\) (.*)", raw_text)
    d_match = re.search(r"D\) (.*)", raw_text)
    correct_match = re.search(r"Correct: ([A-D])", raw_text)
    exp_match = re.search(r"Explanation: (.*)", raw_text, re.DOTALL)

    if q_match:
        st.markdown(f"### ❓ Question:")
        st.write(q_match.group(1))
        
        # ရွေးချယ်စရာများ
        options = {
            "A": a_match.group(1) if a_match else "",
            "B": b_match.group(1) if b_match else "",
            "C": c_match.group(1) if c_match else "",
            "D": d_match.group(1) if d_match else ""
        }
        
        user_choice = st.radio("အဖြေကို ရွေးချယ်ပါ -", list(options.keys()), 
                               format_func=lambda x: f"{x}) {options[x]}")

        if st.button("Submit Answer"):
            correct_ans = correct_match.group(1)
            if user_choice == correct_ans:
                st.success(f"✅ မှန်ကန်ပါတယ်။ အဖြေက ({correct_ans}) ဖြစ်ပါတယ်။")
            else:
                st.error(f"❌ မှားယွင်းပါတယ်။ အဖြေမှန်က ({correct_ans}) ဖြစ်ပါတယ်။")
            
            st.markdown("#### 💡 ရှင်းလင်းချက်")
            st.write(exp_match.group(1) if exp_match else "ရှင်းလင်းချက် မရှိပါ။")

elif not api_key:
    st.warning("ညာဘက် Sidebar တွင် API Key ထည့်သွင်းပေးပါဆရာ။")
else:
    st.write("မေးခွန်းစတင်ထုတ်ရန် 'Generate New Quiz' ခလုတ်ကို နှိပ်ပါ။")

