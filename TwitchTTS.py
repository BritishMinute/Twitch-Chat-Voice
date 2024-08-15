import socket
import logging
import pyttsx3
import re
import os
import threading
import queue
import time
import wave
import pyaudio

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Twitch configuration
TWITCH_SERVER = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667
TWITCH_CHANNEL = 'your channel here'  # Channel to join, must contain a hashtag ((hashtag)BritishMinute)

# Path to the access token file
TOKEN_FILE_PATH = r'your file path\twitch_access_token.txt'
WAV_DIR = 'wav_files'  # Directory to save WAV files

# Ensure WAV directory exists
os.makedirs(WAV_DIR, exist_ok=True)

# Initialize the TTS engine
engine = pyttsx3.init()

# Create a queue for messages to be spoken
message_queue = queue.Queue()

# Load the access token from file
def load_access_token():
    try:
        with open(TOKEN_FILE_PATH, 'r') as file:
            token = file.read().strip()
            logger.debug(f'Loaded access token: {token}')

            # Ensure token starts with "oauth:"
            if not token.startswith('oauth:'):
                token = f'oauth:{token}'
                logger.debug(f'Formatted token as: {token}')
                
            return token
    except FileNotFoundError:
        logger.error(f'Token file not found at {TOKEN_FILE_PATH}')
        return None

# Connect to Twitch IRC server
def connect_to_twitch():
    token = load_access_token()
    if not token:
        logger.error('No token available. Exiting.')
        return None

    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TWITCH_SERVER, TWITCH_PORT))

        # Send authentication commands
        sock.sendall(f'NICK justinfan123\r\n'.encode('utf-8'))
        sock.sendall(f'PASS {token}\r\n'.encode('utf-8'))
        sock.sendall(f'JOIN {TWITCH_CHANNEL}\r\n'.encode('utf-8'))

        return sock
    except Exception as e:
        logger.error(f'Failed to connect to Twitch IRC: {e}')
        return None

# Function to save text as WAV file using pyttsx3
def save_text_as_wav(text, filename):
    try:
        temp_file = os.path.join(WAV_DIR, filename)
        # Save speech to a WAV file
        engine.save_to_file(text, temp_file)
        engine.runAndWait()
        logger.info(f'Saved message to WAV: {filename}')
    except Exception as e:
        logger.error(f'Error saving text as WAV: {e}')

# Function to play WAV file using pyaudio
def play_wav(filename):
    try:
        filepath = os.path.join(WAV_DIR, filename)
        
        # Open the WAV file
        wf = wave.open(filepath, 'rb')
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open a stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # Read data in chunks
        chunk = 1024
        data = wf.readframes(chunk)
        
        # Play the sound
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        logger.info(f'Played WAV file: {filename}')
    except Exception as e:
        logger.error(f'Error playing WAV file {filename}: {e}')

# Function to delete WAV file after playback
def delete_wav(filename):
    time.sleep(3)  # Wait for 3 seconds before deleting
    try:
        filepath = os.path.join(WAV_DIR, filename)
        os.remove(filepath)
        logger.info(f'Deleted file: {filename}')
    except Exception as e:
        logger.error(f'Error deleting WAV file {filename}: {e}')

# Worker thread function to process messages from the queue
def message_worker():
    while True:
        text = message_queue.get()
        if text is None:  # Sentinel value to exit the loop
            break
        
        filename = f'message_{int(time.time())}.wav'
        save_text_as_wav(text, filename)
        
        # Play the WAV file in a separate thread
        threading.Thread(target=play_wav, args=(filename,), daemon=True).start()
        
        # Start a thread to delete the WAV file after 3 seconds
        threading.Thread(target=delete_wav, args=(filename,), daemon=True).start()
        
        message_queue.task_done()

# Process incoming messages
def process_messages(sock):
    while True:
        try:
            response = sock.recv(2048).decode('utf-8')
            if response:
                logger.debug(f'Received response: {response.strip()}')

                if 'PRIVMSG' in response:
                    # Extract message
                    message = re.search(r'PRIVMSG #\w+ :(.+)', response)
                    if message:
                        text = message.group(1)
                        logger.info(f'Received message: {text}')
                        
                        # Put message in queue for speaking
                        message_queue.put(text)

                elif 'PING' in response:
                    # Respond to PING from Twitch server
                    sock.sendall('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        except Exception as e:
            logger.error(f'Error receiving data: {e}')

if __name__ == '__main__':
    # Start the worker thread
    worker_thread = threading.Thread(target=message_worker, daemon=True)
    worker_thread.start()

    sock = connect_to_twitch()
    if sock:
        logger.info('Joined channel: ' + TWITCH_CHANNEL)
        try:
            process_messages(sock)
        except KeyboardInterrupt:
            logger.info('Shutting down...')
        finally:
            # Ensure the worker thread exits
            message_queue.put(None)
            worker_thread.join()
