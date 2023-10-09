import tkinter as tk
import soundcard as sc
import numpy as np
import keyboard
import communicate
import random
import time
import threading
import traceback
import pyaudio

exit_event = threading.Event()  # Event to signal the loop to exit

# Config
SPAWN_AMOUNT = 50  # Number of LEDs to change colors
FADE_DECAY = 10
FPS = 30.0
NUM_LEDS = 50
SPAWN_DELAY  = 0.1

# Audio Config
CHUNK = 1024  # Size of audio chunks to analyze
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
zero = [ 0, 0, 0 ]

# Logic
invFPS = 1.0 / FPS
leds = [[0, 0, 0] for _ in range(NUM_LEDS)]
state = communicate.connect_waiting(baudrate=200000, port='COM5')
time.sleep(2)
timestamp = time.time()
COLOR    = [ 0, 255, 0 ]
last_clicked_button = None  # Declare as a global variable
last_clicked_button_number = None  # Declare as a global variable


p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def map_numpad_key(scan_code):
    numpad_mapping = {
        # Map scan codes to actual numbers
        79: 1,
        80: 2,
        81: 3,
        75: 4,
        76: 5,
        77: 6,
        71: 7,
        72: 8,
        73: 9,
        82: 10,
    }
    
    return numpad_mapping.get(scan_code, None)
def button_click(button_number):
    global last_clicked_button  # Reference the global variable

    def inner():
        global last_clicked_button  # Use nonlocal to modify the global variable
        if last_clicked_button is not None:
            last_clicked_button.configure(bg="lightgray")
        last_clicked_button = buttons[button_number - 1]
        last_clicked_button.configure(bg="green")
        print(f"Button {button_number} clicked")
        global last_clicked_button_number
        last_clicked_button_number=button_number
       

    return inner

def on_num_pad_key(event):
    if event.event_type == keyboard.KEY_DOWN:
        try:
            button_number = int(event.scan_code) - 79
            print('EVENT: ',event.scan_code)
            print(map_numpad_key(event.scan_code))
            
            
            global last_clicked_button_number
            if 1 <= map_numpad_key(event.scan_code) <= 10:
                button_click(map_numpad_key(event.scan_code))()
                last_clicked_button_number=map_numpad_key(event.scan_code)
                print('CLECKKKK',last_clicked_button_number)

        except ValueError:
            print('Error')
            print(ValueError)
            pass

