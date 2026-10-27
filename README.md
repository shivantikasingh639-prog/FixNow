# 🔧 FixNow — Smart Repair & Service Booking Platform

FixNow is a web-based repair and service booking platform designed to help customers find technicians and book repair services conveniently.

## 📌 Project Overview

Finding a reliable technician for home or vehicle repairs can be difficult and time-consuming. FixNow aims to simplify this process by providing a platform where users can explore services, view technician profiles, book appointments, and track service progress.

## ✨ Features

* **User Authentication:** Login and signup pages.
* **Service Selection:** Explore available repair services.
* **Technician Profiles:** View technician information.
* **Service Booking:** Submit service booking details.
* **Booking Confirmation:** View confirmation after booking.
* **Technician Tracking:** Tracking interface for service progress.
* **Emergency Assistance:** Dedicated emergency service booking page.
* **Repair Datasets:** CSV datasets for services, technicians, reviews, and repair information.

## 🛠️ Technologies Used

* Python
* Flask
* HTML5
* CSS3
* SQLite
* Pandas
* CSV datasets

## 📂 Project Structure

```text
FixNow/
├── app.py
├── .gitignore
├── data/
│   ├── services.csv
│   ├── technicians.csv
│   ├── reviews_dataset.csv
│   ├── customer_support_tickets.csv
│   └── analyze_repair_data.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
└── templates/
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── dashboard.html
    ├── technicians.html
    ├── profile.html
    ├── booking.html
    ├── confirmation.html
    ├── tracking.html
    └── emergency_booking.html
```

## 🚀 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/shivantikasingh639-prog/FixNow.git
cd FixNow
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment on Windows

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

Install Flask and Pandas:

```bash
pip install Flask pandas
```

If the project uses additional Python packages, install those too.

### 5. Run the Application

```bash
python app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

## 📊 Datasets

The `data/` directory contains repair-related datasets, including service categories, technician information, customer reviews, and support tickets. These datasets can support data analysis and future improvements.

## 🎯 Project Objective

The objective of FixNow is to make repair-service discovery and booking easier through a simple web interface connecting customers with technicians.

## 🔮 Future Enhancements

* Live GPS-based technician tracking.
* Real-time booking status updates.
* Online payment integration.
* Technician availability management.
* Customer ratings and feedback.
* Improved data analytics.

## 👥 Project Team

* **Shivangi Pandey** — Team Leader
* **Shivantika Singh** — Team Member

## 📄 License

This project is developed for educational purposes.
