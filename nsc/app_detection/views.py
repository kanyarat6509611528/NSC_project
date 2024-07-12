from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

from app_general.models import Phobias
from django.apps import apps
Phobias = apps.get_model('app_general', 'Phobias')

# --------------------------------------------------------------------------- 

from django.core.files.base import ContentFile
import os
import shutil
import pyktok as pyk 
import cv2

# --------------------------------------------------------------------------- 

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip

# --------------------------------------------------------------------------

import json

from django.db.models import Value
from django.db.models.functions import Concat

# -----------------------------------------------------------------------

# Set paths
media_dir = "app_detection/static/app_detection/media"
video_dir = "app_detection/static/app_detection/video"
frames_dir = "app_detection/static/app_detection/frames"
audio_dir = "app_detection/static/app_detection/audio"
trained_model_path = "app_detection/static/app_detection/model/new1_model10.h5"

uploaded_video_path = "app_detection/static/app_detection/media/download_video.mp4"
output_video_path = "app_detection/static/app_detection/video/output_video.mp4"

for directory in [media_dir, video_dir, frames_dir, audio_dir]:
    os.makedirs(directory, exist_ok=True)

# Load the trained model
model = load_model(trained_model_path)

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
        
        extract_frames(uploaded_video_path, frames_dir)
        
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

def d_loading1(request):
    current_step = 2
    percent = [50, 60, 70, 85, 100] # รอแก้สิ่งนี้เป็นแบบส่งตัวแปรมา

    classify_frames(frames_dir)

    context = {
        'current_step': current_step,
        'percent': percent
    }
    return render(request, 'app_detection/d02_loading1.html', context)

def background_processing(request):

    classify_frames(frames_dir)

    return JsonResponse({'status': 'success'})

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
    result_path = "app_detection/static/app_detection/results.json"
    with open(result_path, 'r') as f:
        results = json.load(f)
    
    pb = Phobias.objects.all().order_by('name_ENG')
    pb_name = [f'{phobia.name_TH} ({phobia.name_ENG})' for phobia in pb]
    filtered_phobias = []
    for phobia in pb_name:
        if any(result['predicted_class_name'] == phobia for result in results):
            filtered_phobias.append(phobia)

    current_step = 4
    
    phobias = Phobias.objects.all().order_by('name_ENG') 
    
    selected_phobias = []

    if request.method == 'POST':
        # Handle form submission
        phobia_ids = request.POST.getlist('phobias')

        request.session['selected_phobias'] = phobia_ids

        for phobia_id in phobia_ids:
            phobia = Phobias.objects.get(id=phobia_id)
            phobia.count += 1  # Increment count
            phobia.save()
            selected_phobias.append(phobia.name_ENG)

        return redirect('d05_loading2') 

    context = {
        'current_step': current_step,
        'phobias': filtered_phobias,

    }

    return render(request, 'app_detection/d04_select.html', context)

# --------------------------------------------------------------------------- 

def blur_video(uploaded_video_path, output_video_path, segment_times):
    import cv2

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

    print("Starting video blurring...")

    while cap.isOpened() and current_segment < len(segment_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if segment_frames[current_segment][0] <= frame_count < segment_frames[current_segment][1]:
            blurred_frame = cv2.GaussianBlur(frame, (51, 51), 0)
            out.write(blurred_frame)
        else:
            out.write(frame)

        frame_count += 1

        if frame_count >= segment_frames[current_segment][1]:
            current_segment += 1

    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_count += 1

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

@login_required
def d_loading2(request):
    current_step = 5
    percent = [50, 60, 70, 85, 100] # รอแก้สิ่งนี้เป็นแบบส่งตัวแปรมา

    # Extract audio from the original video
    audio_path = os.path.join(audio_dir, "original_audio.mp3")
    video_clip = VideoFileClip(uploaded_video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()

    # Retrieve selected phobia IDs from session
    selected_phobia_ids = request.session.get('selected_phobias', [])

    # Query the database to get names based on IDs
    selected_phobias = Phobias.objects.filter(id__in=selected_phobia_ids).annotate(
        combined_name=Concat('name_TH', Value(' ('), 'name_ENG', Value(')'))
    ).values_list('combined_name', flat=True)

    # Load classified results
    results_path = "app_detection/static/app_detection/results.json"
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Filter frames for blur based on predicted_class_name
    frames_to_blur = [result['frame_number'] for result in results if result['predicted_class_name'] in selected_phobias]
    print(frames_to_blur)

    segment_times = get_segment_times(frames_to_blur)

    # Blur video based on segment times
    blur_video(uploaded_video_path, output_video_path, segment_times)

    # Merge the blurred video with the extracted audio
    final_video_path = os.path.join(video_dir, 'final_video_with_audio.mp4')
    merge_video_audio(output_video_path, audio_path, final_video_path)

    context = {
        'current_step': current_step,
        'percent': percent
    }
    return render(request, 'app_detection/d05_loading2.html', context)

# ---------------------------------------------------------------------------

@login_required
def d_finish(request):
    current_step = 6
    
    # Retrieve selected phobia IDs from session
    selected_phobia_ids = request.session.get('selected_phobias', [])

    # Query the database to get names based on IDs
    selected_phobias = Phobias.objects.filter(id__in=selected_phobia_ids).annotate(
        combined_name=Concat('name_TH', Value(' ('), 'name_ENG', Value(')'))
    ).values_list('combined_name', flat=True)

    context = {
        'current_step': current_step,
        'selected_phobias': selected_phobias,
    }

    return render(request, 'app_detection/d06_finish.html', context)