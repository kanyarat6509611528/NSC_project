from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
import time

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

# -----------------------------------------------------------------------

# Define paths
media_directory = "app_detection/static/app_detection/media"
allimages_directory = "app_detection/static/app_detection/allimages"
imagepersec_directory = "app_detection/static/app_detection/imagePerSec"
blurred_images_directory = "app_detection/static/app_detection/blurredImages"
audio_directory = "app_detection/static/app_detection/audio"
video_directory = "app_detection/static/app_detection/video"
trained_model_path = "app_detection/static/app_detection/model/new3_model.h5"

uploaded_video_path = "app_detection/static/app_detection/media/download_video.mp4"

# Create directories if they do not exist
for directory in [media_directory, allimages_directory, imagepersec_directory, blurred_images_directory, audio_directory, video_directory]:
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

        # Extract frames from video
        cap = cv2.VideoCapture(uploaded_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_path = os.path.join(allimages_directory, f"frame_{frame_number:04d}.jpg")
            cv2.imwrite(frame_path, frame)

            if frame_number % int(fps) == 0:
                frame_per_sec_path = os.path.join(imagepersec_directory, f"frame_{frame_number:04d}.jpg")
                cv2.imwrite(frame_per_sec_path, frame)

            frame_number += 1

        cap.release()
        print(f"Extracted {frame_number} frames to {allimages_directory}")
        print(f"Extracted {frame_number // int(fps)} frames to {imagepersec_directory}")

        return redirect('d02_loading1')

    context = {
        'current_step': current_step,
    }
    return render(request, 'app_detection/d01_import.html', context)

# --------------------------------------------------------------------------- 

def d_loading1(request):
    current_step = 2
    percent = [50, 60, 70, 85, 100] # รอแก้สิ่งนี้เป็นแบบส่งตัวแปรมา
    
    context = {
        'current_step': current_step,
        'percent': percent
    }
    return render(request, 'app_detection/d02_loading1.html', context)

# --------------------------------------------------------------------------- 

def d_result(request):
    
    phobias = Phobias.objects.all().order_by('name_ENG')
    listTW = [f'{phobia.name_TH} ({phobia.name_ENG})' for phobia in phobias]
    class_names = [(name, i + 1) for i, name in enumerate(listTW)] + [("อื่น ๆ (Others)", len(listTW) + 1)]

    # Initialize class counts
    class_counts = {name: 0 for name, _ in class_names}

    # Function to load and preprocess an image
    def load_and_process_image(file_path):
        img = image.load_img(file_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.efficientnet_v2.preprocess_input(img_array)
        return img_array

    # Total number of images processed
    total_images = 0

    results = []

    # Iterate through each file in the directory
    for filename in sorted(os.listdir(allimages_directory)):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            file_path = os.path.join(allimages_directory, filename)
            
            # Load and preprocess the image
            img_array = load_and_process_image(file_path)

            # Use the loaded Keras model for prediction
            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction, axis=1)[0]
            predicted_class_name = listTW[predicted_class_index]
            predicted_prob = np.max(prediction, axis=1)[0] * 100

            # Debugging prints
            print(f"Processing frame: {filename}")
            print(f"Predicted class: {predicted_class_name} with probability: {predicted_prob:.2f}%")

            # Perform blur or copy based on classification
            if predicted_prob < 80:
                predicted_class_name = "อื่น ๆ (Others)"
                print(f"Frame classified as 'อื่น ๆ (Others)' due to low confidence: {predicted_prob:.2f}%")# Save the result
            
            results.append({
                'filename': filename,
                'predicted_class_name': predicted_class_name
            })

            # Increment the count for the predicted class
            class_counts[predicted_class_name] += 1
            total_images += 1

    # Calculate and store the percentage of each class in the context
    class_distribution = []
    for class_name, count in class_counts.items():
        percentage = (count / total_images) * 100 if total_images > 0 else 0
        class_distribution.append({"name": class_name, "percent": f"{percentage:.2f}"})

    context = {
        'current_step': 3,
        'phobias': class_distribution,
    }

    # Find the maximum phobia
    max_phobia = max(context['phobias'], key=lambda x: x['percent'])
    context['max_name'] = max_phobia['name']
    context['max_percent'] = max_phobia['percent']

    results_path = "app_detection/static/app_detection/results.json"

    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    with open(results_path, "w") as json_file:
        json.dump(results, json_file, indent=4)
    
    return render(request, 'app_detection/d03_result.html', context)

# --------------------------------------------------------------------------- 

def d_information(request):
    current_step = 3
    phobias = Phobias.objects.all()  
    context = {
        'current_step': current_step,
        'phobias': phobias
    }
    return render(request, 'app_detection/d03_information.html', context)

# --------------------------------------------------------------------------- 

def d_select(request):
    current_step = 4
    
    phobias = Phobias.objects.all() 
    
    selected_phobias = []

    if request.method == 'POST':
        # Handle form submission
        phobia_ids = request.POST.getlist('phobias')

        request.session['selected_phobias'] = phobia_ids

        for phobia_id in phobia_ids:
            phobia = Phobias.objects.get(id=phobia_id)
            phobia.count += 1  # Increment count
            phobia.save()
            selected_phobias.append(phobia.name)

        return redirect('d05_loading2') 

    context = {
        'current_step': current_step,
        'phobias': phobias,
    }

    return render(request, 'app_detection/d04_select.html', context)

# --------------------------------------------------------------------------- 

def d_loading2(request):
    current_step = 5

    percent = [50, 60, 70, 85, 100] # รอแก้สิ่งนี้เป็นแบบส่งตัวแปรมา
    
    context = {
        'current_step': current_step,
        'percent': percent
    }
    return render(request, 'app_detection/d05_loading2.html', context)

# ---------------------------------------------------------------------------

def extract_audio_and_create_video(uploaded_video_path):
    # Extract audio from the original video
    audio_path = os.path.join(audio_directory, "original_audio.mp3")
    video_clip = VideoFileClip(uploaded_video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()

    # Generate video from processed frames
    def generate_video():
        images = [img for img in os.listdir(blurred_images_directory) if img.endswith((".jpg", ".jpeg", ".png"))]
        images.sort()  # Ensure the images are sorted by filename

        if images:
            first_frame_path = os.path.join(blurred_images_directory, images[0])
            first_frame = cv2.imread(first_frame_path)
            height, width = first_frame.shape[:2]

            clips = []
            for image in images:
                blurred_frame_path = os.path.join(blurred_images_directory, image)
                frame = cv2.imread(blurred_frame_path)

                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))

                clips.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            fps = video_clip.fps
            final_video = ImageSequenceClip(clips, fps=fps)
            final_audio = AudioFileClip(audio_path)
            final_video = final_video.set_audio(final_audio)
            final_video.write_videofile(os.path.join(video_directory, "blurred_video_with_audio.mp4"), fps=fps)
            print(f"Created blurred video with audio: {os.path.join(video_directory, 'blurred_video_with_audio.mp4')}")
        else:
            print("No frames found to create video.")

    generate_video()

