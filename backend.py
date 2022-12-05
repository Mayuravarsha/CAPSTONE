import os 
from flask import Flask,flash, request, jsonify
from werkzeug.utils import secure_filename

import os
import numpy as np
import tensorflow as tf
import tensorflow_io as tfio
import subprocess
import cv2
from matplotlib  import pyplot as plt
app = Flask(__name__)




UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class AudioProc:
    def __init__(self,filepath):
        self.filepath = filepath
        

    def convert(self, filename):
        file = filename.split('.')[0]+'.wav'
        print(os.path.join(self.filepath, filename), os.path.join(self.filepath, file))
        subprocess.call(["ffmpeg", "-y", "-i", os.path.join(self.filepath, filename), os.path.join(
            self.filepath, file)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return 1

    def get_spectrogram(self, waveform):
        frame_length = 255
        frame_step = 128
        waveform = tf.cast(waveform, tf.float32)

        spectrogram = tf.signal.stft(
            waveform, frame_length=frame_length, frame_step=frame_step)
        spectrogram = tf.abs(spectrogram)
        return spectrogram

    def load_audio(self, filename):
       
        if self.convert(filename):
            sample_rate = 44000
            channels = 1
            file = filename.split('.')[0]+'.wav'
            
            audio_binary = tf.io.read_file(os.path.join(self.filepath, file))
            audio, original_sample_rate = tf.audio.decode_wav(
                audio_binary, desired_channels=channels)
            audio = tfio.audio.resample(
                audio, original_sample_rate.numpy(), sample_rate)
            waveform = tf.squeeze(audio, axis=-1)
            return waveform, sample_rate

    def process(self, filename):
        waveform, sample_rate = self.load_audio(filename)
        spectrogram = self.get_spectrogram(waveform)
        spectrogram = spectrogram.numpy()
        spectrogram.resize((1024, 129))
        spectrogram = np.array(spectrogram, dtype=np.float32)
        spectrogram = spectrogram[None, :, :]

        model = tf.keras.models.load_model('final_audio_model.h5')
        nv,v= model.predict(spectrogram).ravel()

        print('Result of Audio Processor: ', nv,v)
        if v>0.8:
            print('Audio is violent')
        else:
            print('Auidio is non-violent')
        return 0


class VideoProc:
    def __init__(self, filepath):
        self.filepath = filepath

    def process(self):
        video = cv2.VideoCapture(self.filepath)
        numframes = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video.get(cv2.CAP_PROP_FPS))
        chunks = numframes//16
        vid = []
        videoFrames = []
        while True:
            ret, img = video.read()
            if not ret:
                break
            videoFrames.append(cv2.resize(img, (112, 112)))

        vid = np.array(videoFrames, dtype=np.float32)
        res = []
        flag = 0
        for i in range(chunks):
            X = vid[i*16:i*16+16]
            
            if X.shape[0] == 16:
                model = tf.keras.models.load_model('final_video_model.h5')
                X = X[None, :, :]
                pred = model.predict(X)
                print(pred)
                pred = 1 if pred >= 0.75 else 0
                res.append(pred)
        print(res)        
        vper=res.count(1)/len(res)            
        print(vper)
        data=[vper,100-vper]
        labels=['Violent','Non-Violent']
       
        if vper>0.70:
            print('Violent Video')
        else:
            print('Non-Violent Video')
        return vper
        


@app.route('/home', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        
        file = request.files['file'] 
        filename = secure_filename(file.filename)   
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename)
        flash('Video successfully uploaded and displayed below')
        dirpath = os.path.abspath('./uploads')
        filepath = os.path.abspath('./uploads/'+filename)
        aud = AudioProc(dirpath)
        print('Processing Audio')
        try: lt = aud.process(filename)
        except:
            print('NO AUDIO')
        finally:
            print('Processing Video')
            vid = VideoProc(filepath)
            vper=vid.process()
            response = jsonify({"data": vper})
            response.headers.add('Access-Control-Allow-Origin', '*')
            for i in os.listdir(dirpath):
                file = dirpath+'\\'+i

                print(file)
                if os.path.isfile(file):
                    os.remove(file)

            return response
        

              

if __name__=="__main__":
  app.run(debug=True)
