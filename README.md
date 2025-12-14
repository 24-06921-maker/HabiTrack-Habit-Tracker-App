# HabiTrack: Habit Tracker App

## Introduction

**HabiTrack** is a comprehensive GUI-based habit tracking applicationa built with Python. This project encourage users to create, monitor, and maintain positive daily habits through an user-friendly interface and powerful visual charts. Whether you're building a fitness routine, learning to code consistently, reading daily, or developing any other habit, HabiTrack helps you stay accountable and motivated by providing real-time progress insights and streak tracking.

## Overview

HabiTrack combines a user-friendly desktop interface with robust data tracking capabilities to deliver a complete habit management solution. The application allows you to:

- **Create and manage** custom daily habits with ease
- **Log daily progress** for each habit with a simple checkbox interface
- **Visualize performance** through interactive charts and monthly calendars
- **Track streaks** to see your consistency and motivation at a glance
- **Analyze statistics** including completion rates, best streaks, and monthly progress
- **Navigate history** effortlessly with month-to-month calendar views

## Key Features

✅ **Simple Habit Management** - Add, edit, and delete habits with an intuitive UI  
✅ **Daily Logging** - Quick checkbox interface to mark habits as completed  
✅ **Visual Dashboard** - Beautiful calendar view with color-coded completion rates  
✅ **Advanced Analytics** - Pie charts, bar graphs, and detailed monthly statistics  
✅ **Streak Tracking** - Monitor your consecutive days of habit completion  
✅ **Data Persistence** - All habits and logs stored in SQLite database and CSV backup  
✅ **Progress Charts** - Real-time visualizations showing completion percentages and trends  

## Project Structure

```
Habit Track/
├── LoginUI/                          # Login and navigation interface
│   └── New folder/build/
│       ├── Login.py                  # Main login screen
│       └── assets/                   # UI assets
│
├── MeynYuay/                         # Main application folder
│   ├── MainUI.py                     # Habit management interface
│   ├── ProgressUI.py                 # Progress tracking and analytics
│   ├── Database/
│   │   ├── habits.csv                # Habit data backup
│   │   └── habits_pandas.db          # SQLite database
│   └── ButtonUI/                     # UI button images
│
├── Habits_/                          # Legacy habit management module
│   ├── Habits.py                     # Habit creation interface
│   └── Database/
│
└── README.md                         
```

## Technology Stack

- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (built-in with Python)
- **Database**: SQLite3
- **Data Processing**: Pandas
- **Visualization**: Matplotlib
- **File Format**: CSV

## Getting Started

### Installation

1. **Clone or download** the project to your local machine
2. **Install dependencies**:
   ```bash
   pip install pandas matplotlib
   ```
   *Note: tkinter and sqlite3 come built-in with Python*

3. **Navigate to the project folder**:
   ```bash
   cd "Habit Track"
   ```

### Quick Start

1. **Launch the application**:
   ```bash
   python LoginUI/New\ folder/build/Login.py
   ```

2. **From the login screen, choose**:
   - **Start** - Manage and log your daily habits
   - **Habits** - Create and configure new habits
   - **Progress** - View visual charts and monthly progress

3. **Start tracking!** Add habits, log daily completion, and watch your progress grow

## How It Works

1. **Add Habits** - Enter the name of a habit you want to track
2. **Log Daily** - Check off completed habits each day using the checkbox interface
3. **Record Progress** - Save your daily logs to the database
4. **View Analytics** - Open the Progress UI to see charts, streaks, and completion rates
5. **Navigate History** - Browse previous months to track long-term progress

## Data Storage

- **SQLite Database** (`habits_pandas.db`) - Stores all habit logs with timestamps
- **CSV Backup** (`habits.csv`) - Maintains a text-based backup of habit data
- **Auto-persistence** - All data is automatically saved when you record progress

---

*For detailed usage instructions, see [USAGE_GUIDE.md](USAGE_GUIDE.md)*
