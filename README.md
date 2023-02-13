# Smart-Video-Monitoring
This Smart Video Monitoring System, by the help of python Tkinter GUI library for motion detection as frontend, and video classification model as backend.

## 🐱‍🏍 Overview
Security and monitoring of a facility is an essential part of keeping the premises safe and secure. Security cameras or CCTV, alarm systems, and monitoring guards can all be used to deter crime and unauthorized entrance. Also, by enabling real-time video and security system notifications to onsite personnel or offsite security teams, monitored in remote control rooms, facilities can remain alert to possible intrusions, thefts, or other situations that may arise. But the problem with such a system is that its costly in hiring many security teams to monitor the premises, and their inefficient storage uses. 

The idea of the project is to provide a desktop application that does the same work as smart cameras, but by using normal conventional cameras integrated with a supervised machine learning model to detect motion and recognize objects.

Python Tkinter library is used to build a graphical user interface, that can automatically work with no interference from the outside world. With the help of computer vision, the detection of motion in the video can be made by applying a set of filters to calculate the difference between frames in order to detect objects and make a bounded rectangular box around them, and that is all done with the help of popular python library called OpenCV. Tensorflow and Keras libraries are used to build the machine learning model to recognize extracted objects from the previous step with the help of a modified version of Overfeat algorithm. And by using the model, the research came out with great results in less time and less CPU usage.

## 🚩 About dataset
In machine learning, a dataset is specified to train the model with. Choosing the right dataset is important step, because it has great reflection in model accuracy and prediction. the dataset is consisting of two classes, which are named (HAC Dataset):
- Cars
- Humans + Animals (Object)

The reason that specific classes are used is because most of the motion captured in videos consist of those specific classes. A collection of dataset is used from:
-	UCF-50 (University of Central Florida): it is an action recognition dataset with 50 action categories, consisting of realistic videos taken from YouTube staged by actors. Some UCF50 data set's 50 action categories collected from YouTube are: Baseball, Basketball, Biking, Horse Racing, Walking with Dog, etc. However, that wasn’t taken all, but some of interesting clip is taken and added to the dataset.
-	YouTube: the data is taken from set of clips from live vide

![image](https://user-images.githubusercontent.com/40520844/218315316-a9392f0e-108f-457b-9d0b-5fb0526dc31e.png)

## 🐱‍💻 The desktop application
Main screen (dashboard)

![image](https://user-images.githubusercontent.com/40520844/218315396-75a3b006-0d37-4278-9f54-514e7eacc5a0.png)

Motion Detection Process Screen

![image](https://user-images.githubusercontent.com/40520844/218315413-dc4ace3b-9010-4158-bf16-4ad5d7a6380a.png)

Object Detection and Recognition Screen

![image](https://user-images.githubusercontent.com/40520844/218315424-901e34e2-f473-40ec-b51f-fd14e1f11edf.png)

## 🎮 How to run it?
- Firstly, open the <Smart Video Monitoring.py> in <Frontend> directory
- Change the directories of resources to match your path (path changes needed on: <iconbitmap>, <path> variable on <predictObject> function, <open_file_photo> variable, and <show_file_photo> variable)
- The default camera that will be running is an external camera, if you wish to use your camera, change the <out> variable on <liveOrLocalTrigger> function to <0> instead of <1>

## 🤔 Hava a question?
Let's chat on [linkedin](https://www.linkedin.com/in/motwkel-idris-1b73b3159/)
