# "L'ARROGANCE!" Meme Generator 🎬

A video meme generator that uses Ludovic Magnin's template shouting "L'ARROGANCE!" (THE ARROGANCE!). The tool automatically adds custom text or GPT-4 generated content to the top of the video, and can send it directly to Telegram.

![Meme Example](docs/images/example.jpg)

## 📑 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Quality Pipeline](#-quality-pipeline)
- [Batch Generation](#-batch-generation)
- [Troubleshooting](#-troubleshooting)

## 🚀 Features

- ✨ Automatic generation of humorous punchlines with OpenAI GPT-4
- 🔍 Quality pipeline to evaluate and select the best punchlines
- 📝 Custom text overlay on the template video
- 🎥 Export of the video with embedded text
- 💰 Token economy mode (uses GPT-3.5-turbo instead of GPT-4)
- 📦 Batch generation from a JSON file of subjects
- 📱 Automatic sending of memes to Telegram
- 🏷️ Automatic generation of relevant hashtags
- 📄 Generation of engaging descriptions for social media
- 📊 Analysis and statistics on the quality of generated punchlines

## 📂 Project Structure

```
arrogance-meme-creator/
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment variables file
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── run-meme.sh           # Shell script to run the meme generator
├── data/                 # Persistent data
│   └── quality_data.db   # Database of punchlines and evaluations
├── docs/                 # Additional documentation
│   └── images/           # Images for documentation
├── output/               # Folder where generated files are stored
│   ├── videos/           # Generated meme videos
│   ├── reports/          # Batch generation reports and tests
│   └── exports/          # Exported files (punchlines, etc.)
└── src/                  # Source code
    ├── __init__.py       # Package initialization
    ├── main.py           # Main entry point
    ├── generate_meme.py  # Meme generation script
    ├── core/             # Main classes
    │   ├── meme_generator.py # Main meme generator class
    │   ├── quality_pipeline.py # Quality pipeline for punchlines
    │   └── video_processor.py # Video processing with MoviePy
    ├── clients/          # Clients for external APIs
    │   ├── openai_client.py  # Client for OpenAI API
    │   └── telegram_client.py # Client for Telegram API
    ├── data/             # Data used by the generator
    │   ├── template.mp4      # "L'ARROGANCE!" template video
    │   ├── test_subjects.json # Example subjects for generation
    │   └── json.json         # Default JSON file for batch generation
    ├── utils/            # Various utilities
    │   ├── export_punchlines.py # Utility to export punchlines
    │   └── punchlines_stats.py # Utility to display punchline statistics
    └── tests/            # Unit tests
        ├── test_quality_pipeline.py # Tests for the quality pipeline
        └── test_quality_pipeline_mock.py # Tests with mocks for the quality pipeline
```

## 📋 Prerequisites

- Python 3.12
- OpenAI API key (for punchline generation)
- Telegram Bot (for sending memes to Telegram, optional)

## 🔧 Installation

1. Clone this repository
   ```bash
   git clone https://github.com/helios-code/arrogance-meme-creator.git
   cd arrogance-meme-creator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file and add your OpenAI API key and Telegram parameters.

## ⚙️ Configuration

The `.env` file contains all the necessary configurations for the meme generator. Here are the main options:

### General Configuration
```
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
LOG_LEVEL=info
```

### OpenAI API
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Meme Generator Configuration
```
TEMPLATE_VIDEO_PATH=src/template.mp4
OUTPUT_DIRECTORY=output
FONT_PATH=Arial
FONT_SIZE=40
TEXT_COLOR=white
TEXT_POSITION_Y=0.35  # 35% from the top (about 250px on a 720p video)
TEXT_MARGIN_X=0.01    # 1% margin on each side
TEXT_BACKGROUND=black
```

### Token Economy Mode
```
ECONOMY_MODE=false  # Uses GPT-3.5-turbo instead of GPT-4
```

### Telegram Configuration
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_AUTO_SEND=false
```

### Quality Pipeline Configuration
```
USE_QUALITY_PIPELINE=true
QUALITY_THRESHOLD=0.7
NUM_PUNCHLINE_CANDIDATES=3
```

## 🎮 Usage

### Simple Generation

```bash
cd src
python generate_meme.py
```

### With Custom Text

```bash
cd src
python generate_meme.py -t "When the intern pushes to prod on Friday at 5pm"
```

### With a Specific Subject

```bash
cd src
python generate_meme.py -s "Swiss banks"
```

### Token Economy Mode

```bash
cd src
python generate_meme.py -e
```

### Send to Telegram

```bash
cd src
python generate_meme.py -s "The media" --telegram
```

### Using the Shell Script

The `run-meme.sh` script makes it easier to use the generator:

```bash
./run-meme.sh --help
```

## 🔍 Quality Pipeline

The quality pipeline significantly improves the relevance and impact of generated punchlines by following these steps:

1. **Multiple Generation**: Generates multiple candidate punchlines for each subject
2. **Automatic Evaluation**: Analyzes each punchline according to 5 key criteria:
   - **Originality**: Uniqueness and freshness of the punchline
   - **Humor**: Comic potential and humorous impact
   - **Relevance**: Appropriateness to the requested subject
   - **Conciseness**: Optimal formulation and appropriate length
   - **Impact**: Viral potential and memorability
3. **Intelligent Filtering**: Eliminates punchlines that don't exceed a configurable quality threshold
4. **Optimal Selection**: Chooses the best punchline for meme generation
5. **Continuous Analysis**: Stores evaluations in a database to improve future generations

### Pipeline Configuration

You can configure the quality pipeline in the `.env` file:

```
# Enable/disable the quality pipeline
USE_QUALITY_PIPELINE=true

# Quality threshold (between 0 and 1)
QUALITY_THRESHOLD=0.7

# Number of candidate punchlines to generate
NUM_PUNCHLINE_CANDIDATES=3
```

## 📦 Batch Generation

You can generate multiple memes from a JSON file containing subjects:

```bash
cd src
python generate_meme.py -b "test_subjects.json" -l 5
```

JSON file format:

```json
{
  "subjects": [
    "Politicians",
    "Influencers",
    "Developers"
  ]
}
```

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Error**: Check that your API key is valid and that you have available credits.

2. **Video Generation Error**: Make sure the template.mp4 file exists in the src folder.

3. **Telegram Sending Error**: Check that your bot token and chat ID are correct.

### Logs

Logs are available in the console and can help diagnose problems.

---

Created by Loic Mancino - [GitHub](https://github.com/loicmancino) 