def d_finish(request):
    current_step = 6

    # Retrieve selected phobia IDs from session
    selected_phobia_ids = request.session.get('selected_phobias', [])

    # Query the database to get names based on IDs
    selected_phobias = Phobias.objects.filter(id__in=selected_phobia_ids).values_list('name', flat=True)

    results_path = "app_detection/static/app_detection/results.json"
    
    with open(results_path, "r") as json_file:
        results = json.load(json_file)

    # Get list of filenames from allimages_directory
    allimages_directory = "app_detection/static/app_detection/allimages"
    filenames = [filename for filename in os.listdir(allimages_directory) if filename.endswith((".jpg", ".png"))]

    for filename in filenames:
        result = None
        for res in results:
            if res['filename'] == filename:
                result = res
                break
        
        if result:
            predicted_class_name = result['predicted_class_name']
            
            if predicted_class_name in selected_phobias:
                print(f"Blurring frame: {predicted_class_name}")
                file_path = os.path.join(allimages_directory, filename)
                img = cv2.imread(file_path)
                if img is not None:
                    blurred_img = cv2.GaussianBlur(img, (51, 51), 0)  # Large kernel size for significant blurring
                    blurred_file_path = os.path.join(blurred_images_directory, filename)
                    cv2.imwrite(blurred_file_path, blurred_img)
                    print(f"Blurred image saved: {blurred_file_path}")
                else:
                    print(f"Error loading image: {filename}")
            else:
                print(f"Copying original frame for 'others' class: {predicted_class_name}")
                shutil.copy(os.path.join(allimages_directory, filename), os.path.join(blurred_images_directory, filename))
        else:
            print(f"No result found for filename: {filename}")

    print("Blurring process completed.")

    extract_audio_and_create_video(uploaded_video_path)

    context = {
        'current_step': current_step,
    }

    return render(request, 'app_detection/d06_finish.html', context)