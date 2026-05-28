# app.py
import os
import sys
import json
import requests
from typing import Dict, Any, List, Tuple

import streamlit as st

# LangChain imports - using classic package for compatibility
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from ddgs import DDGS

# ======================== CONFIGURATION ========================
st.set_page_config(
    page_title="🌤️ AI Weather Assistant",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disable warnings and tracing
import warnings
warnings.filterwarnings('ignore')
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Custom CSS for animations and styling
st.markdown("""
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeIn 0.5s ease-out;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .step-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff4b4b;
    }
    .stSpinner > div {
        border-top-color: #ff4b4b !important;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1 {
        background: linear-gradient(120deg, #ff4b4b, #ff9a9e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ======================== ENVIRONMENT VARIABLES ========================
def get_api_keys():
    """Retrieve API keys from secrets or environment"""
    try:
        hf_token = st.secrets["HUGGINGFACEHUB_ACCESS_TOKEN"]
        weather_token = st.secrets["WEATHERSTACK_API_KEY"]
    except:
        # Fallback for local development
        hf_token = os.environ.get("HUGGINGFACEHUB_ACCESS_TOKEN", "")
        weather_token = os.environ.get("WEATHERSTACK_API_KEY", "b2371d9babefdb3ce1a8adececadc290")
    
    if not hf_token:
        st.error("⚠️ HuggingFace API token not found. Please set it in secrets.toml or environment.")
        st.stop()
    
    return hf_token, weather_token

HF_TOKEN, WEATHER_API_KEY = get_api_keys()
os.environ["HUGGINGFACEHUB_ACCESS_TOKEN"] = HF_TOKEN

# ======================== WORKING SEARCH TOOL ========================
@tool
def web_search(query: str) -> str:
    """Search the web for current information. Input is a search query."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                # Fallback for common queries
                return get_fallback_answer(query)
            
            output = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Untitled')
                body = result.get('body', '')
                # Clean up the body text
                body = body.replace('\n', ' ').strip()
                if len(body) > 300:
                    body = body[:300] + "..."
                output.append(f"**{i}. {title}**\n   {body}")
            
            return "\n\n".join(output)
    
    except Exception as e:
        return get_fallback_answer(query)

def get_fallback_answer(query: str) -> str:
    """Fallback answers for common queries when search fails"""
    query_lower = query.lower()
    
    # Capital cities database
    capitals = {
        "france": "Paris",
        "germany": "Berlin",
        "japan": "Tokyo",
        "india": "New Delhi",
        "italy": "Rome",
        "spain": "Madrid",
        "united kingdom": "London",
        "uk": "London",
        "usa": "Washington, D.C.",
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "australia": "Canberra",
        "china": "Beijing",
        "russia": "Moscow",
        "brazil": "Brasília",
        "jharkhand": "Ranchi",
        "california": "Sacramento",
        "texas": "Austin",
        "new york": "Albany"
    }
    
    # Check for capital queries
    if "capital of" in query_lower:
        for country, capital in capitals.items():
            if country in query_lower:
                return f"The capital of {country.title()} is {capital}."
        return "I couldn't find that capital. Please try a more specific search or ask about weather."
    
    # Check for weather-related fallbacks
    if any(word in query_lower for word in ["weather", "temperature", "rain", "sunny", "cloud"]):
        return "For accurate weather information, please specify a city name like 'weather in London'."
    
    return "I couldn't find an answer. Please try rephrasing your question or ask about specific locations for weather."

# ======================== WEATHER TOOL ========================
@tool
def get_weather_data(city: str) -> str:
    """Get REAL current weather data for a city. Input is a city name (e.g., 'London', 'New York')."""
    url = f'http://api.weatherstack.com/current?access_key={WEATHER_API_KEY}&query={city}'
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'error' in data:
            error_msg = data['error'].get('info', 'Unknown error')
            if 'rate limit' in error_msg.lower():
                return "Weather API rate limit reached. Please try again in a minute."
            return f"Weather API Error: {error_msg}"
        
        if 'current' in data:
            temp = data['current'].get('temperature', 'N/A')
            feelslike = data['current'].get('feelslike', 'N/A')
            desc = data['current'].get('weather_descriptions', ['Unknown'])[0]
            hum = data['current'].get('humidity', 'N/A')
            wind = data['current'].get('wind_speed', 'N/A')
            pressure = data['current'].get('pressure', 'N/A')
            obs_time = data['current'].get('observation_time', 'N/A')
            
            return (f"{desc}, {temp}°C (feels like {feelslike}°C), "
                    f"humidity {hum}%, wind {wind} km/h, pressure {pressure} mb. "
                    f"Observation time: {obs_time} UTC")
        
        location = data.get('location', {}).get('name', city)
        return f"Could not fetch weather for {location}. Please check the city name."
    
    except requests.exceptions.Timeout:
        return "Weather service timeout. Please try again."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

# ======================== AGENT SETUP ========================
@st.cache_resource
def get_agent():
    """Create and cache the ReAct agent with working tools"""
    try:
        llm_instance = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            max_new_tokens=512,
            temperature=0.01,
            stop_sequences=["Observation:", "\nObservation:"],
            huggingfacehub_api_token=HF_TOKEN,
            timeout=30
        )
        
        chat_model = ChatHuggingFace(llm=llm_instance)
        
        # Tools list with working search
        tools = [web_search, get_weather_data]
        tool_names = ["web_search", "get_weather_data"]
        
        prompt_template = """You are a helpful assistant. Answer the following question by using the available tools.

Tools:
{tools}

To use a tool, follow this EXACT format:

Thought: (your reasoning)
Action: tool_name (must be one of {tool_names})
Action Input: the input for the tool

After you receive an Observation, you can continue with another Thought/Action or output Final Answer.

Here is an example:

Question: What is the capital of France and its weather?
Thought: I need to find the capital first.
Action: web_search
Action Input: capital of France
Observation: Paris is the capital.
Thought: Now I can get the weather.
Action: get_weather_data
Action Input: Paris
Observation: Sunny, 25°C
Thought: I now know the final answer.
Final Answer: The capital is Paris and the weather is sunny, 25°C.

Do NOT write Observation yourself. Do NOT skip Action after Thought. Always write Action and Action Input on separate lines.

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(prompt_template)
        agent = create_react_agent(llm=chat_model, tools=tools, prompt=prompt)
        
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        return executor
    
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.stop()

# ======================== HELPER FUNCTIONS ========================
def display_weather_animation(weather_text: str):
    """Display a fun animation based on weather description"""
    weather_lower = weather_text.lower()
    if "sunny" in weather_lower or "clear" in weather_lower:
        st.markdown("☀️ **Sunny weather!** *Don't forget sunscreen!*")
        st.balloons()
    elif "rain" in weather_lower or "drizzle" in weather_lower:
        st.markdown("🌧️ **Rain detected!** *Grab an umbrella!* ☔")
        st.snow()  # Using snow as rain effect
    elif "cloud" in weather_lower:
        st.markdown("☁️ **Cloudy skies** *Perfect for a cozy day!*")
    elif "snow" in weather_lower:
        st.markdown("❄️ **Snowy weather!** *Stay warm!* 🧣")
        st.snow()
    elif "storm" in weather_lower or "thunder" in weather_lower:
        st.markdown("⛈️ **Storm alert!** *Stay safe indoors!* ⚡")

def format_intermediate_steps(steps: List[Tuple[Any, str]]) -> str:
    """Format intermediate steps for display"""
    formatted = []
    for i, (action, observation) in enumerate(steps, 1):
        tool_name = getattr(action, 'tool', 'Unknown')
        # Handle both string and dict tool inputs
        tool_input = getattr(action, 'tool_input', '')
        if isinstance(tool_input, dict):
            tool_input = str(tool_input)
        
        # Truncate long observations
        if len(observation) > 500:
            observation = observation[:500] + "..."
        
        formatted.append(f"""
**Step {i}: {tool_name}**  
📥 Input: `{tool_input}`  
📤 Observation: {observation}
""")
    return "\n".join(formatted)

# ======================== MAIN APP ========================
def main():
    st.title("🌤️  AI Weather Forecasting Agent")
    st.caption("Powered by Qwen2.5-7B-Instruct | WeatherStack | DuckDuckGo Search")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings & Info")
        st.markdown("---")
        st.markdown("### 🎯 What can I do?")
        st.markdown("""
        - 🌡️ Get current weather for any city
        - 🔍 Search for capitals, facts, and general info
        - 🤔 Answer complex multi-step questions
        - 💬 Natural conversation about weather
        
        **Example queries:**
        - "What's the weather in Tokyo?"
        - "What is the capital of France and its current weather?"
        - "Compare weather in London and Paris"
        - "Should I take an umbrella in Mumbai today?"
        """)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Status indicators
        st.markdown("### 🔌 API Status")
        col1, col2 = st.columns(2)
        with col1:
            if HF_TOKEN:
                st.success("HuggingFace ✅")
            else:
                st.error("HuggingFace ❌")
        with col2:
            if WEATHER_API_KEY:
                st.success("WeatherStack ✅")
            else:
                st.error("WeatherStack ❌")
        
        st.markdown("---")
        st.caption("Built with Intelligence using LangChain & Streamlit")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "intermediate" in message and message["intermediate"]:
                with st.expander("🔍 View reasoning steps"):
                    st.markdown(message["intermediate"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about weather, capitals, or anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt, "intermediate": ""})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking... (may take a few seconds)"):
                try:
                    agent = get_agent()
                    response = agent.invoke({"input": prompt})
                    final_answer = response.get("output", "Sorry, I couldn't process that.")
                    intermediate_steps = response.get("intermediate_steps", [])
                    
                    # Format intermediate steps
                    steps_display = format_intermediate_steps(intermediate_steps) if intermediate_steps else ""
                    
                    # Display final answer
                    st.markdown(final_answer)
                    
                    # Weather animation if weather mentioned
                    weather_keywords = ["°c", "temperature", "humidity", "wind", "rain", "sunny", "cloud", "snow", "storm"]
                    if any(word in final_answer.lower() for word in weather_keywords):
                        display_weather_animation(final_answer)
                    
                    # Show reasoning in expander
                    if steps_display:
                        with st.expander("🔍 See how I got this answer"):
                            st.markdown(steps_display)
                    
                    # Save to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_answer,
                        "intermediate": steps_display
                    })
                    
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}. Please try again with a simpler query."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "intermediate": ""
                    })

if __name__ == "__main__":
    main()