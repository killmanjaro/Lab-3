import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
from tkinter import *
import sqlite3
# Alyssa Goldgeisser
# Lab 3
# Module 3
# lab3front

def fetch_data_from_db():
    conn = sqlite3.connect('travel_data.db')
    cur = conn.cursor()
    cur.execute('''
    SELECT d.rank, d.destination, d.finished_text, d.destination_link, m.month_name
    FROM destinations d
    JOIN months m ON d.month_id = m.id
    ''')
    data = cur.fetchall()
    conn.close()
    return data

class MainWin(tk.Tk) :
    def __init__(self, data) :
        ''' constructor for mainWin class, takes data which is a list of disctionaries from json file'''
        super().__init__() 
        self.title("Travel")
        self.data = data
        
        self.title_label = tk.Label(self, text="Best Places to Travel in 2024", font='Helvetica, 10')
        self.title_label.grid(row=0, column=2, padx=5, pady=10)

        self.label = tk.Label(self, text="Search by:",font='Helvetica, 10', fg='blue')
        self.label.grid(row=1, column=0, pady=5, padx=5)
        
        self.btn_place = tk.Button(self, text="Name", font='Helvetica, 10', command=self.go_name_of_place, bg='cyan', fg='blue')
        self.btn_place.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_month = tk.Button(self, text="Month", font='Helvetica, 10', command=self.go_month_of_year, bg='cyan', fg='blue')
        self.btn_month.grid(row=1, column=2, padx=5, pady=5)
        
        self.btn_rank = tk.Button(self, text="Rank", font='Helvetica, 10', command=self.go_ranking, bg='cyan', fg='blue')
        self.btn_rank.grid(row=1, column=3, padx=5, pady=5)
    
        
    def go_name_of_place(self):
        ''' function that creates DialogWin class upon command to use Name'''
        first_letters = sorted(list(set(item[4][0] for item in self.data)))
        DialogWin(self, "letter", first_letters)

    def go_month_of_year(self):
        ''' function that creates DialogWin class upon command to use month'''
        month_order = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        
        # I understand that maybe this is considered hardcoded, but I just wanted it to be in order, but I
        # get the months from my data. if this is not allowed, please ignore.
        
        months = sorted(list(set(item[4] for item in self.data)), key=lambda month: month_order.index(month))
        DialogWin(self, "month", months )

    def go_ranking(self):
        ''' function that creates DialogWin class upon command to use rank'''
        ranks = sorted(set(item[0] for item in self.data), key=int)
        DialogWin(self, "rank", ranks)

class DialogWin(tk.Toplevel):
    def __init__(self, parent, search_type, options) :
        ''' constructor for dialog window class, takes search_type and options and uses them generally to create option window'''
        super().__init__(parent) 
        self.grab_set()
        self.label = tk.Label(self, text=f'Click on a {search_type} to select').grid()
        self.search_type = search_type
        self.data = data

        self.selected_option = tk.StringVar(value=options[0])
        self.selected_option.trace_add('write', self.go_result)

        for idx, option in enumerate(options):
            radio_btn = ttk.Radiobutton(self, text=option, variable=self.selected_option, value=option)
            radio_btn.grid(row=idx + 1, column=0, padx=20, sticky="w")

    def go_result(self, *args):
        ''' function that when selected option is pressed, gets the option and creates a result window'''
        selected_value = self.selected_option.get()
        self.destroy()
        ResultWin(selected_value, self.search_type, self.data)

class ResultWin(tk.Toplevel):
    def __init__(self, result, search_type, data) :
        ''' constructor for result window class that creates a scrollbar with listbox for all the results'''
        super().__init__() 
        self.data = data
        self.search_type = search_type

        key_mapping = {
            "letter": 1,
            "month": 4,
            "rank": 0
        }


        if search_type == "letter":
            filtered_data = [item for item in data if item[1][0].upper() == result]
        else:  
            search_key = key_mapping.get(search_type)
            filtered_data = [item for item in data if item[search_key] == result]

    
        description = {
                "letter": f"Destinations starting with {result}",
                "month": f"Top destinations for {result} in ranking order",
                "rank": f"Destinations with rank {result} for the listed months"
            }
        
        label = tk.Label(self, text=description[search_type], font=("Helvetica", 12))
        label.grid(row=0, column=0, padx=10, pady=10)

        self.listbox = tk.Listbox(self, height=10, width=50)
        scrollbar = tk.Scrollbar(self, orient='vertical', command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)

        unique_destinations = [] # temporary container to not have duplicate destinations
        if search_type == "rank":
            for item in filtered_data: 
                    destination_info = f"{item[1]}: {item[4]}"
                    if item[1] not in unique_destinations:
                        self.listbox.insert(tk.END, destination_info)
                        unique_destinations.append(item[1])

        elif search_type == 'month':
            for item in filtered_data:
                destination_info = f"{item[0]} {item[1]}"
                if item[1] not in unique_destinations:
                    self.listbox.insert(tk.END, destination_info)
                    unique_destinations.append(item[1])

        else:
            for item in filtered_data:
                destination_info = f"{item[0]} {item[1]}"
                if item[1] not in unique_destinations:
                    self.listbox.insert(tk.END, destination_info)
                    unique_destinations.append(item[1])
    
        self.listbox.grid(row=1, column=0, padx=10, pady=10)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self.listbox.bind("<<ListboxSelect>>", self.show_destination_info)

    def show_destination_info(self, *args):
        ''' method that calls display window class, passing in rank and destination that are found from data'''
        if self.search_type == 'rank':
            my_destination, my_month = self.listbox.get(self.listbox.curselection()).split(': ', 1)
            for entry in self.data:
                if entry[1] == my_destination and entry[4] == my_month:
                    my_description = entry[2]
                    my_url = entry[3]
        

        else: 
            my_rank, my_destination = self.listbox.get(self.listbox.curselection()).split(' ', 1)
            print(my_rank)
            print(my_destination)
            for entry in self.data:
                if entry[1] == my_destination and entry[0] == my_rank:
                    my_description = entry[2]
                    my_url = entry[3]
        
        DisplayWin(my_destination, my_description, my_url)
        

class DisplayWin(tk.Toplevel):
    def __init__(self, destination_name, description, url):
        ''' constructor for display window class, shows the destination name, description, and url if needed'''
        super().__init__() 
        self.title(destination_name)
        self.configure(bg = 'blue')
        
        name_label = tk.Label(self, text=destination_name, font=("Helvetica", 14, "bold"))
        name_label.grid(row=0, column=0, padx=10, pady=10)

        desc_text = tk.Label(self, text=description, wraplength=300, justify="left")
        desc_text.grid(row=1, column=0, padx=10, pady=10)

        if url != 'no url':
            url_label = tk.Label(self, text=f"See {destination_name} details", bg="cyan", cursor="hand2")
            url_label.grid(row=2, column=0, pady=5)
            url_label.bind("<Button-1>", lambda event: self.open_url(url))
        
    def open_url(self, url):
        ''' opens url in browser'''
        webbrowser.open(url)

data = fetch_data_from_db()
app = MainWin(data)
app.mainloop()