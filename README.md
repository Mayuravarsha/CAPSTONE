# CAPSTONE
# Detection Of Violent Content in Videos using Audio and Video features

In this project, we have proposed 2 deep-learning models for violence detection in videos. 
“AudioProcessor” is a Computer Vision based deep learning model which classifies violent and non-violent audio using the spectrogram of the audio clips. 
The number of trainable parameters in this model amounts to 7.8 M. “VideoProcessor” is a deep learning model which uses C3D as a feature extractor and 
layers of densely connected neurons as the classifier. Using transfer learning, the weights for the feature extractor are imported from the model trained 
on the Sports-1M dataset. Combining the feature extractor and classifier, the number of parameters in the model amounts to 65.9 M where the non-trainable 
parameters are 61.2 M and the trainable ones are 4.7M. Therefore, the total number of trainable parameters is 12.5 M.

We have employed 4 benchmark datasets for evaluating our approach. Experimental results show that our proposed approach achieves better results than the 
state-of-the-art approaches for both person-to-person fights and crowd violence. The proposed model also has a significantly 
lower number of parameters than the models used in most of the approaches. Therefore, the proposed model is very efficient and capable of real-time processing.
