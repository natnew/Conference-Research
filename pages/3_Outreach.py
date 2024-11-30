import streamlit as st
from langchain.llms import OpenAI
import streamlit.components.v1 as components


# Particles.js HTML Content
particles_js = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }
  </style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content">
    <!-- Placeholder for Streamlit content -->
  </div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""

# Render the Particles.js Background
components.html(particles_js, height=0, width=0)

#####
####

st.sidebar.title("Conference Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research 
    workflows. It combines generative AI, voice-to-action capabilities, 
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
    methodologies to deliver efficient and accurate results.

    """)

# Sidebar information
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "We use multi-agent systems and other AI technologies to power this app."
    )
    st.markdown(
        "This tool is a work in progress."
    )
    openai_api_key = st.secrets["openai_api_key"]
    

st.title("💬 Outreach - Email Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference. :balloon:")

def generate_response(input_text):
    try:
        llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        response = llm(input_text)
        st.info(response)
    except Exception as e:
        st.error(f"Error generating response: {e}")

with st.form('my_form'):
    text = st.text_area('Enter text:', 'Craft emails to participants to reach out and engage with them before the conference.')
    submitted = st.form_submit_button('Submit')
    
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        else:
            generate_response(text)

