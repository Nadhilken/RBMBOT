from flask import Flask, request, render_template, jsonify
import smtplib
from email.mime.text import MIMEText
import uuid
import logging
import requests
import time
import os
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Validate environment variables on startup
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    app.logger.error("Missing EMAIL_ADDRESS or EMAIL_PASSWORD environment variables")
    raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment variables")

# Fallback image URL
FALLBACK_IMAGE_URL = "https://via.placeholder.com/300x300.png?text=Robot+Image"

# Validate image URL with retries
def validate_image_url(url, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.head(url, timeout=10, headers=headers, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '').lower()
            is_image = response.status_code == 200 and 'image' in content_type
            if not is_image:
                app.logger.warning(f"URL {url} returned status {response.status_code} or content-type {content_type}")
            return is_image
        except requests.exceptions.Timeout:
            app.logger.error(f"Attempt {attempt+1}/{max_retries}: Timeout validating image URL {url}")
        except requests.exceptions.ConnectionError:
            app.logger.error(f"Attempt {attempt+1}/{max_retries}: Connection error for image URL {url}")
        except Exception as e:
            app.logger.error(f"Attempt {attempt+1}/{max_retries}: Image validation failed for {url}: {e}")
        if attempt < max_retries - 1:
            time.sleep(delay)
    return False

# Robot catalog
ROBOTS = {
    "Humanoid": {
        "Intelligent Humanoid Robot - Front Office": {
            "description": "Service robot for front office reception, providing welcome, appointment scheduling, and company interaction functions for offices, hotels, and exhibition halls.",
            "specs": {
                "Height": "1.4 meters",
                "AI": "Facial recognition, ID authentication, 2D-code verification",
                "Features": "Voice interaction, autonomous navigation, multi-language support",
                "Connectivity": "Wi-Fi",
                "Battery": "6-hour runtime"
            },
            "price": 470000,
            "original_price": 470000,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/humanoid-medical-robot-nursing-robot-500x500-4.webp",
            "fallback_image_urls": []
        },
        "Nila Humanoid Robot": {
            "description": "Intelligent humanoid robot for event celebrations, welcoming guests, dancing, photography, and engaging with kids and families at ceremonies.",
            "specs": {
                "Height": "1.5 meters",
                "AI": "Voice interaction, gesture recognition",
                "Features": "Dancing, instant photography, autonomous movement",
                "Control": "Voice-activated, mobile app",
                "Battery": "8-hour runtime"
            },
            "price": 330000,
            "original_price": 330000,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/DSC_5317__1_-removebg-preview-e1717401701793.png",
            "fallback_image_urls": []
        },
        "Mobile Reception Robot": {
            "description": "Humanoid robot for customer service in hotels, offices, and showrooms, offering autonomous navigation and interactive voice responses.",
            "specs": {
                "Height": "1.3 meters",
                "AI": "Voice interaction, facial recognition",
                "Features": "Autonomous navigation, touchscreen interface, multi-language support",
                "Connectivity": "Wi-Fi",
                "Battery": "7-hour runtime"
            },
            "price": 364000,
            "original_price": 364000,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/05/Mobile-reception-robot.jpg",
            "fallback_image_urls": []
        },
        "Robomiracle Dinebot": {
            "description": "Service delivery robot for corporate and industrial settings, ideal for restaurants and offices.",
            "specs": {
                "Dimensions": "1.2m x 0.5m x 0.5m",
                "Payload": "Up to 10kg",
                "Navigation": "Autonomous with obstacle avoidance",
                "Connectivity": "Wi-Fi",
                "Battery": "6-hour runtime"
            },
            "price": 460000,
            "original_price": 460000,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/Rbm_foodrover-768x768.png",
            "fallback_image_urls": []
        }
    },
    "Quadruped": {
        "Unitree Go2 EDU": {
            "description": "Advanced quadruped robot for STEM education and research, with remote controller and standard battery.",
            "specs": {
                "Dimensions": "70cm x 31cm x 40cm",
                "Weight": "15kg",
                "Speed": "Up to 3.7m/s",
                "Features": "4D LiDAR, HD camera, autonomous navigation",
                "Battery": "8000mAh, 1-2 hour runtime"
            },
            "price": 1160000,
            "original_price": 1250000,
            "discount": "7.2%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/10/unitree-go2-voice-ai-large-model-machine-dog-go2-500x500-1.webp",
            "fallback_image_urls": []
        },
        "Unitree Go2 Pro": {
            "description": "Multi-purpose quadruped robot with enhanced AI and voice control, ideal for research and home use.",
            "specs": {
                "Dimensions": "70cm x 31cm x 40cm",
                "Weight": "15kg",
                "Speed": "Up to 3.5m/s",
                "Features": "4D LiDAR, voice command, 4G module (EU only)",
                "Battery": "8000mAh, 1-2 hour runtime"
            },
            "price": 398900,
            "original_price": 450000,
            "discount": "11.36%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/10/Screenshot-2024-08-28-181722.webp",
            "fallback_image_urls": []
        },
        "Unitree Go2 Air": {
            "description": "Consumer-grade quadruped robot for daily companionship and entertainment, with remote controller.",
            "specs": {
                "Dimensions": "70cm x 31cm x 40cm",
                "Weight": "15kg",
                "Speed": "Up to 2.5m/s",
                "Features": "4D LiDAR, HD camera, intelligent side-follow",
                "Battery": "8000mAh, 1-2 hour runtime"
            },
            "price": 236500,
            "original_price": 260000,
            "discount": "9.04%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/10/Screenshot-2024-08-28-181830.webp",
            "fallback_image_urls": []
        }
    },
    "Toy": {
        "Robert Dancing Robot": {
            "description": "Smart dancing robot with Bluetooth speaker, ideal for kids with app-controlled movements.",
            "specs": {
                "Height": "30cm",
                "Power": "5W speaker",
                "Connectivity": "Bluetooth 4.2 (10m range)",
                "Features": "Hand/leg movements, LED eye color change, mobile app control",
                "Battery": "3.7V, 2-hour runtime"
            },
            "price": 7999,
            "original_price": 7999,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2023/11/ROBERT0-768x768.jpg",
            "fallback_image_urls": []
        },
        "Plastic Emo AI Robot": {
            "description": "Intelligent toy robot with AI-driven interactions, suitable for kids and educational play.",
            "specs": {
                "Height": "25cm",
                "AI": "Basic conversational learning",
                "Connectivity": "Bluetooth",
                "Features": "Voice interaction, LED expressions",
                "Battery": "4-hour runtime"
            },
            "price": 42500,
            "original_price": 42500,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/655e03876f30ec135c472545-emo-robot-living-ai-desktop-pet-robot.jpg",
            "fallback_image_urls": [
                "https://m.media-amazon.com/images/I/71g2b3yW4xL._AC_SL1500_.jpg"
            ]
        },
        "Loona Premium Robot": {
            "description": "Advanced AI petbot with ChatGPT integration, auto-charging dock, and expressive interactions for kids and families.",
            "specs": {
                "Dimensions": "8.3in x 6.8in x 6.8in",
                "Weight": "1.1kg",
                "AI": "Quad-core CPU, 5 TOPS BPU, ChatGPT integration",
                "Connectivity": "Dual-band Wi fiestas-Fi, Bluetooth 5.0",
                "Features": "Voice/gesture recognition, 720P camera, 3D ToF sensor, Google Blockly programming",
                "Battery": "1350mAh, auto-charging dock"
            },
            "price": 48000,
            "original_price": 48000,
            "discount": "0%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/download.avif",
            "fallback_image_urls": []
        },
        "Loona Go Robot": {
            "description": "Playful AI petbot for kids, offering interactive games and STEM learning with voice and gesture recognition.",
            "specs": {
                "Dimensions": "8.3in x 6.8in x 6.8in",
                "Weight": "1.1kg",
                "AI": "Quad-core CPU, 5 TOPS BPU",
                "Connectivity": "Dual-band Wi-Fi, Bluetooth 5.0",
                "Features": "Voice/gesture recognition, 720P camera, 3D ToF sensor, Google Blockly programming",
                "Battery": "1350mAh, USB Type-C charging"
            },
            "price": 45000,
            "original_price": 48000,
            "discount": "6.25%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/61TMNWWQYkL._AC_UF10001000_QL80_.jpg",
            "fallback_image_urls": []
        },
        "Vector 2.0 AI Robot": {
            "description": "Smart AI companion robot with voice recognition and home monitoring, ideal for kids and tech enthusiasts.",
            "specs": {
                "Dimensions": "10cm x 6cm x 6cm",
                "AI": "Voice-activated assistant",
                "Connectivity": "Wi-Fi, Bluetooth",
                "Features": "HD camera, voice commands, remote monitoring",
                "Battery": "3-hour runtime"
            },
            "price": 35000,
            "original_price": 40000,
            "discount": "12.5%",
            "image_url": "https://robomiracle.com/wp-content/uploads/2024/06/63ec97a3da947a5fda5c5183-vector-2-0-ai-robot-companion-smart.jpg",
            "fallback_image_urls": [
                "https://www.robotshop.com/cdn/shop/products/vector-2-0-ai-robot-companion-1.jpg"
            ]
        }
    }
}

# Validate image URLs on startup
for category in ROBOTS:
    for robot_name, robot in ROBOTS[category].items():
        if not validate_image_url(robot["image_url"]):
            app.logger.warning(f"Invalid image URL for {robot_name}: {robot['image_url']}. Checking fallbacks.")
            fallback_used = False
            for fallback_url in robot.get("fallback_image_urls", []):
                if validate_image_url(fallback_url):
                    robot["image_url"] = fallback_url
                    app.logger.info(f"Using fallback URL {fallback_url} for {robot_name}")
                    fallback_used = True
                    break
            if not fallback_used:
                robot["image_url"] = FALLBACK_IMAGE_URL
                app.logger.warning(f"No valid fallback for {robot_name}. Using default fallback: {FALLBACK_IMAGE_URL}")

# Welcome templates
WELCOME_TEMPLATES = {
    "buy": "Welcome to RoboMiracle! Ready to explore our cutting-edge robots? Choose a type: Humanoid, Quadruped, or Toy!",
    "expo": "Hi there! Excited to join a RoboMiracle expo? I’ll help you book a slot and showcase our AI-powered robots!",
    "inquiry": "Hello! Curious about robotics, AI, or STEM education? I’m here to answer your questions and show you what RoboMiracle has in store!"
}

# Suggestions for alternate robots (maps each robot to another in the same category)
SUGGESTIONS = {
    "Humanoid": {
        "Intelligent Humanoid Robot - Front Office": "Nila Humanoid Robot",
        "Nila Humanoid Robot": "Mobile Reception Robot",
        "Mobile Reception Robot": "Robomiracle Dinebot",
        "Robomiracle Dinebot": "Intelligent Humanoid Robot - Front Office"
    },
    "Quadruped": {
        "Unitree Go2 EDU": "Unitree Go2 Pro",
        "Unitree Go2 Pro": "Unitree Go2 Air",
        "Unitree Go2 Air": "Unitree Go2 EDU"
    },
    "Toy": {
        "Robert Dancing Robot": "Plastic Emo AI Robot",
        "Plastic Emo AI Robot": "Loona Premium Robot",
        "Loona Premium Robot": "Loona Go Robot",
        "Loona Go Robot": "Vector 2.0 AI Robot",
        "Vector 2.0 AI Robot": "Robert Dancing Robot"
    }
}

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable SMTP debug output
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        app.logger.info(f"Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f"SMTP Authentication Error: Invalid email or password. Details: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        app.logger.error(f"SMTP Connect Error: Unable to connect to {SMTP_SERVER}:{SMTP_PORT}. Details: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        app.logger.error(f"SMTP Recipients Refused: Invalid recipient {to_email}. Details: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        app.logger.error(f"SMTP Server Disconnected: Connection lost. Details: {e}")
        return False
    except Exception as e:
        app.logger.error(f"Unexpected error sending email to {to_email}: {e}")
        return False

@app.route("/")
def index():
    return render_template("index.html", welcome_message="Welcome to RoboMiracle! How can I assist you today?", options=["Buy a Robot", "Book an Expo", "Learn More"])

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.form.get("user_input", "").strip()
        intent = request.form.get("intent", "inquiry")
        robot_type = request.form.get("robot_type", "")
        robot_name = request.form.get("robot_name", "")
        app.logger.debug(f"Received: user_input={user_input}, intent={intent}, robot_type={robot_type}, robot_name={robot_name}")

        if not user_input:
            raise ValueError("Empty user input")

        response = {"message": "", "suggestions": [], "robot_details": None}

        # Handle intent transitions (lowercase for matching)
        user_input_lower = user_input.lower()
        if user_input_lower in ["buy a robot", "book an expo", "learn more"]:
            intent = "buy" if "buy" in user_input_lower else "expo" if "expo" in user_input_lower else "inquiry"
            robot_type = ""
            robot_name = ""

        # Set welcome message for new intent
        if intent in WELCOME_TEMPLATES and not robot_type and not robot_name:
            response["message"] = WELCOME_TEMPLATES[intent]

        # Handle user input
        if intent == "buy":
            if not robot_type:
                response["message"] = "Please select a robot type: Humanoid, Quadruped, or Toy."
                response["suggestions"] = ["Humanoid", "Quadruped", "Toy"]
            elif "buy this robot" in user_input_lower or "order" in user_input_lower:
                if robot_type in ROBOTS and robot_name in ROBOTS[robot_type]:
                    response["message"] = "Please provide your name, email, and contact number to place your order."
                    response["suggestions"] = ["Submit order"]
                else:
                    response["message"] = "No robot selected. Please choose a robot first."
                    response["suggestions"] = [name for name in ROBOTS.get(robot_type, {}).keys()]
            elif user_input_lower.startswith("show another robot"):
                # Extract the alternate robot name (preserve case)
                alternate_robot = user_input.split("Show another robot: ")[-1].strip()
                if robot_type in ROBOTS and alternate_robot in ROBOTS[robot_type]:
                    robot = ROBOTS[robot_type][alternate_robot]
                    specs = "\n".join([f"{key}: {value}" for key, value in robot["specs"].items()])
                    response["message"] = f"Details for {alternate_robot}:\nDescription: {robot['description']}\nPrice: ₹{robot['price']}\nOriginal Price: ₹{robot['original_price']}\nDiscount: {robot['discount']}\nSpecifications:\n{specs}"
                    response["robot_details"] = {
                        "name": alternate_robot,
                        "image_url": robot["image_url"],
                        "fallback_image_url": FALLBACK_IMAGE_URL,
                        "fallback_image_urls": robot.get("fallback_image_urls", []),
                        "price": robot["price"]
                    }
                    new_alternate = SUGGESTIONS.get(robot_type, {}).get(alternate_robot, "")
                    response["suggestions"] = ["Buy this robot", f"Show another robot: {new_alternate}"]
                else:
                    response["message"] = "Sorry, that robot is not available. Please select another."
                    response["suggestions"] = [name for name in ROBOTS.get(robot_type, {}).keys()]
            elif robot_type in ROBOTS and not robot_name:
                response["message"] = f"Available {robot_type} robots:\n" + "\n".join([f"• {name}: ₹{info['price']}" for name, info in ROBOTS[robot_type].items()])
                response["suggestions"] = [name for name in ROBOTS[robot_type].keys()]
            elif robot_type in ROBOTS and robot_name in ROBOTS[robot_type]:
                robot = ROBOTS[robot_type][robot_name]
                specs = "\n".join([f"{key}: {value}" for key, value in robot["specs"].items()])
                response["message"] = f"Details for {robot_name}:\nDescription: {robot['description']}\nPrice: ₹{robot['price']}\nOriginal Price: ₹{robot['original_price']}\nDiscount: {robot['discount']}\nSpecifications:\n{specs}"
                response["robot_details"] = {
                    "name": robot_name,
                    "image_url": robot["image_url"],
                    "fallback_image_url": FALLBACK_IMAGE_URL,
                    "fallback_image_urls": robot.get("fallback_image_urls", []),
                    "price": robot["price"]
                }
                alternate_robot = SUGGESTIONS.get(robot_type, {}).get(robot_name, "")
                response["suggestions"] = ["Buy this robot", f"Show another robot: {alternate_robot}"]
            else:
                response["message"] = f"Sorry, '{robot_name}' not found in {robot_type}. Please select a valid robot."
                response["suggestions"] = [name for name in ROBOTS.get(robot_type, {}).keys()]
        elif intent == "expo" or "expo" in user_input_lower:
            response["message"] = "Please provide your name, email, phone number, and preferred expo date (e.g., YYYY-MM-DD) to book a slot."
            response["suggestions"] = ["Submit expo booking"]
        elif "rent" in user_input_lower or "demo" in user_input_lower:
            response["message"] = "Interested in renting or demoing a robot? Please provide your name, email, and phone number for more details."
            response["suggestions"] = ["Submit inquiry"]
        else:
            response["message"] = (
                "About RoboMiracle:\n"
                "RoboMiracle is an education-oriented company dedicated to advancing STEM education and robotics innovation. "
                "We provide hands-on training, webinars, and internships focused on robotics, AI, 3D printing, and drones. "
                "Our humanoid robots and automation solutions serve industries like education, healthcare, service, and manufacturing.\n\n"
                "Services:\n"
                "• STEM Education: Platforms for students to learn and innovate through practical, hands-on experiences.\n"
                "• Robotics Development: Advanced humanoid robots with AI, computer vision, and autonomous navigation.\n"
                "• Training Programs: Specialized courses to equip students and professionals with automation and AI skills.\n"
                "• Industry Solutions: Automation for healthcare, service, and manufacturing sectors.\n\n"
                "Contact Us:\n"
                "• Address: No. 4-A, MKG Layout, Near Govt ITI, GN Mills Post, Coimbatore, Tamil Nadu, India, 641029\n"
                "• Phone: +916380473177, +917907108559\n"
                "• Email: support@robomiracle.com, sales@robomiracle.com, robomiracle.education@gmail.com\n\n"
                "Visit us at: https://robomiracle.com/"
            )
            response["suggestions"] = ["Buy a Robot", "Book an Expo"]

        app.logger.debug(f"Response: {response}")
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error in /chat: {e}")
        return jsonify({"message": "Sorry, something went wrong. Please try again.", "suggestions": []})

@app.route("/submit_order", methods=["POST"])
def submit_order():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        robot_name = request.form.get("robot_name")
        robot_type = request.form.get("robot_type")

        if not all([name, email, phone, robot_name, robot_type]):
            return jsonify({"message": "Please provide all required details."})

        if robot_type not in ROBOTS or robot_name not in ROBOTS[robot_type]:
            return jsonify({"message": "Invalid robot selected. Please try again."})

        robot = ROBOTS[robot_type][robot_name]
        order_id = str(uuid.uuid4())

        # Customer email
        customer_body = f"Dear {name},\nYour order for {robot_name} is confirmed and our team will contact you in a short time.\nOrder ID: {order_id}"
        if not send_email(email, "Order Confirmation - RoboMiracle", customer_body):
            app.logger.error(f"Failed to send confirmation email to {email}")
            return jsonify({"message": "Failed to send confirmation email. Please contact support at support@robomiracle.com."})

        # Team email
        team_body = f"New Order Received:\nCustomer Details:\nName: {name}\nEmail: {email}\nContact Number: {phone}\n\nRobot Details:\nName: {robot_name}\nPrice: ₹{robot['price']}\nDescription: {robot['description']}\nOrder ID: {order_id}"
        if not send_email("robomiracle87@gmail.com", "New Robot Order - RoboMiracle", team_body):
            app.logger.error(f"Failed to send team notification to robomiracle87@gmail.com")
            return jsonify({"message": "Failed to notify our team. Please contact support at support@robomiracle.com."})

        return jsonify({"message": "Order placed successfully! Check your email for confirmation."})
    except Exception as e:
        app.logger.error(f"Error in /submit_order: {e}")
        return jsonify({"message": "Sorry, something went wrong. Please try again."})

@app.route("/submit_expo", methods=["POST"])
def submit_expo():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        date = request.form.get("date")

        if not all([name, email, phone, date]):
            return jsonify({"message": "Please provide all required details."})

        robomiracle_body = f"New Expo Booking:\nName: {name}\nEmail: {email}\nPhone: {phone}\nPreferred Date: {date}\nBooking ID: {uuid.uuid4()}"
        if not send_email("robomiracle87@gmail.com", "New Expo Booking - RoboMiracle", robomiracle_body):
            app.logger.error(f"Failed to send expo booking notification to robomiracle87@gmail.com")
            return jsonify({"message": "Failed to notify our team. Please contact support at support@robomiracle.com."})

        customer_body = f"Dear {name},\nYour expo booking for {date} is confirmed! We’ll reach out with details.\nBooking ID: {uuid.uuid4()}"
        if not send_email(email, "Expo Booking Confirmation - RoboMiracle", customer_body):
            app.logger.error(f"Failed to send expo confirmation email to {email}")
            return jsonify({"message": "Failed to send confirmation email. Please contact support at support@robomiracle.com."})

        return jsonify({"message": "Expo booking confirmed! Check your email for details.(check spam folder also)"})
    except Exception as e:
        app.logger.error(f"Error in /submit_expo: {e}")
        return jsonify({"message": "Sorry, something went wrong. Please try again."})

@app.route("/submit_inquiry", methods=["POST"])
def submit_inquiry():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        if not all([name, email, phone]):
            return jsonify({"message": "Please provide all required details."})

        robomiracle_body = f"New Inquiry:\nName: {name}\nEmail: {email}\nPhone: {phone}\nInquiry ID: {uuid.uuid4()}"
        if not send_email("robomiracle87@gmail.com", "New Inquiry - RoboMiracle", robomiracle_body):
            app.logger.error(f"Failed to send inquiry notification to robomiracle87@gmail.com")
            return jsonify({"message": "Failed to notify our team. Please contact support at support@robomiracle.com."})

        customer_body = f"Dear {name},\nThank you for your inquiry! We’ll contact you soon with more details.\nInquiry ID: {uuid.uuid4()}"
        if not send_email(email, "Inquiry Confirmation - RoboMiracle", customer_body):
            app.logger.error(f"Failed to send inquiry confirmation email to {email}")
            return jsonify({"message": "Failed to send confirmation email. Please contact support at support@robomiracle.com."})

        return jsonify({"message": "Inquiry submitted successfully! Check your email for confirmation."})
    except Exception as e:
        app.logger.error(f"Error in /submit_inquiry: {e}")
        return jsonify({"message": "Sorry, something went wrong. Please try again."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)