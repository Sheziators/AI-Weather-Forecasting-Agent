```markdown
# 🌤️ AI Weather Forecasting Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.7-green.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An intelligent, conversational weather assistant powered by **Qwen2.5-7B-Instruct** that provides real-time weather data and answers general knowledge questions using the ReAct (Reasoning + Acting) agent architecture.

## ✨ Features

- 🌡️ **Real-time Weather Data** – Current temperature, humidity, wind speed, pressure, and conditions via WeatherStack API
- 🔍 **Smart Search** – DuckDuckGo integration for facts, capitals, and general queries
- 🧠 **ReAct Agent Logic** – Transparent reasoning with tool calling and observation handling
- 💬 **Chat Interface** – Clean, modern Streamlit UI with message history
- 🎨 **Animated Responses** – Weather-based emoji alerts (☀️ 🌧️ ❄️) and smooth fade-in effects
- 🔍 **Explainable AI** – Expandable panel showing every tool call and reasoning step
- ⚡ **Cached Performance** – Faster repeated queries with agent caching
- 📱 **Responsive Design** – Works on desktop, tablet, and mobile

## 🚀 Live Demo

[Deploy to Streamlit Cloud](https://streamlit.io/cloud) – One-click deployment available

## 📋 Prerequisites

- Python 3.11 or higher
- Hugging Face API token ([Get one here](https://huggingface.co/settings/tokens))
- WeatherStack API key ([Free tier available](https://weatherstack.com/))

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-weather-forecasting-agent.git
cd ai-weather-forecasting-agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up API keys

Create a `.streamlit/secrets.toml` file:

```toml
HUGGINGFACEHUB_ACCESS_TOKEN = "hf_your_token_here"
WEATHERSTACK_API_KEY = "your_weatherstack_api_key"
```

Or use environment variables:

```bash
export HUGGINGFACEHUB_ACCESS_TOKEN="hf_your_token_here"
export WEATHERSTACK_API_KEY="your_weatherstack_api_key"
```

### 5. Run the application

```bash
streamlit run app.py
```

## 📦 Dependencies

```
streamlit
langchain
langchain-community
langchain-core
langchain-huggingface
ddgs
requests
huggingface-hub
transformers
sentence-transformers
```

## 🎯 Usage Examples

| Query | Agent Action |
|-------|--------------|
| "What's the weather in Tokyo?" | Direct weather API call |
| "What is the capital of France and its current weather?" | Search → Weather |
| "Should I take an umbrella in London?" | Weather + reasoning |
| "Compare temperature in Delhi and Mumbai" | Sequential weather calls |
| "What's the humidity in Rio?" | Specific weather attribute |

### Sample Interaction

```
User: What is the capital of Japan and its current weather?

Assistant: The capital of Japan is Tokyo. 
The current weather in Tokyo is partly cloudy, 22°C (feels like 22°C), 
humidity 65%, wind 12 km/h, pressure 1015 mb.

☁️ Cloudy skies - Perfect for a cozy day!

🔍 View reasoning steps:
Step 1: web_search
📥 Input: capital of Japan
📤 Observation: Tokyo

Step 2: get_weather_data
📥 Input: Tokyo
📤 Observation: Partly cloudy, 22°C...
```

## 🏗️ Architecture

```
User Query → Streamlit UI → ReAct Agent → Tool Selection
                                          ↓
                              ┌───────────┴───────────┐
                              ↓                       ↓
                        WeatherStack API        DuckDuckGo Search
                              ↓                       ↓
                        └───────────┬───────────┘
                                    ↓
                            LLM Reasoning (Qwen2.5)
                                    ↓
                            Final Answer → User
```

## 🔧 Configuration

### Agent Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | Qwen/Qwen2.5-7B-Instruct | Hugging Face model |
| Temperature | 0.01 | Low randomness for consistent output |
| Max tokens | 512 | Response length limit |
| Max iterations | 5 | Tool call attempts per query |

### Customization

- **Change LLM** – Update `repo_id` in `HuggingFaceEndpoint`
- **Add tools** – Create new `@tool` decorated functions
- **Modify prompt** – Edit `prompt_template` in `get_agent()`

## 🚢 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard:
   - `HUGGINGFACEHUB_ACCESS_TOKEN`
   - `WEATHERSTACK_API_KEY`
5. Deploy!

### Deploy locally with Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t weather-agent .
docker run -p 8501:8501 weather-agent
```

## 📁 Project Structure

```
ai-weather-forecasting-agent/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── .streamlit/
│   └── secrets.toml       # API keys (gitignored)
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No good DuckDuckGo Search Result" | The app automatically falls back to common facts database |
| Slow first response | Agent caching warms up after first query |
| Weather API rate limit | Free tier has monthly limits; upgrade for production |
| ImportError on AgentExecutor | Use `langchain-classic` or downgrade to langchain 0.3.0 |

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) – Agent framework
- [Qwen2.5](https://huggingface.co/Qwen) – LLM provider
- [WeatherStack](https://weatherstack.com/) – Weather API
- [Streamlit](https://streamlit.io/) – UI framework
- [DuckDuckGo](https://duckduckgo.com/) – Search API

## 📧 Contact

Tathagat Shaw – tathagatshaw@gmail.com

Project Link: https://github.com/Sheziators/AI-Weather-Forecasting-Agent

## ⭐ Show your support

Give a ⭐️ if this project helped you!

---

Built with ❤️ using LangChain & Streamlit
```

## 📋 Also create a `LICENSE` file

```markdown
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🎯 Quick Checklist Before Pushing to GitHub

- [ ] Remove any hardcoded API keys from `app.py`
- [ ] Add `.streamlit/secrets.toml` to `.gitignore`
- [ ] Test the app locally one last time
- [ ] Update the `yourusername` and contact info in README
- [ ] Add a screenshot of the app (create a `screenshots/` folder)
- [ ] Push to GitHub and enable GitHub Pages if desired
