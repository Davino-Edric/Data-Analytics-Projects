import streamlit as st
import pickle
import pandas as pd
import numpy as np

@st.cache_resource
def load_model_package():
    with open('rf_model_complete.pkl', 'rb') as f:
        return pickle.load(f)

# Load the model package
model_package = load_model_package()
model = model_package['model']
scaler = model_package.get('scaler', None)
feature_columns = model_package['feature_columns']

st.title("Iphone Buy Prediction System")

# Create input fields for each feature
input_data = {}
for feature in feature_columns:
    input_data[feature] = st.number_input(f"Enter {feature}:", value=0.0)

if st.button("Make Prediction"):
    # Convert input to DataFrame with correct column order
    input_df = pd.DataFrame([input_data])[feature_columns]
    
    # Apply same preprocessing as training
    if scaler:
        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)
    else:
        prediction = model.predict(input_df)
    
    # Display results
    st.success(f"Prediction: {prediction[0]}")
    
    # Show prediction probabilities if classification
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(input_scaled if scaler else input_df)
        st.write("Prediction Probabilities:")
        for i, prob in enumerate(probabilities[0]):
            st.write(f"Class {i}: {prob:.3f}")