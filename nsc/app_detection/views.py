# Django imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.apps import apps

# App imports
from app_general.models import Phobias, UserPhobias
from django.db import connection
from django.db.models.expressions import RawSQL


# Third-party imports
import pyktok as pyk
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip

# Standard library imports
import os
import shutil
import json
import threading

# Get the Phobias model
Phobias = apps.get_model('app_general', 'Phobias')

# -----------------------------------------------------------------------

# Set paths
media_dir = "app_detection/static/app_detection/media"
video_dir = "app_detection/static/app_detection/video"
frames_dir = "app_detection/static/app_detection/frames"
audio_dir = "app_detection/static/app_detection/audio"
trained_model_path = "app_detection/static/app_detection/model/10class_model.h5"

uploaded_video_path = "app_detection/static/app_detection/media/download_video.mp4"
output_video_path = "app_detection/static/app_detection/video/output_video.mp4"
audio_path = os.path.join(audio_dir, 'original_audio.mp3')

for directory in [media_dir, video_dir, frames_dir, audio_dir]:
    os.makedirs(directory, exist_ok=True)

# Load the trained model
model = load_model(trained_model_path)

progress_file = "app_detection/static/app_detection/progress.txt"

def update_progress(progress):
    with open(progress_file, 'w') as f:
        f.write(f'{progress}')

def read_progress():
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return int(f.read())
    return 0

def reset_progress():
    with open(progress_file, 'w') as f:
        f.write('0') 

# --------------------------------------------------------------------------- 

def save_tiktok_data(url, output_dir, custom_video_name, browser='firefox'):
    # Download TikTok data
    pyk.specify_browser(browser)
    pyk.save_tiktok(url, True, 'video_data.csv', browser)

    current_dir = os.getcwd()
    video_files = [f for f in os.listdir(current_dir) if f.endswith('.mp4')]

    if video_files:
        random_video_name = video_files[0]  # Only one video is downloaded
        original_video_path = os.path.join(current_dir, random_video_name)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        new_video_path = os.path.join(output_dir, f'{custom_video_name}.mp4')

        # Move the video file with the custom name
        shutil.move(original_video_path, new_video_path)

        # Move the CSV file as well (if needed)
        original_csv_path = os.path.join(current_dir, 'video_data.csv')
        new_csv_path = os.path.join(output_dir, 'video_data.csv')
        shutil.move(original_csv_path, new_csv_path)
        
    else:
        raise FileNotFoundError("No video file found in the current directory.")
    