def run_selected_function():
    global last_clicked_button_number
    in_last= None
    while not exit_event.is_set():
        if last_clicked_button is not None:
            # button_number = int(last_clicked_button.cget("text"))
            # # Run specific code based on button_number
            print(f"Running code for Button {last_clicked_button_number}")
        # time.sleep(1)  # Adjust the sleep duration as needed
        try:
            if last_clicked_button_number!=in_last:
                print('not last')
                print(in_last)
                print(last_clicked_button_number)
                for i in range(NUM_LEDS):
                    leds[i] = [0, 0, 0]  # Setting all color components to 0 (black)
                communicate.send_led_state(state, leds, 0)
            
            
           
            # If statement 1
            if last_clicked_button_number == 1:
                for i in range(SPAWN_AMOUNT):
                    leds[random.randint(0, NUM_LEDS - 1)] = [ random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) ]
                timestamp = time.time()

                communicate.send_led_state(state, leds, 0)
                time.sleep(invFPS)

                for l in leds:
                    l[0] = max(0, l[0] - FADE_DECAY)
                    l[1] = max(0, l[1] - FADE_DECAY)
                    l[2] = max(0, l[2] - FADE_DECAY)
                pass

            # If statement 2
            if last_clicked_button_number == 2:
                
                for i in range(NUM_LEDS):
                    leds[i] = [5, 100, 255] 
                communicate.send_led_state(state, leds, 0)
                for i in range(NUM_LEDS):
                    leds[i] = [0, 0, 0]  # Setting all color components to 0 (black) 
                communicate.send_led_state(state, leds, 0)
                time.sleep(0.05)
                pass

            # If statement 3
            if last_clicked_button_number == 3:
                random_color = [random.randint(0, 255), 255, random.randint(0, 255)]
                for i in range(NUM_LEDS):
                    leds[i] = random_color
                    communicate.send_led_state(state, leds, 0)
                    time.sleep(1.0/120)
                    leds[i] = zero
            
                for i in reversed(range(NUM_LEDS)):
                    leds[i] = random_color
                    communicate.send_led_state(state, leds, 0)
                    time.sleep(1.0/120)
                    leds[i] = zero
                    pass

            # If statement 4
            if last_clicked_button_number == 4:
                # //MIC in react
                MIC_FADE_DECAY=10
                # Read audio data
                data = stream.read(CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate the audio intensity (volume)
                audio_intensity = np.abs(audio_data).mean()
                print(audio_intensity)
                audio_intensity=audio_intensity*2
                # Map audio intensity to LED color intensity
                color_intensity = int(audio_intensity / 32767 * 255)
                
                # Set LED colors
                for i in range(SPAWN_AMOUNT):
                    random_led_index = np.random.randint(0, NUM_LEDS)
                    # leds[random_led_index] = [color_intensity, color_intensity, color_intensity]
                    brightness_factor = 1.5  # Increase this factor to make it brighter, decrease for less brightness
                    leds[random_led_index] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]

                
                # Apply fading effect to all LEDs
                for i in range(NUM_LEDS):
                    leds[i][0] = max(0, leds[i][0] - MIC_FADE_DECAY)
                    leds[i][1] = max(0, leds[i][1] - MIC_FADE_DECAY)
                    leds[i][2] = max(0, leds[i][2] - MIC_FADE_DECAY)
                
                communicate.send_led_state(state, leds, 0)
                time.sleep(invFPS)
                pass

            # If statement 5
            if last_clicked_button_number == 5:
                # flash 2
                random_color = [random.randint(0, 255), 255, random.randint(0, 255)]
                for i in range(NUM_LEDS):
                    leds[i] = random_color 
                communicate.send_led_state(state, leds, 0)
                for i in range(NUM_LEDS):
                    leds[i] = [0, 0, 0]  # Setting all color components to 0 (black) 
                communicate.send_led_state(state, leds, 0)
                time.sleep(0.05)
                pass

            # If statement 6
            if last_clicked_button_number == 6:
                # //MIC in react
                MIC_FADE_DECAY=10
                # Read audio data
                data = stream.read(CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate the audio intensity (volume)
                audio_intensity = np.abs(audio_data).mean()
                print(audio_intensity)
                audio_intensity=audio_intensity*2
                # Map audio intensity to LED color intensity
                # color_intensity = int(audio_intensity / 32767 * 255)
                   # flash 2
                
                # Set LED colors
                # for i in range(SPAWN_AMOUNT):
                #     random_led_index = np.random.randint(0, NUM_LEDS)
                #     # leds[random_led_index] = [color_intensity, color_intensity, color_intensity]
                #     brightness_factor = 1.5  # Increase this factor to make it brighter, decrease for less brightness
                #     leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                if audio_intensity>1500:
                    
                    for i in range(NUM_LEDS):
                        random_color = [random.randint(0, 255), 255, random.randint(0, 255)]
                        brightness_factor = 1.0  # Increase this factor to make it brighter, decrease for less brightness
                        # leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                        leds[i] = random_color 
                 
                
                # Apply fading effect to all LEDs
                for i in range(NUM_LEDS):
                    leds[i][0] = max(0, leds[i][0] - MIC_FADE_DECAY)
                    leds[i][1] = max(0, leds[i][1] - MIC_FADE_DECAY)
                    leds[i][2] = max(0, leds[i][2] - MIC_FADE_DECAY)
                
                communicate.send_led_state(state, leds, 0)
                time.sleep(invFPS)
                pass

            # If statement 7
            if last_clicked_button_number == 7:
                # //MIC in react
                MIC_FADE_DECAY=100
                # Read audio data
                data = stream.read(CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate the audio intensity (volume)
                audio_intensity = np.abs(audio_data).mean()
                print(audio_intensity)
                audio_intensity=audio_intensity*2
                # Map audio intensity to LED color intensity
                # color_intensity = int(audio_intensity / 32767 * 255)
                # flash 2
                
                # Set LED colors
                # for i in range(SPAWN_AMOUNT):
                #     random_led_index = np.random.randint(0, NUM_LEDS)
                #     # leds[random_led_index] = [color_intensity, color_intensity, color_intensity]
                #     brightness_factor = 1.5  # Increase this factor to make it brighter, decrease for less brightness
                #     leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                if audio_intensity>6000:
                    
                    for i in range(NUM_LEDS):
                        random_color = [random.randint(0, 255), 255, random.randint(0, 255)]
                        brightness_factor = 1.0  # Increase this factor to make it brighter, decrease for less brightness
                        # leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                        leds[i] = random_color 
                
                    # communicate.send_led_state(state, leds, 0)
                # Apply fading effect to all LEDs
                for i in range(NUM_LEDS):
                    # leds[i] = [0, 0, 0]
                    leds[i][0] = max(0, leds[i][0] - MIC_FADE_DECAY)
                    leds[i][1] = max(0, leds[i][1] - MIC_FADE_DECAY)
                    leds[i][2] = max(0, leds[i][2] - MIC_FADE_DECAY)
                
                communicate.send_led_state(state, leds, 0)
                time.sleep(invFPS)
                pass

            # If statement 8
            if last_clicked_button_number == 8:
                 # //MIC in react
                MIC_FADE_DECAY=128
                # Read audio data
                data = stream.read(CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate the audio intensity (volume)
                audio_intensity = np.abs(audio_data).mean()
                print(audio_intensity)
                audio_intensity=audio_intensity*2
                # Map audio intensity to LED color intensity
                # color_intensity = int(audio_intensity / 32767 * 255)
                # flash 2
                
                # Set LED colors
                # for i in range(SPAWN_AMOUNT):
                #     random_led_index = np.random.randint(0, NUM_LEDS)
                #     # leds[random_led_index] = [color_intensity, color_intensity, color_intensity]
                #     brightness_factor = 1.5  # Increase this factor to make it brighter, decrease for less brightness
                #     leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                if audio_intensity>6000:
                    
                    # random_color = [random.randint(0, 255), 255, random.randint(0, 255)]
                    for i in range(NUM_LEDS):
                        random_color = [0, 0, 255]
                        brightness_factor = 1.0  # Increase this factor to make it brighter, decrease for less brightness
                        # leds[i] = [int(color_intensity * brightness_factor), int(color_intensity * brightness_factor), int(color_intensity * brightness_factor)]
                        leds[i] = random_color 
                
                    # communicate.send_led_state(state, leds, 0)
                # Apply fading effect to all LEDs
                for i in range(NUM_LEDS):
                    # leds[i] = [0, 0, 0]
                    leds[i][0] = max(0, leds[i][0] - MIC_FADE_DECAY)
                    leds[i][1] = max(0, leds[i][1] - MIC_FADE_DECAY)
                    leds[i][2] = max(0, leds[i][2] - MIC_FADE_DECAY)
                
                communicate.send_led_state(state, leds, 0)
                time.sleep(invFPS)
                pass

            # If statement 9
            if last_clicked_button_number == 9:
               
               
                pass

            # If statement 10
            if last_clicked_button_number == 10:
                FADE_DECAY_2 = 100
                try:
                    for i in range(NUM_LEDS):
                        leds[i] = [5, 0, 255] 
                        # Apply fading effect to all LEDs
                    for i in range(NUM_LEDS):
                        leds[i][0] = max(0, leds[i][0] - FADE_DECAY_2)
                        leds[i][1] = max(0, leds[i][1] - FADE_DECAY_2)
                        leds[i][2] = max(0, leds[i][2] - FADE_DECAY_2)
                    
                    communicate.send_led_state(state, leds, 0)
                    for i in range(NUM_LEDS):
                        leds[i] = [0, 0, 0]  # Setting all color components to 0 (black) 
                        # communicate.send_led_state(state, leds, 0)
                    for i in range(NUM_LEDS):
                        leds[i][0] = max(0, leds[i][0] - FADE_DECAY_2)
                        leds[i][1] = max(0, leds[i][1] - FADE_DECAY_2)
                        leds[i][2] = max(0, leds[i][2] - FADE_DECAY_2)
                    
                    communicate.send_led_state(state, leds, 0)
                
                    # time.sleep(1.0/6000000)
                    last_clicked_button.configure(bg="lightgray")
                    last_clicked_button_number=0
                except:
                    print('Error')
        
                    
                pass

        except Exception:
            traceback.print_exc()
            communicate.close(state)
            print('ERORR')
        in_last= last_clicked_button_number
    

root = tk.Tk()
root.title("Light Control Pad - desh")
root.geometry("400x300")
412000002000020000202200002200021010100000001001011010110101024
buttons = []

for i in range(1, 11):
    button = tk.Button(root, text=str(i), command=button_click(i))
    button.pack(fill=tk.BOTH, expand=True)
    buttons.append(button)

keyboard.on_press(on_num_pad_key)


 
# Create a separate thread to run the selected function continuously
selected_function_thread = threading.Thread(target=run_selected_function)
selected_function_thread.daemon = True
selected_function_thread.start()
# Function to handle UI closure
def on_closing():
    exit_event.set()  # Signal the loop to exit
    root.destroy()  # Close the GUI window
    exit()

root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle UI closure

root.mainloop()

