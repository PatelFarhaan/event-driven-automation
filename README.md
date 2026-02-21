# Event-Driven Automation System

A multi-threaded event distribution platform that automates the process of publishing events across multiple partner sites (Eventbrite, EventsHigh, EventSeeker, Hook2Events, TownScript, DoAttend). Reads event data from a MySQL database and concurrently posts formatted event details to each platform via their respective APIs and web automation.

## Tech Stack

- **Language:** Python 3.x
- **Database:** MySQL (connection pooling)
- **Web Scraping:** Selenium, BeautifulSoup
- **Cloud Storage:** Google Cloud Storage
- **APIs:** Eventbrite API, EventsHigh API, EventSeeker API
- **Concurrency:** Python Threading
- **Image Processing:** Pillow (PIL)

## Features

- Automated event data extraction from MySQL database
- Multi-threaded concurrent posting to 6+ event platforms
- Eventbrite: Full API integration for event creation, ticketing, and media upload
- EventsHigh: Auth0 authentication with event publishing via REST API
- EventSeeker: Session-based web automation for venue and event creation
- TownScript: Selenium-based browser automation for event publishing
- DoAttend: Full browser automation with date/time picker interaction
- Google Cloud Storage integration for image hosting
- Configurable event categorization and ticket management
- Database status tracking for published events
- Comprehensive logging to file

## Prerequisites

- Python 3.6 or higher
- MySQL server with event database schema
- Google Chrome and ChromeDriver (for Selenium-based sites)
- Google Cloud service account credentials (for image hosting)
- API keys for supported platforms
- pip

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Event-Driven-Automation-System
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   ```

5. Set up the Google Cloud credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
   ```

6. Ensure MySQL is running with the required database schema.

## Environment Variables

| Variable                       | Description                          | Required |
|--------------------------------|--------------------------------------|----------|
| `DB_HOST`                      | MySQL database host                  | Yes      |
| `DB_NAME`                      | MySQL database name                  | Yes      |
| `DB_USER`                      | MySQL database user                  | Yes      |
| `DB_PASSWORD`                  | MySQL database password              | Yes      |
| `GOOGLE_APPLICATION_CREDENTIALS`| Path to GCP service account JSON    | Yes      |
| `EVENTBRITE_API_KEY`           | Eventbrite OAuth token               | Yes      |
| `EVENTSHIGH_CLIENT_ID`         | EventsHigh Auth0 client ID          | Yes      |
| `EVENTSHIGH_USERNAME`          | EventsHigh login username            | Yes      |
| `EVENTSHIGH_PASSWORD`          | EventsHigh login password            | Yes      |
| `EVENTSHIGH_AUTH0_CLIENT`      | EventsHigh Auth0 client token        | Yes      |
| `EVENTSHIGH_BEARER_TOKEN`      | EventsHigh API bearer token          | Yes      |
| `EVENTSEEKER_EMAIL`            | EventSeeker account email            | Yes      |
| `EVENTSEEKER_PASSWORD`         | EventSeeker account password         | Yes      |
| `HOOK2EVENTS_EMAIL`            | Hook2Events account email            | Yes      |
| `HOOK2EVENTS_PASSWORD`         | Hook2Events account password         | Yes      |
| `DOATTEND_EMAIL`               | DoAttend account email               | Yes      |
| `DOATTEND_PASSWORD`            | DoAttend account password            | Yes      |
| `TOWNSCRIPT_EMAIL`             | TownScript account email             | Yes      |
| `TOWNSCRIPT_PASSWORD`          | TownScript account password          | Yes      |

## How to Run

```bash
python app.py
```

The system will:
1. Connect to the MySQL database and fetch events marked as "ready to upload"
2. Distribute events to the appropriate partner site queues
3. Launch concurrent threads to publish events on each platform
4. Log all activity to `EventsLog.log`

## Project Structure

```
Event-Driven-Automation-System/
├── app.py                              # Main entry point and thread orchestrator
├── requirements.txt                    # Python dependencies
├── __init__.py
├── common_utils/
│   ├── __init__.py
│   ├── common_files.py                 # MySQL queries and event data extraction
│   └── event_details.txt              # Runtime event queue
├── sites/
│   ├── eventbrite/
│   │   ├── app.py                      # Eventbrite API integration
│   │   ├── main_resp.py                # Response data formatting
│   │   ├── test.py                     # Test scripts
│   │   └── event_details.txt
│   ├── eventhigh/
│   │   ├── __init__.py
│   │   ├── login_crawl.py              # Auth0 authentication
│   │   ├── data_formation.py           # Event data formatting
│   │   ├── data_posting.py             # API posting logic
│   │   ├── google_image.py             # GCS image upload
│   │   ├── categories.py               # Category mapping
│   │   ├── update_db.py                # Database status updates
│   │   └── main_resp.py
│   ├── eventseeker/
│   │   ├── __init__.py
│   │   ├── login_crawl.py              # Session authentication
│   │   ├── data_formation.py           # Event data formatting
│   │   ├── data_posting.py             # Web form posting
│   │   ├── image.py                    # Image handling
│   │   └── main_resp.py
│   ├── hook2events/
│   │   ├── __init__.py
│   │   ├── login_crawl.py              # Session authentication
│   │   ├── data_formation.py           # Event data formatting
│   │   ├── data_posting.py             # API posting
│   │   ├── image.py                    # Image handling
│   │   └── main_resp.py
│   ├── townscript/
│   │   ├── app.py                      # Selenium browser automation
│   │   ├── data_posting.py             # Event posting orchestrator
│   │   ├── update_db.py                # Database status updates
│   │   └── main_resp.py
│   └── doattend/
│       ├── app.py                      # Selenium browser automation
│       ├── doattend.py                 # DoAttend data processing
│       └── main_resp.py
├── .env.example                        # Environment variable template
├── .gitignore                          # Git ignore rules
├── Makefile                            # Common development commands
└── README.md                           # Project documentation
```

## License

MIT License
