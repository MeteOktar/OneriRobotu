from tkinter import *
from tkinter import ttk
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

#****************************************************************************************
#---------------------------- [COLLECTING INPUT DATA] ----------------------------
def submit_data():
    input_1 = first_user_input_entry.get()
    input_2 = second_user_input_entry.get()
    input_3 = third_user_input_entry.get()
    input_4 = fourth_user_input_entry.get()
    
    rating_1 = rating_1_combobox.get()
    rating_2 = rating_2_combobox.get()
    rating_3 = rating_3_combobox.get()
    rating_4 = rating_4_combobox.get()
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#------------------------------ [CREATING WINDOW] ------------------------------
window = Tk()
window.title("SUGGESTOR UI")
window.resizable(False, False)
#****************************************************************************************
#====================================================================================================
#------------------------ FOR MACBOOK --------------------------|
window.attributes('-topmost', True)  # Pencereyi en üste getirir|
#---------------------------------------------------------------|
#====================================================================================================
#****************************************************************************************
#------------------------------ [FRAME GENERATION] ------------------------------ 

frame = Frame(window)
frame.pack()

user_input_frame_1 = LabelFrame(frame, bg="lightpink", text="Input Area 1", bd=0, highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"))
user_input_frame_2 = LabelFrame(frame, bg="lightgreen", text="Input Area 2", bd=0, highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"))
user_input_frame_3 = LabelFrame(frame, bg="lightblue", text="Input Area 3", bd=0, highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"))
user_input_frame_4 = LabelFrame(frame, bg="lightgray", text="Input Area 4", bd=0, highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"))
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#------------------------------- [USER TEXT ENTRY] ------------------------------- 

first_user_input = Label(user_input_frame_1, text="First Input", bg="lightpink", font=("Arial", 12, "bold"))
second_user_input = Label(user_input_frame_2, text="Second Input", bg="lightgreen", font=("Arial", 12, "bold"))
third_user_input = Label(user_input_frame_3, text="Third Input", bg="lightblue", font=("Arial", 12, "bold"))
fourth_user_input = Label(user_input_frame_4, text="Fourth Input", bg="lightgray", font=("Arial", 12, "bold"))

first_user_input_entry = Entry(user_input_frame_1)
second_user_input_entry = Entry(user_input_frame_2)
third_user_input_entry = Entry(user_input_frame_3)
fourth_user_input_entry = Entry(user_input_frame_4)
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#------------------------------ [USER RATING ENTRY] ------------------------------ 

rating_1 = Label(user_input_frame_1, text="Rating-1", bg="lightpink", font=("Arial", 12, "bold"))
rating_2 = Label(user_input_frame_2, text="Rating-2", bg="lightgreen", font=("Arial", 12, "bold"))
rating_3 = Label(user_input_frame_3, text="Rating-3", bg="lightblue", font=("Arial", 12, "bold"))
rating_4 = Label(user_input_frame_4, text="Rating-4", bg="lightgray", font=("Arial", 12, "bold"))

rating_1_combobox = ttk.Combobox(user_input_frame_1, values=[0,1,2,3,4,5])
rating_2_combobox = ttk.Combobox(user_input_frame_2, values=[0,1,2,3,4,5])
rating_3_combobox = ttk.Combobox(user_input_frame_3, values=[0,1,2,3,4,5])
rating_4_combobox = ttk.Combobox(user_input_frame_4, values=[0,1,2,3,4,5])
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#-------------------------------- [SUBMIT BUTTON] -------------------------------- 

submit_button = Button(frame, text="Submit", command=submit_data, font=("Arial", 12, "bold"))
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#----------------------------------- [GRIDS] ----------------------------------- 

user_input_frame_1.grid(row=0, column=0, padx=20, pady=10)
user_input_frame_2.grid(row=1, column=0, padx=20, pady=10)
user_input_frame_3.grid(row=2, column=0, padx=20, pady=10)
user_input_frame_4.grid(row=3, column=0, padx=20, pady=10)

first_user_input.grid(row=0, column=0)
second_user_input.grid(row=0, column=0)
third_user_input.grid(row=0, column=0)
fourth_user_input.grid(row=0, column=0)

first_user_input_entry.grid(row=1, column=0)
second_user_input_entry.grid(row=1, column=0)
third_user_input_entry.grid(row=1, column=0)
fourth_user_input_entry.grid(row=1, column=0)

rating_1.grid(row=0, column=1)
rating_2.grid(row=0, column=1)
rating_3.grid(row=0, column=1)
rating_4.grid(row=0, column=1)

rating_1_combobox.grid(row=1, column=1)
rating_2_combobox.grid(row=1, column=1)
rating_3_combobox.grid(row=1, column=1)
rating_4_combobox.grid(row=1, column=1)

submit_button.grid(row=4, column=0, sticky="news", padx=100, pady=10)
#****************************************************************************************
#====================================================================================================
#****************************************************************************************
#----------------------------------- [PADDING] ----------------------------------- 

for widget in user_input_frame_1.winfo_children():
    widget.grid_configure(padx=10, pady=5)
for widget in user_input_frame_2.winfo_children():
    widget.grid_configure(padx=10, pady=5)
for widget in user_input_frame_3.winfo_children():
    widget.grid_configure(padx=10, pady=5)
for widget in user_input_frame_4.winfo_children():
    widget.grid_configure(padx=10, pady=5)
#****************************************************************************************

window.mainloop()