RoboMiracle Chatbot
A Flask-based chatbot for RoboMiracle, allowing users to explore robots, book expos, and make inquiries. The frontend is hosted on GitHub Pages, and the backend is deployed on a separate server (e.g., Render).
Project Structure
robomiracle/
├── app.py              # Flask backend (API)
├── index.html          # Static frontend
├── static/
│   └── styles.css      # CSS styling
├── .gitignore          # Git ignore file
├── README.md           # This file
├── requirements.txt    # Backend dependencies

Features

Browse robots (Humanoid, Quadruped, Toy) with details and images.
Place orders, book expos, or submit inquiries via forms.
Cancel form submissions with updated chat messages.
Send confirmation emails to customers and notifications to the team (robomiracle87@gmail.com).
Supports up to 250 submissions/day (500 emails) on a free Gmail account.

Setup Instructions
Prerequisites

GitHub account
Render account (or alternative: Heroku, PythonAnywhere)
Python 3.8+
Git installed

1. Host Frontend on GitHub Pages

Create a GitHub Repository:

Create a new repository (e.g., robomiracle).

Push the project files:
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/robomiracle.git
git push -u origin main




Enable GitHub Pages:

Go to repository Settings → Pages.
Set Source to main branch, root directory.
Save. Note the URL (e.g., https://your-username.github.io/robomiracle).


Update Backend URL:

In index.html, replace https://your-backend.onrender.com with your actual backend URL (from step 2).

Commit and push:
git add index.html
git commit -m "Update backend URL"
git push





2. Deploy Backend on Render

Create a Render Account:

Sign up at https://render.com.


Create a New Web Service:

In Render Dashboard, click "New" → "Web Service".
Connect your GitHub repository (robomiracle).
Configure:
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app


Add Environment Variable:
Key: EMAIL_PASSWORD
Value: Your Gmail app password (e.g., vbqv nklq semn tsia)


Deploy the service.


Get Backend URL:

After deployment, note the URL (e.g., https://robomiracle.onrender.com).
Update index.html with this URL (see step 1.3).


Install Gunicorn:

Ensure requirements.txt includes gunicorn:
flask==2.3.3
requests==2.31.0
flask-cors==4.0.0
gunicorn==21.2.0





3. Test the Application

Access Frontend:

Visit https://your-username.github.io/robomiracle.
Verify welcome message and options ("Buy a Robot", "Book an Expo", "Learn More").


Test Chat:

Click "Buy a Robot" → "Humanoid" → "Nila Humanoid Robot".
Expect robot details and suggestions.


Test Form Submission:

Select "Buy this robot", fill form (use a test email).
Submit. Expect:
Confirmation email to your test email.
Team email to robomiracle87@gmail.com.


Test expo booking and inquiry similarly.


Test Cancel:

Open order form, click "Cancel".
Expect form hides, prompt removed, "Show another robot" suggestion.



Troubleshooting

Frontend Not Loading:

Check GitHub Pages URL and ensure index.html is in the root.
Verify static/styles.css path.


Backend Errors:

Check Render logs for errors (Dashboard → Logs).

Test API:
curl -X POST https://your-backend.onrender.com/chat -d "user_input=Buy a Robot"


Ensure EMAIL_PASSWORD is set in Render.



Emails Not Sending:

Verify Gmail app password:
import smtplib
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("robomiracle.1@gmail.com", "vbqv nklq semn tsia")
    print("Login successful")


Regenerate app password if needed.




Security Notes

Store EMAIL_PASSWORD in environment variables, not in app.py.
Monitor robomiracle87@gmail.com for team notifications.
Limit submissions to 250/day (500 emails) to stay within Gmail’s free tier.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/new-feature).
Commit changes (git commit -m "Add new feature").
Push to the branch (git push origin feature/new-feature).
Open a Pull Request.

Contact

Email: support@robomiracle.com
Website: https://robomiracle.com

