import streamlit as st
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
import os
from PIL import Image
import io
import base64


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


st.set_page_config(
    page_title="SkinCare Chatbot",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background-color: #2b5876;
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #4e4376;
        color: white;
        margin-right: 20%;
    }
    .timestamp {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    .stTextInput > div > div > input {
        background-color: white !important;
        color: black !important;
    }
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: black !important;
    }
    .uploaded-image {
        max-width: 250px;
        max-height: 250px;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        object-fit: cover;
    }
    .message-image {
        max-width: 200px;
        max-height: 200px;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
    }
    .input-container {
        position: sticky;
        bottom: 0;
        background: rgba(102, 126, 234, 0.95);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
        backdrop-filter: blur(10px);
    }
    .file-uploader-container {
        width: 60px;
        margin-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const textarea = document.querySelector('textarea');
            if (textarea) {
                textarea.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        const sendButton = document.querySelector('button[kind="primary"]');
                        if (sendButton) {
                            sendButton.click();
                        }
                    }
                });
            }
        });
    </script>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_configured" not in st.session_state:
    st.session_state.api_configured = False

if "chat_model" not in st.session_state:
    st.session_state.chat_model = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "image_preview" not in st.session_state:
    st.session_state.image_preview = None

if "input_key" not in st.session_state:
    st.session_state.input_key = 0  

if "enter_pressed" not in st.session_state:
    st.session_state.enter_pressed = False


def configure_gemini():
    """Gemini API'yi yapılandırır"""
    try:
        if not GEMINI_API_KEY:
            return None, "API Key bulunamadı! Lütfen .env dosyasına GEMINI_API_KEY ekleyin."
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        generation_config = {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config
        )
        
        return model, None
    except Exception as e:
        return None, str(e)


def process_image(image, max_size=200):
    """Görseli küçültüp base64'e çevirir"""
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    image_base64 = base64.b64encode(img_byte_arr).decode()
    return image_base64


if not st.session_state.api_configured:
    model, error = configure_gemini()
    if error:
        st.error(f"❌ API Yapılandırma Hatası: {error}")
        st.info("""
        **Kurulum Adımları:**
        1. Proje klasöründe `.env` dosyası oluşturun
        2. İçine şunu yazın: `GEMINI_API_KEY=your_api_key_here`
        3. API key'i [Google AI Studio](https://makersuite.google.com/app/apikey)'dan alın
        """)
        st.stop()
    else:
        st.session_state.chat_model = model
        st.session_state.api_configured = True


st.title("🧴 SkinCare Chatbot")
st.markdown("**Gemini 2.0 Flash - Cilt Bakımı Uzmanı**")
st.divider()


chat_container = st.container()

with chat_container:
    if len(st.session_state.messages) == 0:
        st.info("👋 Merhaba! Ben SkinCare Chatbot'unuzum. Cilt bakımı sorularınızı metin veya görsel ile sorabilirsiniz!")
    
    for message in st.session_state.messages:
        timestamp = message.get("timestamp", "")
        
        if message["role"] == "user":
            content_html = f"<b>👤 Siz:</b><br>"
            if "image" in message:
                content_html += f'<img src="data:image/png;base64,{message["image"]}" class="message-image"><br>'
            content_html += f'{message["content"]}<div class="timestamp">{timestamp}</div>'
            st.markdown(f'<div class="chat-message user-message">{content_html}</div>', 
                       unsafe_allow_html=True)
        else:
            content_html = f"<b>🧴 SkinCare Bot:</b><br>{message['content']}<div class='timestamp'>{timestamp}</div>"
            st.markdown(f'<div class="chat-message bot-message">{content_html}</div>', 
                       unsafe_allow_html=True)


st.markdown('<div class="input-container">', unsafe_allow_html=True)


input_container = st.container()
with input_container:
    col1, col2 = st.columns([1, 8])
    
    with col1:
        st.markdown('<div class="file-uploader-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📸",
            type=["png", "jpg", "jpeg", "gif", "webp"],
            label_visibility="collapsed",
            key=f"file_uploader_{st.session_state.input_key}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        user_input = st.text_area(
            "💬 Mesajınızı yazın:",
            placeholder="Cilt bakımı sorunuzu buraya yazın...",
            height=80,
            key=f"user_input_field_{st.session_state.input_key}"
        )


button_col1, button_col2 = st.columns([1, 1])

with button_col1:
    send_button = st.button("📤 Gönder", use_container_width=True, type="primary")

with button_col2:
    clear_button = st.button("🗑️ Temizle Hepsi", use_container_width=True)


if uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)
    st.session_state.image_preview = uploaded_file


if st.session_state.image_preview is not None:
    with col1:
        st.image(st.session_state.uploaded_image, width=60, caption="📎")

st.markdown('</div>', unsafe_allow_html=True)


if clear_button:
    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.image_preview = None
    st.session_state.input_key += 1  # Reset input widgets
    st.session_state.enter_pressed = False
    st.rerun()


if (send_button or st.session_state.get('enter_pressed', False)) and (user_input or st.session_state.uploaded_image):
    current_time = datetime.now().strftime("%H:%M")
    
    
    user_message = {
        "role": "user",
        "content": user_input if user_input else "📷 Görsel gönderildi",
        "timestamp": current_time
    }
    
    
    image_for_gemini = None
    if st.session_state.uploaded_image is not None:
        small_image_base64 = process_image(st.session_state.uploaded_image.copy(), max_size=200)
        user_message["image"] = small_image_base64
        image_for_gemini = st.session_state.uploaded_image
    
   
    st.session_state.messages.append(user_message)
    
    
    with st.spinner("🤔 SkinCare Bot düşünüyor..."):
        try:
            if image_for_gemini and user_input:
                prompt_parts = [user_input, image_for_gemini]
            elif image_for_gemini:
                prompt_parts = ["Bu cilt görselinde ne görüyorsunuz? Cilt bakımı için öneriler sunun.", image_for_gemini]
            else:
                prompt_parts = [user_input]
            
            response = st.session_state.chat_model.generate_content(prompt_parts)
            bot_response = response.text
            
            st.session_state.messages.append({
                "role": "bot",
                "content": bot_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
        except Exception as e:
            error_message = f"⚠️ Hata oluştu: {str(e)}"
            st.session_state.messages.append({
                "role": "bot",
                "content": error_message,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    
    st.session_state.uploaded_image = None
    st.session_state.image_preview = None
    st.session_state.input_key += 1  
    st.session_state.enter_pressed = False  
    
    st.rerun()


st.divider()

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.metric("💬 Toplam Mesaj", len(st.session_state.messages))

with info_col2:
    st.metric("🧴 Model", "Gemini 2.0 Flash")

st.markdown("""
    <div style='text-align: center; color: white; padding: 10px;'>
        <p style='font-size: 0.9rem;'>✨ <b>SkinCare Chatbot</b> | 📷 Cilt Analizi | 💾 Konuşma Geçmişi</p>
    </div>
""", unsafe_allow_html=True)