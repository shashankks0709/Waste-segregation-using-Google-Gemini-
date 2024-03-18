import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import io
import google.generativeai as genai

# Specify the path or URL to the Google logo
google_logo_url = 'google.png'  # Replace with your actual logo path or URL

# Set Streamlit page configuration
st.set_page_config(layout="wide")

# # Use columns to place the logo and title next to each other
# col1, col2 = st.columns([1, 5])  # Adjust the ratio as needed for your layout

# with col1:
#     st.image(google_logo_url, width=100)  # Display the Google logo

# with col2:
#     st.markdown("<h1 style='text-align: left; color: black;'>Real-Time Waste Classification and Disposal Educator</h1>", unsafe_allow_html=True)



def set_container_width(width):
    # Set a custom width for the main content container.
    st.markdown(f'''
        <style>
            .css-1lcbmhc .css-1d391kg {{"max-width": "{width}px"}}
        </style>
    ''', unsafe_allow_html=True)

# Set Streamlit page configuration
#st.set_page_config(layout="wide")

# Set custom width for the Streamlit container
set_container_width(width=1500)  # Adjust the width as needed

# Custom CSS to reduce the height of the video capture element
def custom_css():
    st.markdown("""
        <style>
        /* Adjust the height of the camera input */
        .stCamera > div > div {
            height: 300px; /* Set this to your desired value */
        }
        /* Adjust the camera viewfinder size to fit the new height */
        .stCamera video {
            height: 300px !important; /* Set this to your desired value */
        }
        </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
custom_css()



# Configure your Google API
GOOGLE_API_KEY = 'YOUR API KEY'  # Replace with your actual Google API key
genai.configure(api_key=GOOGLE_API_KEY)

# Define the Gemini model
model = genai.GenerativeModel('gemini-pro-vision')

# Define a mapping of disposal recommendations to image URLs or paths
disposal_images = {
    'recycle': 'recycle.jpg',  # Replace with your actual image path or URL
    'trash': 'trash.jpg',      # Replace with your actual image path or URL
    'do not put in the dustbin': 'notdustbin.jpg',  # Replace with your actual image path or URL
}

def process_frame_with_gemini_api(image_data):
    """
    Sends the captured image to the Gemini API for processing.
    
    Args:
        image_data: The image data captured from the Streamlit camera input.
    
    Returns:
        A string with the API response (e.g., "Object: Bottle, Dispose: Recycle").
    """
    try:
        # Convert the image data to a PIL Image
        img = Image.open(io.BytesIO(image_data.getvalue()))
        
        # Use the Gemini model for processing
        response = model.generate_content(["You are an expert in waste segregation. Your task is to analyze the image provided and: 1) Identify the object(s) being discarded. 2) Suggest the appropriate disposal method based on the university's waste management guidelines. There are only three disposal methods: 'trash', 'recycle', or 'do not put in the dustbin'. For each object identified, provide your recommendation in the format: 'Object: [object name], Dispose: [disposal method]'. If there are multiple objects or recommendations, list them comma-separated.", img])
        response.resolve()
        
        # Return the text part of the response
        return response.text
    except Exception as e:
        return f"Error processing image with Gemini API: {e}"

# Initialize session state for last processed time, processed text, and disposal image
if 'last_processed' not in st.session_state:
    st.session_state.last_processed = datetime.now() - timedelta(seconds=10)
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = ""
if 'disposal_image' not in st.session_state:
    st.session_state.disposal_image = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Custom CSS for styling
def custom_css():
    st.markdown("""
        <style>
        /* General app styling */
        .css-18e3th9 {
            background-color: #f0f2f6;
            color: #333;
        }
        /* Style the title */
        h1 {
            color: #0e1117;
        }
        /* Style the buttons */
        .stButton>button {
            border: 2px solid #4CAF50;
            border-radius: 20px;
            color: white;
            background-color: #4CAF50;
            padding: 10px 24px;
            cursor: pointer;
            font-size: 18px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        /* Style the camera input */
        .stCamera {
            border: 4px dashed #4CAF50;
            border-radius: 20px;
        }
        /* Style the text */
        .stTextInput>div>div>input {
            color: #4CAF50;
        }
        /* Style for the image caption */
        .stImage>div>div>figure>figcaption {
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS
custom_css()


# Display the camera widget and process the image
if not st.session_state.show_results:
    captured_image = st.camera_input("Capture", key="camera", help="Capture image from your camera")
    if st.button('Process Now'):
        if captured_image is not None:
            # Process the image through the Gemini API
            processed_text = process_frame_with_gemini_api(captured_image)
            st.session_state.processed_text = processed_text
            # Extract the disposal recommendation from the processed text
            disposal_recommendation = processed_text.split('Dispose: ')[-1].strip().lower()
            # Map the recommendation to the corresponding image
            st.session_state.disposal_image = disposal_images.get(disposal_recommendation, None)
            # Navigate to the processing result "page"
            st.session_state.show_results = True
            st.experimental_rerun()

# Display the processing results
if st.session_state.show_results:
    # Display the processed text with larger font size and improved formatting
    # # Use columns to place the logo and title next to each other
    col1, col2 = st.columns([1, 5])  # Adjust the ratio as needed for your layout

    with col1:
        st.image(google_logo_url, width=150)  # Display the Google logo

    with col2:
        st.markdown("<h1 style='text-align: left; color: black;'>Real-Time Waste Classification and Disposal Educator using Gemini</h1>", unsafe_allow_html=True)
    if st.session_state.processed_text:
        st.markdown(f"""
        <div style="font-size:24px; font-weight:bold; color:#4CAF50; margin-bottom:20px;">
            Last Processed: {st.session_state.last_processed.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        <div style="font-size:20px; color:black; background-color:#f0f2f6; padding:10px; border-radius:10px; margin-bottom:20px;">
            Processed Text: {st.session_state.processed_text}
        </div>
        """, unsafe_allow_html=True)
# Display the disposal image if available
if st.session_state.disposal_image and st.session_state.show_results:
    # Use columns to center the image. Adjust the ratios as needed to better center the image.
    col1, col2, col3 = st.columns([1,2,1])

    with col2:  # This puts the image in the center column
        # Display the image with a specified width to make it bigger. Adjust the width as needed.
        st.image(st.session_state.disposal_image, caption="Type of Disposal", width=300)

# Button to go back to the camera
if st.session_state.show_results:  # Show the button only if in the results view
    if st.button('Back to camera'):
        # Reset relevant states to go back to the camera view
        st.session_state.show_results = False
        st.session_state.disposal_image = None  # Clear the disposal image state
        st.experimental_rerun()


