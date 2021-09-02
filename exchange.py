import os
from tkinter import * 
from  tkinter import  _setit
import requests
import json
from datetime import datetime

history_file_name = 'history.json'

def get_currencies():
    url = 'https://api.exchangerate.host/symbols'
    response = requests.get(url)
    data = response.json()
    return list(data["symbols"].keys())

def exchange():
    s_amount = start_amount.get()
    try:
        float(s_amount)
    except(ValueError):
        dest_currency_output["text"] = "Numbers only!"
        return

    s_curreny = start_currency.get()
    d_currency = dest_currency.get()
    url = f'https://api.exchangerate.host/convert?from={s_curreny}&to={d_currency}&amount={s_amount}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        dest_currency_output["text"] = round(data["result"],2)
        
        history = read_json()
        history.update(new_history(data))
        write_json(history)
        update_history_list()
        update_search_date_options()
    else:
        dest_currency_output["text"] = "Something went wrong."

def new_history(data):
    history = { 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"): { #in a real project this should be utcnow
            "from":data["query"]["from"], 
            "to":data["query"]["to"],
            "s_amount": data["query"]["amount"],
            "d_amount": data["result"]
            }}
    return history

def write_json(result):
    with open( history_file_name, 'w') as f:
        json.dump(result, f, indent = 2)    

def read_json():
    file = os.path.join(os.getcwd(), history_file_name)
    if os.path.exists(file) and os.stat(file).st_size > 0:
        f = open(history_file_name)
        return json.load(f)
    else:
        return {}

def get_starter_and_dest_currencies():
    starter_currencies = currencies.copy()
    dest_currencies = currencies.copy()
    
    exchanges = read_json()
    if(exchanges):
        last_five = sorted(exchanges.keys(), reverse= True)[:5]
        for date in last_five:
            s_currency = exchanges[date]['from']
            d_currency = exchanges[date]['to']

            starter_currencies.remove(s_currency)
            starter_currencies.insert(last_five.index(date),s_currency)

            dest_currencies.remove(d_currency)
            dest_currencies.insert(last_five.index(date),d_currency)
        
    return starter_currencies, dest_currencies

def get_history():
    exchanges = read_json()
    if(exchanges):
        history = []
        for date in exchanges:
            history.append(
                f"{date}: {exchanges[date]['s_amount']} {exchanges[date]['from']} to {round(exchanges[date]['d_amount'], 2)} {exchanges[date]['to']}")
        return history
    else:
        return []

def search_by_date():
    exchanges = read_json()
    if(exchanges):
        history_list.delete(0,END)
        i = 0
        for date in exchanges:
            if datetime.strptime(search_by_date_str.get(), "%Y-%m-%d").date() == datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date():
                history_list.insert(i+1, f"{date}: {exchanges[date]['s_amount']} {exchanges[date]['from']} to {round(exchanges[date]['d_amount'], 2)} {exchanges[date]['to']}")
    
def search_by_currency(currency):
    exchanges = read_json()
    if(exchanges):
        history_list.delete(0,END)
        i = 0
        for date in exchanges:
            if currency in exchanges[date]['from'] or currency in exchanges[date]['to']:
                history_list.insert(i+1, f"{date}: {exchanges[date]['s_amount']} {exchanges[date]['from']} to {round(exchanges[date]['d_amount'], 2)} {exchanges[date]['to']}")

def update_history_list():
    history_list.delete(0, END)
    history = get_history()
    for h in history:
        history_list.insert(history.index(h), h)
        
def get_dates():
    exchanges = read_json()
    if(exchanges):
        dates = []
        tmp_date = datetime(1970,1,1)
        for date in exchanges:
            date_from_data = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
            if(date_from_data != tmp_date):
                dates.append(date_from_data)
            tmp_date = date_from_data
        return dates
    else:
        return ["No history yet"]

def update_search_date_options():
    search_by_date_options["menu"].delete(0, END)
    dates = get_dates()
    search_by_date_str.set(dates[0])
    for d in dates:
        search_by_date_options["menu"].add_command(label=d, command=_setit(search_by_date_str,d) )

currencies = get_currencies()

window = Tk()
window.geometry("600x300")
window.title("Exchange rate")

start_amount = Entry(window, width=10)
start_amount.pack(side=LEFT, anchor='n')

starter_currencies, dest_currencies = get_starter_and_dest_currencies()
start_currency = StringVar(master=window)
start_currency.set(starter_currencies[0])

start_currency_selector = OptionMenu(window, start_currency, *starter_currencies)
start_currency_selector.pack(side=LEFT, anchor='n')

button = Button(text="To", width=4, height=1, command= exchange )
button.pack(side=LEFT, anchor='n')

dest_currency = StringVar(master=window)
dest_currency.set(dest_currencies[1])

dest_currency_selector = OptionMenu(window, dest_currency, *dest_currencies)
dest_currency_selector.pack(side=LEFT, anchor='n')

dest_currency_output = Label(window, width=10)
dest_currency_output.pack(side=LEFT, anchor='n')

search_by_date_lst = get_dates()
search_by_date_str = StringVar(master=window)
search_by_date_str.set(search_by_date_lst[0])
search_by_date_options = OptionMenu(window, search_by_date_str, *search_by_date_lst)
search_by_date_options.pack()

search_by_date_button = Button(text="Search by date", width=15, height=1, command= search_by_date )
search_by_date_button.pack()

search_by_currency_str = StringVar(master=window)
search_by_currency_str.set(currencies[0])
search_by_currency_options = OptionMenu(window, search_by_currency_str, *currencies, command=search_by_currency)
search_by_currency_options.pack()

reset_hitory_button = Button(text="Reset history data", width=15, height=1, command= update_history_list )
reset_hitory_button.pack()

history = get_history()
history_list = Listbox(window, width= 100)
history_list.pack(side=RIGHT, anchor='n')
if(history):
    for h in history:
        history_list.insert(history.index(h), h)

window.mainloop()