import yaml
import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
from crew import emailCrew

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = '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'

# Configure Streamlit app
def configure():
    st.set_page_config(
        page_title="Generation phase",
        page_icon="📃",
        layout="wide"
    )
    st.title("Email Generator")
    temperature = st.slider('Creativity', min_value=0.0, max_value=1.0, step=0.1, value=0.5)
    return temperature

# Load campaign inputs from YAML file
def load_inputs():
    try:
        with open('campaign_inputs.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None

# Create HTML header


# Main function to run the app
def run():
    temperature = configure()
    with open(r'/home/arun-kumar-arali/Downloads/Epsilon-Project/config/tasks.yaml', 'r') as file:
        tasks = yaml.safe_load(file)
    description = st.text_area("Enter the description for the email generation task")
    result = None
    if st.button("👉 Update Description and Run 👈"):
        tasks['email_generation_task']['description'] = description
        with open(r'/home/arun-kumar-arali/Downloads/Epsilon-Project/config/tasks.yaml', 'w') as file:
            yaml.dump(tasks, file, default_flow_style=False, allow_unicode=True)

        st.success("✔️ Description updated and task configuration saved!")
        result = emailCrew(temperature).crew().kickoff()
        
        try:
            if result:
                st.subheader("Generated Email!")
                
                # Load inputs from file
                inputs = load_inputs()
                if inputs:
                    
                   
                    
                    # Combine header, result, and footer
                    full_email = f"""
                    
                            <div class="content" style=" background-color:white;">
                                {result}
                            
                    """
                    
                    # Display the email as an HTML page
                    st.components.v1.html(full_email, height=600, scrolling=True)
                    
                else:
                    # Display the result directly if no inputs found
                    st.markdown(result, unsafe_allow_html=True)
                    st.warning("No campaign inputs found. The email is displayed without additional formatting.")
        except RuntimeError:
            st.error("Error while generating the output!")

if __name__ == "__main__":
    run()
