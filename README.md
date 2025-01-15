# POTHOLE-DETECTION![potweb app upload](https://git
![sp1](https://github.com/user-attachments/assets/f6bd39bb-5588-4725-a15a-dc2c15054990)
![spot3](https://github.com/user-attachments/assets/83f1b4b4-c058-4725-aa2d-1ade637f75fb)

Pothole Detection Backend - Capstone Project
This repository covers the Core Backend Segment of the Pothole Detection Capstone Project, part of my BSc in Civil Engineering at Multimedia University of Kenya.

Introduction
Potholes significantly impact road safety and vehicle maintenance. Globally, authorities struggle to monitor and repair road damage due to limited budgets, lack of efficient monitoring systems, and unpredictable weather conditions.

This project introduces a real-time pothole detection system to help identify, report, and manage potholes effectively. It uses a YOLOv8 object detection model, integrated with cloud-based services, to geocode and assess pothole severity. Users can access the system via a mobile app or a web application, and municipal authorities receive dynamic reports to manage repairs efficiently.

Key Objectives:
Provide real-time pothole detection using computer vision.
Enable citizens to report potholes using images or videos.
Notify municipal authorities of severe road conditions.
Visualize pothole data on a Flask-based web dashboard.
Motivation
Road accidents caused by potholes claim lives and damage vehicles, costing billions annually. For instance:

According to AAA, U.S. drivers spend $3 billion yearly on pothole-related vehicle repairs.
In 2017, potholes claimed nearly 10 lives daily, as reported by The Guardian.
This project aims to create a scalable solution to mitigate such issues through technology-driven infrastructure monitoring.

Features
Core Functionalities:
Object Detection: Pothole identification using the YOLOv8 model.
Geocoding: Extract GPS coordinates for detected potholes.
Driver Alerts: Notify users of nearby potholes.
Dynamic Reports: Automated generation of severity-based reports for municipal authorities.
Data Visualization: Real-time display of pothole data on a Flask web dashboard.
Backend Highlights:
Cloud Integration: Firebase for storing reports, images, and user data.
REST API: Built with Flask for seamless communication between components.
Database Design: Schema for users, reports, comments, and authority roles.
Dockerized Deployment: Easy replication and scalability.
YOLOv8 Training Pipeline: Trained on a curated dataset of 2000+ pothole images.
Technology Stack
Languages & Frameworks:
Python: Core backend logic and machine learning integration.
Flask: REST API development.
MySQL: Database management.
Tools & Libraries:
Ultralytics YOLOv8: Pothole detection model.
OpenCV: Image preprocessing and video slicing.
Firebase: Cloud-based data storage and user authentication.
Docker: Application containerization.
Postman: API testing.
Infrastructure:
AWS EC2 Instance: Model training and deployment.
Roboflow: Dataset preparation and annotation.
System Architecture

The architecture comprises three tiers:

Data Collection: User-submitted media files (images/videos).
Processing Layer: YOLOv8 model for object detection, Flask API, and database operations.
Visualization: Real-time insights on mobile and web applications.
API Endpoints
Endpoint	Description	Method	Required Parameters
/api/detect/image	Detect potholes in an image.	POST	image_url
/api/reports/create	Submit a new pothole report.	POST	location, severity, image_url
/api/reports/all	Retrieve all reports.	GET	N/A
/api/reports/comments	Fetch comments for a report.	POST	report_id
/api/profile/authority/update	Update authority details.	POST	authority_id, email, name
Setup and Deployment
Follow these steps to set up and run the backend:

1. Clone the Repository
bash
Copy code
git clone https://github.com/username/pothole-detection-backend.git
cd pothole-detection-backend
2. Install Dependencies
bash
Copy code
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file to store sensitive data like database credentials, Firebase keys, and API endpoints.

4. Set Up MySQL Database
Import the provided schema.sql file.
Update database credentials in config.py.
5. Run the Application
bash
Copy code
flask run
6. Dockerized Deployment
Build and run the Docker container:

bash
Copy code
docker build -t pothole-backend .
docker run -p 5000:5000 pothole-backend
Future Enhancements
Pothole width and depth estimation.
Severity scoring using machine learning regression.
Push notifications for severe potholes.
Advanced analytics for municipal authorities.
User reward system for frequent reporting.
Contributing
Contributions are welcome! Feel free to submit issues or pull requests for new features or bug fixes.

License
This project is licensed under the MIT License. See the LICENSE.md file for details.

Developer
Chris Mwenda Nyamu

GitHub: @ Nyamu007: https://github.com/Nyamu007
LinkedIn: https://www.linkedin.com/in/chris-nyamu-b1397622a/
Email: thechrisnyamu@gmail.com