def extract_frames(uploaded_video_path, frames_dir):
    if os.path.exists(frames_dir):
        for filename in os.listdir(frames_dir):
            file_path = os.path.join(frames_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(frames_dir)

    # Open the video file
    cap = cv2.VideoCapture(uploaded_video_path)

    # Get frames per second (fps) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate exact frame interval to save 1 frame per second
    frame_interval = int(round(fps))

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Save every frame_interval-th frame (i.e., 1 frame per second)
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(frames_dir, f'frame_{saved_frame_count:04d}.jpg')
            cv2.imwrite(frame_path, frame)
            saved_frame_count += 1
            print(f"Extracted frame {saved_frame_count}")

        frame_count += 1

    cap.release()

    # Count the number of frames in the directory
    files = os.listdir(frames_dir)
    frame_files = [file for file in files if file.startswith('frame_') and file.endswith('.jpg')]
    num_frames = len(frame_files)

    print(f"Number of frames in the directory: {num_frames}")

# --------------------------------------------------------------------------- 

def d_import(request):
    current_step = 1

    if request.method == 'POST':
        url = request.POST.get('video_url')
        uploaded_file = request.FILES.get('video_file')

        output_dir = os.path.join('app_detection', 'static', 'app_detection', 'media')
        custom_video_name = 'download_video'  # Set the file's name (here)
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        # URL
        if url:
            save_tiktok_data(url, output_dir, custom_video_name)

        # Uploaded file
        if uploaded_file:
            new_file_path = os.path.join(output_dir, f'{custom_video_name}.mp4')
            with open(new_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
         
                    destination.write(chunk)
        
        return redirect('d02_loading1')

    context = {
        'current_step': current_step,
    }
    return render(request, 'app_detection/d01_import.html', context)

# --------------------------------------------------------------------------- 

def classify_frames(frames_dir):
    # Initialize results list
    results = []

    # Fetch phobias from the database and prepare class names
    phobias = Phobias.objects.all().order_by('name_ENG')
    listTW = [f'{phobia.name_TH} ({phobia.name_ENG})' for phobia in phobias]
    class_names = [(name, i + 1) for i, name in enumerate(listTW)] + [("อื่น ๆ (Others)", len(listTW) + 1)]

    # Initialize class counts
    class_counts = {name: 0 for name, _ in class_names}

    # Initialize
    frame_number = 0
    frame_time = "0.00"

    # Iterate over frames in frames_dir
    for filename in sorted(os.listdir(frames_dir)):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            file_path = os.path.join(frames_dir, filename)
            img = image.load_img(file_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = tf.keras.applications.efficientnet_v2.preprocess_input(img_array)

            # Use the loaded Keras model for prediction
            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction, axis=1)[0]
            predicted_class_name = listTW[predicted_class_index]  # Access class name from list
            predicted_prob = np.max(prediction, axis=1)[0] * 100

            # Debugging prints
            print(f"Processing frame {frame_number}: {filename}")
            print(f"Predicted class: {predicted_class_name} with probability: {predicted_prob:.2f}%")

            # Perform blur or copy based on classification
            if predicted_prob < 80:
                predicted_class_name = "อื่น ๆ (Others)"
                print(f"Frame classified as 'อื่น ๆ (Others)' due to low confidence: {predicted_prob:.2f}%")# Save the result
                

            # Save result to results list
            result = {
                'filename': filename,
                "frame_number": frame_number,
                "frame_time": frame_time,
                "predicted_class_name": predicted_class_name
            }
            results.append(result)

            frame_number += 1

            frame_time = float(frame_time)
            frame_time += 0.01
            if frame_time - int(frame_time) == 0.60:
                frame_time = int(frame_time)  + 1
            frame_time = round(frame_time, 2)
            frame_time = f"{frame_time:.2f}"
            
            class_counts[predicted_class_name] += 1

    results_path = "app_detection/static/app_detection/results.json"
    if os.path.exists(results_path):
        os.remove(results_path)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=4)

    # Calculate and return the percentage of each class
    total_images = sum(class_counts.values())
    class_distribution = []
    for class_name, count in class_counts.items():
        percentage = (count / total_images) * 100 if total_images > 0 else 0
        class_distribution.append({"name": class_name, "percent": f"{percentage:.2f}"})

    percentage_path = "app_detection/static/app_detection/percentage.json"
    if os.path.exists(percentage_path):
        os.remove(percentage_path)
    with open(percentage_path, 'w') as f:
        json.dump(class_distribution, f, indent=4)

def extract_audio(uploaded_video_path, audio_dir):
    # Create the output audio file path
    audio_path = os.path.join(audio_dir, "original_audio.mp3")
    
    # Load the video file
    video_clip = VideoFileClip(uploaded_video_path)
    
    # Extract audio from the video
    audio_clip = video_clip.audio
    
    # Write the audio file
    audio_clip.write_audiofile(audio_path)
    
    # Close the audio and video clips
    audio_clip.close()
    video_clip.close()

    print("Extract audio complete!!!")

def task_1():
    extract_audio(uploaded_video_path, audio_dir)
    update_progress(30)
    
    # สกัดเฟรม
    extract_frames(uploaded_video_path, frames_dir)
    update_progress(60)  # ส่ง 50% หลังจากสกัดเฟรม

    # Classify frames
    classify_frames(frames_dir)
    update_progress(100)

def start_task_1_thread():
    task_thread = threading.Thread(target=task_1)
    task_thread.start()
    return task_thread

def d_loading1(request):
    current_step = 2
    
    reset_progress()
    start_task_1_thread()

    context = {
        'current_step': current_step,
    }

    return render(request, 'app_detection/d02_loading1.html', context)

def get_progress(request):
    progress = read_progress()
    return JsonResponse({'percent': progress})

# --------------------------------------------------------------------------- 

def d_result(request):

    # Load percentage 
    percentage_path = "app_detection/static/app_detection/percentage.json"
    with open(percentage_path, 'r') as f:
        class_distribution = json.load(f)

    context = {
        'current_step': 3,
        'phobias': class_distribution,
    }

    # Find the maximum phobia based on percentage
    if class_distribution:
        max_phobia = max(class_distribution, key=lambda x: float(x['percent']))
        context['max_name'] = max_phobia['name']
        context['max_percent'] = max_phobia['percent']

    return render(request, 'app_detection/d03_result.html', context)

# --------------------------------------------------------------------------- 

def d_information(request):
    result_path = "app_detection/static/app_detection/results.json"
    with open(result_path, 'r') as f:
        results = json.load(f)
    
    image_list = []
    image_dir = os.path.join(settings.BASE_DIR, 'app_detection/static/app_detection/frames')
    for filename in os.listdir(image_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join('app_detection/frames/', filename)
            print(image_path)
            image_list.append(image_path)

    current_step = 3

    pb = Phobias.objects.all().order_by('name_ENG')
    pb_name = [f'{phobia.name_TH} ({phobia.name_ENG})' for phobia in pb]
    filtered_phobias = []
    for phobia in pb_name:
        if any(result['predicted_class_name'] == phobia for result in results):
            filtered_phobias.append(phobia)

    context = {
        'current_step': current_step,
        'phobias': filtered_phobias,
        'results': results,
        'image_list': image_list,
    }
    return render(request, 'app_detection/d03_information.html', context)

# --------------------------------------------------------------------------- 

def d_select(request):
    # โหลดข้อมูลผลลัพธ์จาก JSON
    result_path = "app_detection/static/app_detection/results.json"
    with open(result_path, 'r') as f:
        results = json.load(f)
    
    user_id = request.user.id
    
     # ใช้ RawSQL เพื่อสร้างชื่อที่รวมกัน
    user_phobias = UserPhobias.objects.filter(user_id=user_id).annotate(
        combined_name=RawSQL(
            """
            SELECT CONCAT(agp.name_TH, ' (', agp.name_ENG, ')')
            FROM app_general_phobias agp
            WHERE agp.id = userphobias.phobia_id
            """,
            []
        )
    ).values_list('combined_name', flat=True)
    

    pb = Phobias.objects.all().order_by('name_ENG')
    pb_name = [f'{phobia.name_TH} ({phobia.name_ENG})' for phobia in pb]
    filtered_phobias = [phobia for phobia in pb_name if any(result['predicted_class_name'] == phobia for result in results)]

    current_step = 4 
    selected_phobias = []

    if request.method == 'POST':
        selected_phobias = request.POST.getlist('phobias')  # Get list of selected phobia names
        
        for phobia_name in selected_phobias:
            # Split the name to separate Thai and English names
            phobia_eng = phobia_name.split('(')[-1].strip(')').strip()
            
            phobia = Phobias.objects.get(name_ENG=phobia_eng)
            phobia.count += 1
            phobia.save()

        request.session['selected_phobias'] = selected_phobias
        
        return redirect('d05_loading2')

    context = {
        'current_step': current_step,
        'phobias': filtered_phobias,
        'user_phobias': user_phobias,
        'selected_phobias': selected_phobias,
    }

    return render(request, 'app_detection/d04_select.html', context)

# --------------------------------------------------------------------------- 

def blur_video(uploaded_video_path, output_video_path, segment_times):
    cap = cv2.VideoCapture(uploaded_video_path)
    if not cap.isOpened():
        print("Error opening video file.")
        return

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    segment_frames = [(int(start * frame_rate), int(end * frame_rate)) for start, end in segment_times]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width, frame_height))

    frame_count = 0
    current_segment = 0
    buffer = []

    print("Starting video blurring...")

    # Read the first frame
    ret, frame = cap.read()

    if ret:
        # Perform Gaussian blur on the first frame
        blurred_frame = cv2.GaussianBlur(frame, (101, 101), 0)
        out.write(blurred_frame)  # Write the blurred frame to output video
        print("Blurred the first frame.")

    while cap.isOpened() and current_segment < len(segment_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if segment_frames[current_segment][0] <= frame_count < segment_frames[current_segment][1]:
            blurred_frame = cv2.GaussianBlur(frame, (101, 101), 0)
            buffer.append(blurred_frame)
        else:
            buffer.append(frame)

        frame_count += 1

        if frame_count >= segment_frames[current_segment][1]:
            current_segment += 1

        if len(buffer) >= 100:  # Write in chunks of 100 frames
            for buffered_frame in buffer:
                out.write(buffered_frame)
            buffer = []

    # Write remaining frames
    if buffer:
        for buffered_frame in buffer:
            out.write(buffered_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Video blurring completed.")


def get_segment_times(frame_numbers):
    segment_times = [(frame_num - 1, frame_num) for frame_num in frame_numbers]
    return segment_times

def merge_video_audio(uploaded_video_path, audio_path, output_video_path):
    video_clip = VideoFileClip(uploaded_video_path)
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    video_clip.close()
    audio_clip.close()
    print(f"Video merged with audio and saved to '{output_video_path}'")

# ----------------------------------------------------------------------------------------------

def task_2(uploaded_video_path, output_video_path, audio_path, video_dir, results_path, selected_phobias):
    # Load classified results
    with open(results_path, 'r') as f:
        results = json.load(f)

    # Filter frames for blur based on predicted_class_name
    frames_to_blur = [result['frame_number'] for result in results if result['predicted_class_name'] in selected_phobias]
    print(frames_to_blur)

    segment_times = get_segment_times(frames_to_blur)
    update_progress(20)

    # Blur video based on segment times
    blur_video(uploaded_video_path, output_video_path, segment_times)
    update_progress(60)  

    # Merge the blurred video with the extracted audio
    final_video_path = os.path.join(video_dir, 'final_video_with_audio.mp4')
    merge_video_audio(output_video_path, audio_path, final_video_path)
    update_progress(100)  

def start_task_2_thread(uploaded_video_path, output_video_path, audio_path, video_dir, results_path, selected_phobias):
    task_thread = threading.Thread(target=task_2, args=(uploaded_video_path, output_video_path, audio_path, video_dir, results_path, selected_phobias))
    task_thread.start()
    return task_thread

@login_required
def d_loading2(request):
    current_step = 5

    # Retrieve selected phobia IDs from session
    selected_phobias = request.session.get('selected_phobias', [])

    results_path = "app_detection/static/app_detection/results.json"
    final_video_path = os.path.join(video_dir, 'final_video_with_audio.mp4')
    audio_path = os.path.join(audio_dir, 'original_audio.mp3')

    # Reset progress and start task in thread
    reset_progress()
    start_task_2_thread(uploaded_video_path, output_video_path, audio_path, video_dir, results_path, selected_phobias)

    context = {
        'current_step': current_step,
        'selected_phobias': selected_phobias,
    }

    return render(request, 'app_detection/d05_loading2.html', context)

# ---------------------------------------------------------------------------

@login_required
def d_finish(request):
    current_step = 6
    
    # Retrieve selected phobia IDs from session
    selected_phobias = request.session.get('selected_phobias', [])

    context = {
        'current_step': current_step,
        'selected_phobias': selected_phobias,
    }

    return render(request, 'app_detection/d06_finish.html', context)