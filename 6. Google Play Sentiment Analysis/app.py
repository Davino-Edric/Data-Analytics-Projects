import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model


# Load the DNN model
@st.cache_resource
def load_dnn_model():
    return load_model('last_model.keras')

dnn = load_dnn_model()

def main():
    # Set page config
    st.set_page_config(
        page_title="FF Sentiment Analysis",
        page_icon="🔍",
        layout="centered"
    )
    
    # Custom CSS for dark theme and styling
    st.markdown("""
        <style>
        .main {
            background-color: #1e1e1e;
        }
        .stTitle {
            color: #ffffff;
            text-align: center;
            padding-bottom: 2rem;
        }
        .success-text {
            color: #90EE90;
            font-weight: bold;
            text-align: center;
            font-size: 18px;
        }
        .error-text {
            color: #ff6b6b;
            font-weight: bold;
            text-align: center;
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("🔍 Mesin Pendeteksi Sentimen Review Uber")
    
    # Create columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Input section
        st.markdown("### Masukkan Review Anda")
        input_data = st.text_input(
            "",
            placeholder="Masukkan Review anda",
            key="review_input"
        )
        
        # Model selection
        st.markdown("### Pilih Model")
        model_selection = st.selectbox(
            "",
            options=['SVM', 'Random Forest', 'DNN'],
            key="model_combo"
        )
        
        # Submit button
        if st.button("🚀 Analyze", type="primary", use_container_width=True):
            if not input_data.strip():
                st.markdown('<p class="error-text">❌ Masukkan input dulu!</p>', unsafe_allow_html=True)
            else:
                # Process the input
                with st.spinner('Menganalisis sentimen...'):
                    try:
                        # Preprocess the data (assuming these functions exist)
                        series_input = pd.Series(input_data)
                        input_preprocess = pd.Series(series_input.apply(preprocess))
                        input_tf = input_preprocess.apply(_tf)
                        input_tfidf = input_tf.apply(tfidf)
                        input_vectorized = input_tfidf.apply(tfidf_vectorizer)
                        input_ready = np.array([np.array(row) for row in input_vectorized])
                        
                        # Make prediction based on selected model
                        if model_selection == 'SVM':
                            input_pred = svm.predict(input_ready)
                        elif model_selection == 'Random Forest':
                            input_pred = rf.predict(input_ready)
                        else:  # DNN
                            input_pred = np.argmax(dnn.predict(input_ready)) + 1
                        
                        # Map prediction to output
                        output_dict = {1: 'Kritik', 2: 'Mixed', 3: 'Pujian'}
                        
                        if isinstance(input_pred, np.ndarray):
                            prediction_value = input_pred.item()
                        else:
                            prediction_value = input_pred
                            
                        output_text = output_dict.get(prediction_value, "Unknown")
                        
                        # Display result
                        st.markdown("### Hasil Analisis")
                        st.markdown(f'<p class="success-text">✅ Teks tersebut adalah: {output_text}</p>', 
                                  unsafe_allow_html=True)
                        
                        # Display confidence or additional info
                        st.info(f"Model yang digunakan: {model_selection}")
                        
                    except Exception as e:
                        st.markdown('<p class="error-text">❌ Terjadi kesalahan dalam pemrosesan!</p>', 
                                  unsafe_allow_html=True)
                        st.error(f"Error details: {str(e)}")
        
        # Add some spacing
        st.markdown("---")
        
        # Instructions or help section
        with st.expander("📋 Petunjuk Penggunaan"):
            st.markdown("""
            1. **Masukkan Review**: Ketik review Uber yang ingin dianalisis
            2. **Pilih Model**: Pilih salah satu model (SVM, Random Forest, atau DNN)
            3. **Klik Analyze**: Tekan tombol untuk memulai analisis
            4. **Lihat Hasil**: Hasil akan menunjukkan apakah review tersebut:
               - **Kritik**: Review negatif
               - **Mixed**: Review netral/campuran
               - **Pujian**: Review positif
            """)

if __name__ == "__main__":
    main()