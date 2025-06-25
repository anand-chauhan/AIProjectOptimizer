# 🧠 MoodSentry: Emotion-Driven AI Productivity

MoodSentry is an intelligent FastAPI-based system that detects employee emotions and recommends personalized tasks to enhance productivity and well-being.

## 🚀 Features

- 😃 Mood detection from **text, voice, and facial input**
- 🎯 Emotion-aware **task assignment**
- 📊 Weekly mood analytics for HR and Owners
- 🕵️ Admin/audit log viewing
- 📢 HR gets alerts when stress is detected
- 🧠 Powered by BERT + OpenCV + SpeechRecognition

## 🧱 Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Database:** PostgreSQL via SQLAlchemy
- **NLP:** Huggingface Transformers
- **Speech:** SpeechRecognition
- **Vision:** OpenCV
- **Templating:** Jinja2 + HTML + CSS

## 🖼️ Preview

![screencapture-127-0-0-1-8000-2025-04-23-18_47_07](https://github.com/user-attachments/assets/c37b74d1-b04b-4389-a04b-0b82c705342c)

![screencapture-127-0-0-1-8000-register-2025-04-23-18_50_07](https://github.com/user-attachments/assets/0e31a496-7c1a-45b1-a5b7-69d55192832d)

![screencapture-127-0-0-1-8000-login-2025-04-23-18_50_20](https://github.com/user-attachments/assets/5511624c-15a2-4c8d-8fcf-f3da79fce765)

- Employ Dashboard
  
![screencapture-127-0-0-1-8000-dashboard-2025-04-23-18_55_06](https://github.com/user-attachments/assets/7c00e19d-792d-4987-86d4-8e45ef9e2770)

![screencapture-127-0-0-1-8000-mood-2025-04-23-18_57_04](https://github.com/user-attachments/assets/febe1c0e-254d-4aa5-8dcb-b3361ed68d32)

![screencapture-127-0-0-1-8000-mood-voice-2025-04-23-18_58_24](https://github.com/user-attachments/assets/d8a25d49-f75f-4465-b4c3-c3a588060dd4)

![screencapture-127-0-0-1-8000-mood-facial-2025-04-23-18_58_52](https://github.com/user-attachments/assets/9d239eca-13c5-4555-a113-649b0a0feaff)

![screencapture-127-0-0-1-8000-tasks-2025-04-23-19_02_28](https://github.com/user-attachments/assets/b6396762-2301-4ce6-928e-556f3d16ab1c)

![screencapture-127-0-0-1-8000-weekly-moods-2025-04-23-19_02_40](https://github.com/user-attachments/assets/46a6c49c-5fbf-43e1-a822-023c89ae56df)


- HR Dashboard

![screencapture-127-0-0-1-8000-dashboard-2025-04-23-18_53_52](https://github.com/user-attachments/assets/7bd95ab4-2bad-4061-9130-fc3a2f9f88e1)

![screencapture-127-0-0-1-8000-hr-filter-2025-04-23-18_54_02](https://github.com/user-attachments/assets/dec0d454-a6b0-4b2e-8e30-d5b3c78596f9)

![screencapture-127-0-0-1-8000-weekly-moods-2025-04-23-18_54_13](https://github.com/user-attachments/assets/1ab580e4-73bb-4370-a190-d09f162a77a8)

![screencapture-127-0-0-1-8000-hr-notifications-2025-04-24-23_12_11](https://github.com/user-attachments/assets/7087fc4c-42e0-409d-9daf-a5b936b6b775)

- Owner Dashboard
  
![screencapture-127-0-0-1-8000-dashboard-2025-04-23-18_51_48](https://github.com/user-attachments/assets/c94367d8-f166-4302-8196-b1f91947bb52)

![screencapture-127-0-0-1-8000-owner-users-2025-04-23-18_51_58](https://github.com/user-attachments/assets/1742842d-60e0-49c1-9344-e11f41129a76)

![screencapture-127-0-0-1-8000-owner-teams-2025-04-23-18_52_07](https://github.com/user-attachments/assets/c70d24e0-cdf7-4b53-ba4a-71dfae1b5e3b)

![screencapture-127-0-0-1-8000-audit-2025-04-23-18_52_16](https://github.com/user-attachments/assets/9647be85-c46d-4e7d-9825-74e2a049b6cb)

![screencapture-127-0-0-1-8000-weekly-moods-2025-04-23-18_52_23](https://github.com/user-attachments/assets/9f6f377f-f058-47a8-8ad4-230c518f658a)

## 🛠️ Setup Instructions

### 1. Clone the repo

    git clone https://github.com/hitakshi-25/MoodSentry.git
    cd MoodSentry

### 2. Create & activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate

### 3.  Install dependencies
    pip install -r requirements.txt

### 4. PostgreSQL Setup
<!-- Open the psql shell by running the command `psql -U postgres` and then execute the following SQL commands:Inside psql shell -->
    CREATE DATABASE mood_sentry;
    CREATE USER mood_user WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE mood_sentry TO mood_user;

### 5. Apply schema
    psql -U mood_user -d mood_sentry -f schema.sql

### 6. Run the app
    uvicorn main:app --reload
    Visit http://localhost:8000
