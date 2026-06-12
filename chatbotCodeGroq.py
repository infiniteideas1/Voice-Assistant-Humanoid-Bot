# GOOGLE TEXT 2 SPEECH
import fitz  # PyMuPDF
import openai
import re
import speech_recognition as sr
from gtts import gTTS
import os
from groq import Groq

# GroqAI configuration
model = "gemma2-9b-it"

# Load environment variables from .env file if dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it or add it to a .env file.")

client = Groq(api_key=api_key)
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
   
    text = ""
    # Iterate through each page and extract text
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

# Improved GroqAI query function
def query_groqai(question, context):
    system_message = (
        "You are Nova, a friendly humanoid robot explorer and storyteller. "
        "You speak with excitement about science, history, and adventure. "
        f"The user has asked: {question}\n"
        f"Here's some relevant context: {context}\n"
        "If the context doesn't contain relevant information, "
        "please provide a creative and helpful answer based on the themes of the story or general knowledge."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
    )    
    return response.choices[0].message.content.strip()


def find_context(question, pdf_text):
    # Use a simple approach to find relevant context based on the question
    context = ""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', pdf_text)
    keywords = question.lower().split()

    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            context += sentence + " "
   
    return context.strip() if context else pdf_text[:1000]  # Default to first 1000 characters if no specific context found

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg123 -q response.mp3")

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return ""

def main():
    # PDF file path (default to local folder for portability)
    pdf_file = "Nova_Chronicles.pdf"

    # Check if the PDF file exists in the directory
    if not os.path.exists(pdf_file):
        raise FileNotFoundError(
            f"'{pdf_file}' not found. Please ensure it exists in the same directory as this script, "
            f"or update the 'pdf_file' variable in chatbotCodeGroq.py."
        )

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_file)
   
    while True:
        print("Say 'hello' to start...")
        wake_word = listen()
        if wake_word == "hello":
            speak("Hello! How can I help you?")
            print("Ask me anything about the content of the PDF (say 'quit' to exit).")
           
            while True:
                print("Listening for your question...")
                question = listen()
                print(question)
               
                if question == 'quit':
                    speak("Goodbye!")
                    print("Exiting...")
                    return
               
                if question:
                    # Find relevant context based on the question
                    context = find_context(question, pdf_text)
               
                    if context:
                        # Query OpenAI with the question and relevant context
                        answer = query_groqai(question, context)
                        speak(answer)
                        print("Answer:", answer)
                    else:
                        speak("Sorry, I couldn't find relevant information in the PDF for that question.")
                        print("Sorry, I couldn't find relevant information in the PDF for that question.")
                else:
                    speak("I didn't catch that. Could you please repeat?")
                    print("I didn't catch that. Could you please repeat?")

if __name__ == "__main__":
    main()
