# Smart-Video-Monitoring
This Smart Video Monitoring System, by the help of python Tkinter GUI library for motion detection as frontend, and video classification model as backend.

## Overview
Security and monitoring of a facility is an essential part of keeping the premises safe and secure. Security cameras or CCTV, alarm systems, and monitoring guards can all be used to deter crime and unauthorized entrance. Also, by enabling real-time video and security system notifications to onsite personnel or offsite security teams, monitored in remote control rooms, facilities can remain alert to possible intrusions, thefts, or other situations that may arise. But the problem with such a system is that its costly in hiring many security teams to monitor the premises, and their inefficient storage uses. 

The idea of the project is to provide a desktop application that does the same work as smart cameras, but by using normal conventional cameras integrated with a supervised machine learning model to detect motion and recognize objects.

Python Tkinter library is used to build a graphical user interface, that can automatically work with no interference from the outside world. With the help of computer vision, the detection of motion in the video can be made by applying a set of filters to calculate the difference between frames in order to detect objects and make a bounded rectangular box around them, and that is all done with the help of popular python library called OpenCV. Tensorflow and Keras libraries are used to build the machine learning model to recognize extracted objects from the previous step with the help of a modified version of Overfeat algorithm. And by using the model, the research came out with great results in less time and less CPU usage.
