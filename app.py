from flask import Flask, request, jsonify, render_template, session
import nltk
from googletrans import Translator
from flask_session import Session
import re

nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

stop_words = set(stopwords.words('english'))
translator = Translator()

def clean_input(input_text):
    # Tokenize the text and remove stopwords
    words = word_tokenize(input_text.lower())
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words
def separate_text_and_links(text):
    """
    Separates text and HTML links. Returns a list where each entry is either plain text or an HTML link.
    """
    return re.split(r'(<a .*?>.*?</a>)', text)

def translate_only_text_parts(text_parts, target_language):
    """
    Translates only plain text parts while leaving HTML links unchanged.
    """
    translated_parts = []
    for part in text_parts:
        if part.startswith('<a '):  # If this part is an HTML link, skip translation
            translated_parts.append(part)
        else:
            translated_parts.append(translator.translate(part, dest=target_language).text)
    return ''.join(translated_parts)

def generate_response(words):
    # Define keywords for different responses
    greeting_keywords = ['hi', 'hello', 'greetings', 'sup', 'what\'s up']
    thanks_keywords = ['stop', 'end', 'exit']
    library_keywords = ['library', 'books', 'study', 'reading']
    department_query_keywords = ['department', 'departments', 'major', 'branch', 'study', 'program']
    academic_calendar_keywords = ['academic', 'calendar', 'schedule', 'events']
    college_info_keywords = ['college', 'institute', 'about', 'MGIT', 'information']
    syllabus_keywords = ['syllabus', 'subjects']
    transport_keywords = ['transport', 'transportation', 'bus']
    placement_keywords=['placements graph','placement report','placement','year-wise placement report']
    examination_center=['exam form','exam registration form']
    course_list_keywords = ['course list', 'ug course list', 'pg course list', 'courses', 'list of courses']
    
    
    department_info = {
        'ece': "Electronics and Communication Engineering (ECE) focuses on electronic devices and software interfaces. The fee for the ECE program is 60000 per semester.",
        'cse': "Computer Science and Engineering (CSE) covers programming, algorithm design, and computer systems. The fee for the CSE program is 60000 per semester.",
        'mec': "Mechanical Engineering (MEC) involves the design and manufacture of physical or automated systems. The fee for the MEC program is 60000 per semester.",
        'civil': "Civil Engineering deals with the design, construction, and maintenance of the environment. The fee for the Civil program is 60000 per semester."
    }

    # Links for different semesters in academic calendar
    academic_calendar_links = {
        'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2024/08/I-BTtech-Academic-Calender-2024-25.pdf",
        'II-IV Semester': "https://mgit.ac.in/wp-content/uploads/2024/08/Almanac-for-B.Tech-III-IV-Semester-2024-25.pdf",
        'V-VI Semester': "https://mgit.ac.in/wp-content/uploads/2024/08/Almanac-for-B.Tech-V-VI-Semester-2024-25.pdf",
        'VII-VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/08/Almanac-for-B.Tech-VII-VIII-Semester-2024-25.pdf"
    }
    

   

    # Syllabus links for each department and semester
    syllabus_links = {
        'cse': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2024/04/MR22-CSE-I-II-SEM-SCHEME-AND-SYLLABUS.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2024/07/MR22-CSE-III-IV-SEM-SCHEME-AND-SYLLABUS.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/07/05-CSE-528.pdf",
            
        },
        'eee': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/EEE-MR22-I-and-II-SEM.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/EEE-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VII Semester': "https://mgit.ac.in/wp-content/uploads/2022/11/MR21-III-IV-SEM.pdf",
            
        },
        'it': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2022/12/IT-I-II-Sem-Scheme-and-Syllabus-Arial-14-11-2022.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/IT-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/03/MR21_UG-IT_V-VIII_Sem_Syllabus.pdf",
            
        },
        'csb': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2022/12/CSB-I-II-Sem-Scheme-and-Syllabus-Arial-14-11-2022.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/CSB-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/03/MR21-CSBS-V-to-VIII-Scheme-and-Syllabus.pdf"
        }
    }

    # College information
    college_info = (
        "Mahatma Gandhi Institute of Technology (MGIT) was established by the Chaitanya Bharathi Educational Society (CBES) in 1997. "
        "MGIT has maintained an excellent academic track record and stands among the top engineering colleges in Telangana... "
    )

    # Greet new users or check for greetings
    if 'greeted' not in session:
        session['greeted'] = True
        return "Hello, welcome to our college! How can I assist you today?"
    
    if any(word in words for word in greeting_keywords):
        return "Hello again! How can I assist you further?"
    elif any(word in words for word in thanks_keywords):
        return "You're welcome! Have a good day."
    
    elif any(keyword in ' '.join(words) for keyword in library_keywords):
        return ("In the first floor of B-Block in MGIT, the Library & Information Center has grown by leaps and bounds. The original 400 titles and 1000 volumes have now grown to 53,852 volumes and 12,734 titles – an addition of 2500 volumes per year. It is now managed by seven technical and three non-technical members.")
    elif any(keyword in words for keyword in department_query_keywords):
        return "Which department do you want to enquire about? ECE, CSE, MEC, or Civil?"
    
    elif any(keyword in words for keyword in academic_calendar_keywords):
        links_response = "Here are the academic calendar links for different semesters:<br>"
        for semester, link in academic_calendar_links.items():
            links_response += f'<a href="{link}" target="_blank" aria-label="click here for {semester} calendar">{semester}</a><br>'
        return links_response

    elif any(word in words for word in college_info_keywords):
        return college_info

    elif any(word in words for word in syllabus_keywords):
        # Ask for department selection for syllabus
        session['awaiting_syllabus_department'] = True
        return "Please specify the department for syllabus information. Options are CSE, EEE, IT, or CSB."

    # Provide syllabus links if a department is specified after the syllabus prompt
    if 'awaiting_syllabus_department' in session:
        for dept, links in syllabus_links.items():
            if dept in words:
                session.pop('awaiting_syllabus_department', None)
                syllabus_response = f"Syllabus links for {dept.upper()} department:<br>"
                for semester, link in links.items():
                    syllabus_response += f'<a href="{link}" target="_blank" aria-label="click here for {semester}">{semester}</a><br>'
                return syllabus_response

    if any(keyword in words for keyword in transport_keywords):
        transport_link = "https://mgit.ac.in/wp-content/uploads/2024/08/Application-Form_Student-Transport_AY-2024-25.pdf"
        return f"You can find the transport application form  <a href='{transport_link}' target='_blank' aria-label='click here'>Transport Application Form</a>"

    if any(keyword in ' '.join(words) for keyword in examination_center):
        link='https://mgit.ac.in/wp-content/uploads/2024/07/MGIT-Registration-Form-I-III-V-VII-Sem-July-2024-25-01072024.pdf'
        return f"You can find the Exam registration form  <a href='{link}' target='_blank' aria-label='click here'>Exam Registration Form</a>"
    
    if any(keyword in ' '.join(words) for keyword in course_list_keywords):
        link="https://mgit.ac.in/ug-pg-course-list/"
        return f"You can find the Course list <a href='{link}' target='_blank' aria-label='click here'>Course List</a>"
    
    if any(keyword in words for keyword in placement_keywords):
        link='https://mgit.ac.in/year-wise-placement/'
        return f"You can find the Year wise Placements report <a href='{link}' target='_blank' aria-label='click here'>Year wise Placements report</a> '"

    # Check for specific department information
    for dept_key, dept_info in department_info.items():
        if dept_key in words:
            return dept_info

    # Default response for unrecognized input
    if 'error' not in session:
        session['error'] = True
        return "Sorry, I didn't understand that. Can you please specify your query?"
    
    return "Please specify your query or contact our support for more help."
def translate_text(text, target_language):
    return translator.translate(text, dest=target_language).text
@app.route('/')
def home():
    session.clear()  # Correct method to reset session at new conversation start
    return render_template('index.html')
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message')
        
        # Ensure user_input is provided
        if not user_input:
            return jsonify({'response': 'Error: Message is missing or empty'}), 400

        language = data.get('language', 'en')  # Default to English
        
        # Translate user input to English for processing if needed
        if language != 'en':
            try:
                translated_input = translate_text(user_input, 'en')
                # Check if translation returned None or empty string
                if not translated_input:
                    return jsonify({'response': 'Error: Translation failed.'}), 500
                user_input = translated_input
            except Exception as e:
                return jsonify({'response': f'Error in translating message: {str(e)}'}), 500

        # Process the cleaned input and generate response
        cleaned_words = clean_input(user_input)
        response = generate_response(cleaned_words)

        # Translate the response back to the user's preferred language if necessary
        if language != 'en':
            text_parts = separate_text_and_links(response)
            response = translate_only_text_parts(text_parts, language)

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f'Error processing your message: {str(e)}'}), 500
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
