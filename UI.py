# UI.py
from tkinter import *
from tkinter import ttk
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class UI:
    def __init__(self):
        self.user_data = {}

        # ------------------------------ [CREATING WINDOW] ------------------------------
        self.window = Tk()
        self.window.title("SUGGESTOR UI")
        self.window.resizable(False, False)

        # ------------------------------ [FOR MACBOOK] ------------------------------
        self.window.attributes('-topmost', True)  

        # ------------------------------ [FRAME GENERATION] ------------------------------ 
        self.frame = Frame(self.window)
        self.frame.pack()

        self.user_input_frame_1 = LabelFrame(
            self.frame, bg="lightpink", text="Enter A Film and Rate It", bd=0, 
            highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"), fg="black"
        )
        self.user_input_frame_2 = LabelFrame(
            self.frame, bg="lightgreen", text="Enter A Second Film and Rate It", bd=0, 
            highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"), fg="black"
        )
        self.user_input_frame_3 = LabelFrame(
            self.frame, bg="lightblue", text="Enter A Third Film and Rate It", bd=0, 
            highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"), fg="black"
        )
        self.user_input_frame_4 = LabelFrame(
            self.frame, bg="lightgray", text="Enter A Fourth Film and Rate It", bd=0, 
            highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"), fg="black"
        )
        
        self.user_input_frame_5 = LabelFrame(
            self.frame, bg="gold", text="Enter A Film That You Want Similars to It", bd=0, 
            highlightthickness=0, labelanchor="n", font=("Arial", 12, "bold"), fg="black"
        )

        # ------------------------------ [USER TEXT ENTRY] ------------------------------
        self.first_user_input = Label(self.user_input_frame_1, 
                                      text="First Input", bg="lightpink", 
                                      font=("Arial", 12, "bold"), fg="black")
        self.first_user_input_entry = Entry(self.user_input_frame_1)

        self.second_user_input = Label(self.user_input_frame_2, 
                                       text="Second Input", bg="lightgreen", 
                                       font=("Arial", 12, "bold"), fg="black")
        self.second_user_input_entry = Entry(self.user_input_frame_2)

        self.third_user_input = Label(self.user_input_frame_3, 
                                      text="Third Input", bg="lightblue", 
                                      font=("Arial", 12, "bold"), fg="black")
        self.third_user_input_entry = Entry(self.user_input_frame_3)

        self.fourth_user_input = Label(self.user_input_frame_4, 
                                       text="Fourth Input", bg="lightgray", 
                                       font=("Arial", 12, "bold"), fg="black")
        self.fourth_user_input_entry = Entry(self.user_input_frame_4)
        
        self.fifth_user_input = Label(self.user_input_frame_5, 
                                       text="Fourth Input", bg="gold", 
                                       font=("Arial", 12, "bold"), fg="black")
        self.fifth_user_input_entry = Entry(self.user_input_frame_5)

        # ------------------------------ [USER RATING ENTRY] ------------------------------
        self.rating_1 = Label(self.user_input_frame_1, 
                              text="Rating-1", bg="lightpink", 
                              font=("Arial", 12, "bold"), fg="black")
        self.rating_1_combobox = ttk.Combobox(self.user_input_frame_1, 
                                              values=[0,1,2,3,4,5])

        self.rating_2 = Label(self.user_input_frame_2, 
                              text="Rating-2", bg="lightgreen", 
                              font=("Arial", 12, "bold"), fg="black")
        self.rating_2_combobox = ttk.Combobox(self.user_input_frame_2, 
                                              values=[0,1,2,3,4,5])

        self.rating_3 = Label(self.user_input_frame_3, 
                              text="Rating-3", bg="lightblue", 
                              font=("Arial", 12, "bold"), fg="black")
        self.rating_3_combobox = ttk.Combobox(self.user_input_frame_3, 
                                              values=[0,1,2,3,4,5])

        self.rating_4 = Label(self.user_input_frame_4, 
                              text="Rating-4", bg="lightgray", 
                              font=("Arial", 12, "bold"), fg="black")
        self.rating_4_combobox = ttk.Combobox(self.user_input_frame_4, 
                                              values=[0,1,2,3,4,5])

        # ------------------------------ [SUBMIT BUTTON] ------------------------------
        self.submit_button = Button(self.frame, text="Submit", 
                                    command=self.submit_data, 
                                    font=("Arial", 12, "bold"))

        # ------------------------------ [GRIDS] ------------------------------
        self.user_input_frame_1.grid(row=0, column=0, padx=20, pady=10)
        self.user_input_frame_2.grid(row=1, column=0, padx=20, pady=10)
        self.user_input_frame_3.grid(row=2, column=0, padx=20, pady=10)
        self.user_input_frame_4.grid(row=3, column=0, padx=20, pady=10)
        self.user_input_frame_5.grid(row=4, column=0, padx=20, pady=10)

        self.first_user_input.grid(row=0, column=0)
        self.first_user_input_entry.grid(row=1, column=0)
        self.rating_1.grid(row=0, column=1)
        self.rating_1_combobox.grid(row=1, column=1)

        self.second_user_input.grid(row=0, column=0)
        self.second_user_input_entry.grid(row=1, column=0)
        self.rating_2.grid(row=0, column=1)
        self.rating_2_combobox.grid(row=1, column=1)

        self.third_user_input.grid(row=0, column=0)
        self.third_user_input_entry.grid(row=1, column=0)
        self.rating_3.grid(row=0, column=1)
        self.rating_3_combobox.grid(row=1, column=1)

        self.fourth_user_input.grid(row=0, column=0)
        self.fourth_user_input_entry.grid(row=1, column=0)
        self.rating_4.grid(row=0, column=1)
        self.rating_4_combobox.grid(row=1, column=1)
        
        self.fifth_user_input.grid(row=0, column=0)
        self.fifth_user_input_entry.grid(row=1, column=0)

        self.submit_button.grid(row=5, column=0, sticky="news", padx=100, pady=10)

        # ------------------------------ [PADDING] ------------------------------
        for widget in self.user_input_frame_1.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        for widget in self.user_input_frame_2.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        for widget in self.user_input_frame_3.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        for widget in self.user_input_frame_4.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        for widget in self.user_input_frame_5.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        # ----------------------------------------------------------------------

    def submit_data(self):
        input_1 = self.first_user_input_entry.get()
        input_2 = self.second_user_input_entry.get()
        input_3 = self.third_user_input_entry.get()
        input_4 = self.fourth_user_input_entry.get()
        input_5 = self.fifth_user_input_entry.get()
        
        rating_1 = self.rating_1_combobox.get()
        rating_2 = self.rating_2_combobox.get()
        rating_3 = self.rating_3_combobox.get()
        rating_4 = self.rating_4_combobox.get()

        self.user_data = {
            "input_1": input_1,
            "input_2": input_2,
            "input_3": input_3,
            "input_4": input_4,
            "input_5": input_5,
            "rating_1": rating_1,
            "rating_2": rating_2,
            "rating_3": rating_3,
            "rating_4": rating_4
        }

        self.window.destroy()


def run_ui():
    app = UI()
    app.window.mainloop()
    return app.user_data