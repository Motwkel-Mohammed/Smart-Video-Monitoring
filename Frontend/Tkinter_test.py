'''
# Created by: motwkel, 19-11-2022
# This is application for detecting motion on the video and recognize the detected object,
# and classify it as Human-Animal or Car (HAC).
# Build by using Tkinter GUI library with the help of computer vision to detect motion
# on the video, and by the help of CNN Deep learning model to recognize the object in the video.
# Note: Normal Camera with good quality is used to capture the video stream, or (other option)
# upload an existing video to make the analysis out of it.
'''

import os
import shutil
import datetime
import threading
import subprocess
import customtkinter
import cv2 as cv
import numpy as np
import tkinter as tk
from tqdm import tqdm
from tensorflow import keras
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
from tkVideoPlayer import TkinterVideo

###############################################################
# Note: change the directories of resources to match your path
###############################################################

# for the theme (appearance mode)
# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    WIDTH = 780
    HEIGHT = 520
    # get current system user (to make the directory to save the files)
    userName= os.getlogin()

    def __init__(self):
        super().__init__()

        # set title and icon and window size
        self.title(" Smart Video Monitoring")
        self.iconbitmap(
            'C:/Users/Motwkel/Downloads/my videos/TkInter/src/cctv.ico')
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)
        # call .on_closing() when app gets closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # make new directories if not exist
        def checkDirectory():
            path= os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring')
            if not os.path.exists(os.path.join(path, 'Cache')):
                os.mkdir(os.path.join(path, 'Cache'))
            if not os.path.exists(os.path.join(path, 'Cars')):
                os.mkdir(os.path.join(path, 'Cars'))
            if not os.path.exists(os.path.join(path, 'Objects')):
                os.mkdir(os.path.join(path, 'Objects'))
            if not os.path.exists(os.path.join(path,'Thumbnails')):
                os.mkdir(os.path.join(path, 'Thumbnails'))

        # binded event, excute when user hover over the help switch button
        def enterHelp(event):
            # set the text of help label
            self.helpLabel.configure(text="This is used for help and it display a note in the bottom of the application, turn it off to stop showing help from the application.")

        # binded event, excute when user hover over the video player screen
        def enterVideo(event):
            # if help swith is on
            if Help.get() == 'help':
                self.helpLabel.configure(text="Enables You to see the summary of the Object Detection and Recognition")
            
        # binded event, excute when user hover over the live switch button
        def enterLive(event):
            if Help.get() == 'help':
                self.helpLabel.configure(text="This is Live or Local")
        
        # binded event, excute when user hover over the zoom-at-object switch button
        def enterZoom(event):
            if Help.get() == 'help':
                self.helpLabel.configure(text="This is Zoom at Object")
        
        # binded event, excute when user hover over the display-motion switch button        
        def enterDisplay(event):
            if Help.get() == 'help':
                self.helpLabel.configure(text="This is Display Motion")

        # binded event, excute when user hover out of the views
        def outOf(event):
            self.helpLabel.configure(text="")    

        # update the end duration time of the video player
        def update_duration(event):
            duration = self.vid_player.video_info()["duration"]
            self.end_time.configure(
                text=str(datetime.timedelta(seconds=int(duration))))
            self.progress_slider["to"] = duration

        # update the duration time of the video player
        def update_scale(event):
            progress_value.set(self.vid_player.current_duration())
            self.start_time.configure(
                text=str(datetime.timedelta(seconds=progress_value.get())))

        # update the seek of the video player when duration change
        def seek(value):
            self.vid_player.seek(int(value))
            self.start_time.configure(
                text=str(datetime.timedelta(seconds=int(value))))

        # skip + or - 5 sec
        def skip(value: int):
            """ skip seconds """
            self.vid_player.seek(int(self.progress_slider.get())+value)
            progress_value.set(self.progress_slider.get() + value)
            self.start_time.configure(
                text=str(datetime.timedelta(seconds=progress_value.get())))

        # play and pause logic of video player
        def play_pause():
            if self.vid_player.is_paused():
                self.vid_player.play()
                self.play_pause_btn.configure(text='Pause')
            else:
                self.vid_player.pause()
                self.play_pause_btn.configure(text='Play')

        # logic when video ended
        def video_ended(event):
            self.progress_slider.set(self.progress_slider["to"])
            self.play_pause_btn.configure(text='Play')
            self.progress_slider.set(0)

        # open windows explorer at the saved video directory
        def showFile():
            path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring')
            subprocess.Popen(f'explorer /,{path}')

        # open the video and make the analysis (for local video)
        def openFile():
            # getting the video 
            file_path = filedialog.askopenfilename()
            # if not empty
            if file_path:
                # setup state of views
                self.play_pause_btn.configure(state=customtkinter.NORMAL)
                liveOrLocal.set('local')
                path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                for files in os.listdir(path):
                    # clear thumbnails directory
                    os.remove(os.path.join(path, files))
                # motion detection process
                out = videoAnalysis(file_path)
                # if not empty
                if out:
                    # setup state of views
                    self.play_pause_btn.configure(text='Pause')
                    self.vid_player.load(out)
                    self.helpLabel.configure(text= "Progress .......")
                    # make prediction for detected object
                    prdictWithThread(self)
                    self.helpLabel.configure(text= "")
                else:
                    # if no motion detected
                    messagebox.showinfo("Successfull ✔", "Not recognize a lot of Motion")
            else:
                # if no file selected
                messagebox.showerror("Error ❌", "No File!")

        # thread to make prediction on background
        def prdictWithThread(self):
            t= threading.Thread(target= self.predictObject)
            t.start()
        
        # Motion detection process
        def videoAnalysis(file_path):
            # get current date
            date_time = datetime.datetime.now()
            startDate = str(date_time.strftime(r"%d-%m-%Y %H;%M;%S"))
            i = 0
            start= date_time.minute
            # the path of saved video
            out = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Cache', startDate+'.mp4')

            # make sure that directories exists
            checkDirectory()
            # 1 => external_camera, 0=> device_camera
            # start capturing the video
            cap = cv.VideoCapture(file_path)
            # read two frames
            _, frame1 = cap.read()
            _, frame2 = cap.read()

            original_video_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            original_video_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

            # check if zoom-at-object switch is on
            if zoomAtObject.get() == 'zoom':
                # dimensions: (100x100)
                video_writer = cv.VideoWriter(out, cv.VideoWriter_fourcc(
                    'm', 'p', '4', 'v'), cap.get(cv.CAP_PROP_FPS), (100, 100))
            else:
                # original video dimensions
                video_writer = cv.VideoWriter(out, cv.VideoWriter_fourcc('m', 'p', '4', 'v'), cap.get(
                    cv.CAP_PROP_FPS), (original_video_width, original_video_height))

            # when the source video still running..
            while cap.isOpened():
                # if video is disconnected or corrupted
                if np.any(frame1) == None:
                    messagebox.showerror("Error ❌", "Video is disconnected!")
                    # clear resources
                    video_writer.release()
                    cap.release()
                    cv.destroyAllWindows()
                    # remove video from Cache directory
                    os.remove(out)
                    path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                    # remove frames from Thumbnails directory
                    for files in os.listdir(path):
                        os.remove(os.path.join(path, files))
                    return 0

                # else: compare the two frames    
                diff = cv.absdiff(frame1, frame2)
                # aplly filters to them, to detect the diffrences
                diff_gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
                blur = cv.bilateralFilter(diff_gray, 1, 100, 40)
                _, thresh = cv.threshold(blur, 70, 225, cv.THRESH_BINARY)
                dilated = cv.dilate(thresh, None, iterations=10)
                # bound the detected object
                contours, _ = cv.findContours(
                    dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    # get the width and height and x,y location of the object
                    (x, y, w, h) = cv.boundingRect(contour)
                    # restrict the sensitivity
                    if cv.contourArea(contour) < 1200:
                        continue
                    # check if display-motion switch is on
                    if displayMotion.get() == 'display':
                        # Draw rectangle around object
                        cv.rectangle(frame1, (x, y),(x+w, y+h), (255, 0, 0), 2)

                    # cv.putText(frame1, "Status: {}".format('Movement'), 
                    # (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    
                    date_time = datetime.datetime.now()
                    frameDate = date_time.strftime("%m/%d/%Y %H:%M:%S")

                    # check if live switch is on
                    if liveOrLocal.get() == 'live':
                        # while less than 5 minutes
                        if date_time.minute >= int(start)+5:
                            video_writer.release()
                            cap.release()
                            cv.destroyAllWindows()
                            # ignor stream if extract less than 20 frames
                            if i <= 20:
                                # remove video from Cache directory
                                os.remove(out)
                                path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                                # remove frames from Thumbnails directory
                                for files in os.listdir(path):
                                    os.remove(os.path.join(path, files))
                                # retuurn nothing
                                return 0
                            # return the result of the video
                            return out

                    # set text on the video indicating the time
                    cv.putText(frame1, frameDate, (30, 60), cv.FONT_HERSHEY_SCRIPT_COMPLEX,
                               0.8, (255, 255, 255), 2)

                    size = frame1[y:y+h, x:x + w].shape
                    # restrict the dimentionality
                    if liveOrLocal.get() == 'live':
                        if zoomAtObject.get() == 'zoom':
                            sclaedFrame = cv.resize(
                                frame1[y:y+h, x:x + w], (100, 100))
                        else:
                            sclaedFrame = cv.resize(
                                frame1, (original_video_width, original_video_height))

                    # save only the extracted object with more than (100x100) dimentionality
                    if(size[0] >= 100 and size[1] >= 100):
                        # save only the extracted object with dimentionality not equal the original dimention of the video
                        if(size[1] != original_video_width and size[0] != original_video_height):
                            # save the resulted video
                            if zoomAtObject.get() == 'zoom':
                                # to smooth the application performance => reduce the dimentionality to (100x100)
                                sclaedFrame = cv.resize(
                                    frame1[y:y+h, x:x + w], (100, 100))
                                video_writer.write(sclaedFrame)
                            else:
                                # save the video with original dimentionality
                                sclaedFrame = cv.resize(
                                    frame1, (original_video_width, original_video_height))
                                video_writer.write(sclaedFrame)
                            
                            # save the extracted object in thumbnails as jpg
                            cv.imwrite(os.path.join(r"C:\Users",App.userName, "Smart Video Monitoring\Thumbnails",str(
                                i)+".jpg"), cv.resize(frame1[y:y+h, x:x + w], (100, 100)))
                            i += 1

                # show the video result in popup dialog
                cv.imshow("Processing..", cv.resize(
                    frame1, (int(original_video_width/2)+100, int(original_video_width/2))))
                # skip two frames to reduce complexity of video
                cap.read()
                cap.read()
                frame1 = frame2
                _, frame2 = cap.read()

                # quit the motion detection process when click (q)
                if cv.waitKey(10) & 0xFF == ord('q'):
                    # clear resorces
                    video_writer.release()
                    cap.release()
                    cv.destroyAllWindows()
                    # ignor video if extract less than 20 frames
                    if i <= 20:
                        # remove video from Cache directory
                        os.remove(out)
                        path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                        # remove frames from Thumbnails directory
                        for files in os.listdir(path):
                            os.remove(os.path.join(path, files))
                        # return null
                        return 0
                    # return the resul video    
                    return out

                # clear resources when there is no next frame
                if np.any(frame2) == None:
                    video_writer.release()
                    cap.release()
                    cv.destroyAllWindows()
                    # ignor video if extract less than 20 frames
                    if i <= 20:
                        # remove video from Cache directory
                        os.remove(out)
                        path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                        # remove frames from Thumbnails directory
                        for files in os.listdir(path):
                            os.remove(os.path.join(path, files))
                        # return null
                        return 0
                    # return the resul video    
                    return out

        # object recognition process    
        def predictObject(self):
            self.helpLabel.configure(text= "Progress .......")
            path = 'C:/Users/Motwkel/Downloads/my videos/TkInter/(97%) Mode summary.h5'
            # load our saved model
            model = keras.models.load_model(path)
            test_data = []

            DATADIR = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
            # iterate over each extracted frame from motion detection process 
            for img in tqdm(os.listdir(DATADIR)):
                try:
                    img_array = cv.imread(os.path.join(
                        DATADIR, img))  
                    # save it in array   
                    test_data.append([img_array])  
                except Exception as e:  
                    pass

            # reshape the images to meet the model requirments
            data = np.array(test_data).reshape(-1, 100, 100, 3)

            # predict the objects
            prediction = model.predict(data)
            data = data.squeeze()
            car = 0
            obj = 0
            # calculate the number of each class to average the final result
            for i in range(0, len(data)):
                # get the max predicting probability of the object
                i = np.argmax(prediction[i])
                if i == 1:
                    car += 1
                else:
                    obj += 1
            #print('car: ', car, 'obj: ', obj)
            
            src= os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Cache')
            path= str(os.listdir(src)[0]).split('Cache')[-1]
            if len(os.listdir(src)) != 0:
                src= os.path.join(src, path)
                # motion recognized as cars
                if obj >= car:
                    des= os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Objects', path)
                    messagebox.showinfo("Successfull ✔", "Objects recognized as humans or animals")
                    # move video to objects directory
                    shutil.move(src, des)
                    # setup state of views
                    self.vid_player.load(des)
                    self.vid_player.play()
                # motion recognized as humans-animals
                else:
                    des= os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Cars', path)
                    messagebox.showinfo("Successfull ✔", "Objects recognized as Cars")
                    # move video to cars directory
                    shutil.move(src, des)
                    # setup state of views
                    self.vid_player.load(des)
                    self.vid_player.play()

        # control what is done when clicking live switch button
        def liveOrLocalTrigger():
            checkDirectory()
            # live video logic
            if liveOrLocal.get() == 'live':
                # setup state of views
                self.play_pause_btn.configure(state=customtkinter.DISABLED)
                self.open_file_button.configure(state=customtkinter.DISABLED)
                self.vid_player.stop()
                path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                for files in os.listdir(path):
                    # clear thumbnails directory
                    os.remove(os.path.join(path, files))
                # capture a live video and analyze it from pc camera if (0), or external camera if (1)
                out = videoAnalysis(1)
                # if not empty
                if out:
                    # setup state of views
                    self.play_pause_btn.configure(text='Pause')
                    self.play_pause_btn.configure(state=customtkinter.NORMAL)
                    self.open_file_button.configure(state=customtkinter.NORMAL)
                    self.vid_player.load(out)
                    # make prediction
                    self.helpLabel.configure(text= "Progress .......")
                    # run the predication (object recognition) process
                    prdictWithThread(self)
                    self.helpLabel.configure(text= "")
                else:
                    messagebox.showinfo("Successfull ✔", "Not recognize a lot of Motion")

            # local video logic
            else:
                # open windows explorer dialog to choose the video
                file_path = filedialog.askopenfilename()
                # if not empty
                if file_path:
                    # setup state of views
                    self.play_pause_btn.configure(state=customtkinter.NORMAL)
                    self.open_file_button.configure(state=customtkinter.NORMAL)
                    path = os.path.join(r'C:\Users', App.userName, 'Smart Video Monitoring\Thumbnails\\')
                    for files in os.listdir(path):
                        # clear thumbnails directory
                        os.remove(os.path.join(path, files))
                    # analysis the video (motion detection process)
                    out = videoAnalysis(file_path)
                    # if not empty
                    if out:
                        # setup state of views
                        self.play_pause_btn.configure(text='Pause')
                        self.vid_player.load(out)
                        self.helpLabel.configure(text= "Progress .......")
                        # make prediction (object recognition process)
                        prdictWithThread(self)
                        self.helpLabel.configure(text= "")
                    else:
                        messagebox.showinfo(
                            "Successfull ✔", "Not recognize a lot of Motion")
                # when no file is choosen
                else:
                    messagebox.showerror("Error ❌", "No File!")
                    liveOrLocal.set('live')
                    self.play_pause_btn.configure(state=customtkinter.DISABLED)
        
        # change theme of the application
        def change_appearance_mode(self, new_appearance_mode):
            customtkinter.set_appearance_mode(new_appearance_mode)

        # close the application on clicking close
        def on_closing(self, event=0):
            self.destroy()

# _____________________________________ UI CODE _____________________________________
        # check if directories exist
        checkDirectory()

        # ============ create three frames ============
        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # left frame
        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 corner_radius=12)
        self.frame_left.grid(row=0, column=0, sticky='ns', padx=5, pady=5)

        # right frame
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky='news', padx=5, pady=2)

        # bottom frame
        self.frame_bottom = customtkinter.CTkFrame(master=self)
        self.frame_bottom.grid(row=1, column=0, columnspan=8, sticky='we', padx=5, pady=5)
        
        # ============ bottom frame View ============

        self.helpLabel = customtkinter.CTkLabel(self.frame_bottom, text="")
        self.helpLabel.grid(row=0,  column=3, ipadx=5)
        
        # ============ left frame Views ============

        # configure grid layout (1x11)
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(0, minsize=10)
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)
        # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)

        self.option_label = customtkinter.CTkLabel(master=self.frame_left,
                                                   text="Dashboard",
                                                   text_font=("Roboto Medium", -18))  # font name and size in px
        self.option_label.grid(row=0, column=0, pady=10, padx=10)

        displayMotion = tk.StringVar()
        self.display_motion_checkbox = customtkinter.CTkCheckBox(master=self.frame_left,
                                                                 text="Display motion",
                                                                 variable=displayMotion,
                                                                 onvalue="display",
                                                                 offvalue="not_display",
                                                                 text_font=(
                                                                     "Roboto Medium", -14))
        self.display_motion_checkbox.grid(
            row=1, column=0, pady=10, padx=20, sticky="w")

        self.display_motion_checkbox.bind("<Enter>", enterDisplay)
        self.display_motion_checkbox.bind("<Leave>", outOf)

        zoomAtObject = tk.StringVar()
        self.zoom_at_object_checkbox = customtkinter.CTkCheckBox(master=self.frame_left,
                                                                 text="Zoom at object",
                                                                 variable=zoomAtObject,
                                                                 onvalue="zoom",
                                                                 offvalue="not_zoom",
                                                                 text_font=(
                                                                     "Roboto Medium", -14))                                                                 
        self.zoom_at_object_checkbox.grid(
            row=2, column=0, pady=10, padx=20, sticky="w")

        self.zoom_at_object_checkbox.bind("<Enter>", enterZoom)
        self.zoom_at_object_checkbox.bind("<Leave>", outOf)

        self.div_label = customtkinter.CTkLabel(master=self.frame_left,
                                                text="__________________",
                                                text_font=("Roboto Medium", -14))  # font name and size in px
        self.div_label.grid(row=3, column=0)

        # Stream or not?
        liveOrLocal = tk.StringVar()
        self.live_local_switch = customtkinter.CTkSwitch(master=self.frame_left,
                                                         text="Live",
                                                         variable=liveOrLocal,
                                                         onvalue="live",
                                                         offvalue="local",
                                                         text_font=(
                                                             "Roboto Medium", -16),
                                                         command=liveOrLocalTrigger)
        self.live_local_switch.grid(
            row=4, column=0, padx=25, ipadx=10, pady=10, sticky='w')

        self.live_local_switch.bind("<Enter>", enterLive)
        self.live_local_switch.bind("<Leave>", outOf)

        Help= tk.StringVar()
        self.help_switch = customtkinter.CTkSwitch(master=self.frame_left,
                                                   text="Help",
                                                 variable=Help,
                                                    onvalue="help",
                                                    offvalue="not_help",
                                                    text_font=(
                                                    "Roboto Medium", -16))
        self.help_switch.grid(row=5, column=0, padx=25, ipadx=10, pady=10, sticky='nw')

        self.help_switch.bind("<Enter>", enterHelp)
        self.help_switch.bind("<Leave>", outOf)

        self.label_mode = customtkinter.CTkLabel(
            master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=9, column=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=[
                                                            "Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ right frame Views ============

        self.vid_player = TkinterVideo(scaled=True, master=self.frame_right)
        self.vid_player.place(relx=0.0, rely=0.0,
                              relwidth=1.0, relheight=0.85, anchor='nw')

        self.play_pause_btn = customtkinter.CTkButton(
            self.frame_right, text="Pause", command=play_pause)
        self.play_pause_btn.place(
            relx=0.5, rely=0.96, anchor='center', relwidth=0.1)

        self.skip_plus_5sec = customtkinter.CTkButton(
            self.frame_right, text="<<", command=lambda: skip(-5))
        self.skip_plus_5sec.place(
            relx=0.375, rely=0.96, anchor='w', relwidth=0.07)

        self.skip_plus_5sec = customtkinter.CTkButton(
            self.frame_right, text=">>", command=lambda: skip(5))
        self.skip_plus_5sec.place(
            relx=0.626, rely=0.96, anchor='e', relwidth=0.07)

        self.start_time = customtkinter.CTkLabel(
            self.frame_right, text=str(datetime.timedelta(seconds=0)))
        self.start_time.place(relx=0.0, rely=0.88,
                              anchor='w', relwidth=0.1, relheight=0.02)

        open_file_photo = ImageTk.PhotoImage(Image.open(
            'C:/Users/Motwkel/Downloads/my videos/TkInter/src/add-folder.png').resize((18, 18)))
        show_file_photo = ImageTk.PhotoImage(Image.open(
            'C:/Users/Motwkel/Downloads/my videos/TkInter/src/show-files.png').resize((25, 25)))

        self.open_file_button = customtkinter.CTkButton(
            self.frame_right, text="", image=open_file_photo, command=openFile)
        self.open_file_button.place(
            relx=0.95, rely=0.96, anchor='center', relwidth=0.05)

        self.show_file_button = customtkinter.CTkButton(
            self.frame_right, text="", image=show_file_photo, command=showFile)
        self.show_file_button.place(
            relx=0.05, rely=0.96, anchor='center', relwidth=0.06, relheight=0.055)

        progress_value = tk.IntVar(self.frame_right)

        self.progress_slider = tk.Scale(self.frame_right, border=0, highlightbackground="#0E0E0E", background="#1F69A6",
                                        showvalue=0, from_=0, to=0,  variable=progress_value, orient="horizontal", command=seek)
        # progress_slider.bind("<ButtonRelease-1>", seek)
        self.progress_slider.place(
            relx=0.1, rely=0.88, relwidth=0.8, anchor='w')

        self.end_time = customtkinter.CTkLabel(
            self.frame_right, text=str(datetime.timedelta(seconds=0)))
        self.end_time.place(relx=1.0, rely=0.88, anchor='e',
                            relwidth=0.1, relheight=0.02)

        # Bind video player actions
        self.vid_player.bind("<<Duration>>", update_duration)
        self.vid_player.bind("<<SecondChanged>>", update_scale)
        self.vid_player.bind("<<Ended>>", video_ended)
        self.vid_player.bind("<Enter>", enterVideo)
        self.vid_player.bind("<Leave>", outOf)

        # set default values of views
        self.optionmenu_1.set("Dark")
        self.live_local_switch.deselect()
        self.play_pause_btn.configure(state=customtkinter.DISABLED)
        zoomAtObject.set('not_zoom')
        displayMotion.set('not_display')


if __name__ == "__main__":
    app = App()
    app.mainloop()
