# L'ARROGANCE Meme Creator

A Python application that generates satirical memes with the theme "L'ARROGANCE!" using AI-generated punchlines.

## Project Structure

This project follows the MVC (Model-View-Controller) architecture:

```
src/
├── models/           # Data models and database operations
├── views/            # Presentation logic
├── controllers/      # Business logic
├── clients/          # External API clients
├── data/             # Data files and templates
├── utils/            # Utility functions
├── tests/            # Test files
├── main.py           # Main entry point
└── generate_meme.py  # Command-line interface
```

### MVC Components

#### Models

- `MemeModel`: Handles meme data storage and retrieval
- `PunchlineModel`: Manages punchline evaluation data
- `VideoModel`: Manages video configuration and paths

#### Views

- `VideoView`: Handles video rendering and display
- `TelegramView`: Formats messages for Telegram

#### Controllers

- `MemeController`: Orchestrates the meme generation process
- `PunchlineController`: Handles punchline generation and evaluation
- `VideoController`: Manages video processing

## Features

- Generate satirical punchlines using OpenAI GPT models
- Quality evaluation pipeline for selecting the best punchlines
- Video generation with text overlay
- Telegram integration for sharing memes
- Batch generation mode for multiple memes
- Economy mode to reduce API token usage

## Usage

### Basic Usage

```bash
python src/main.py
```

### Command-line Options

```bash
python src/generate_meme.py --subject "Your subject" --economy --telegram
```

Options:
- `--subject`, `-s`: Subject for the meme (or comma-separated list in batch mode)
- `--text`, `-t`: Custom text to use instead of generating a punchline
- `--economy`, `-e`: Enable economy mode (use GPT-3.5 instead of GPT-4)
- `--telegram`: Force sending to Telegram
- `--no-telegram`: Force not sending to Telegram
- `--batch`, `-b`: Batch mode for generating multiple memes

## Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TELEGRAM_AUTO_SEND=true
USE_QUALITY_PIPELINE=true
DEFAULT_NUM_CANDIDATES=3
DEFAULT_QUALITY_THRESHOLD=0.7
```

## Dependencies

- Python 3.8+
- OpenAI API
- MoviePy
- python-telegram-bot
- python-dotenv

## Installation

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 