
import tkinter as tk
from tkinter import ttk
from unittest import result
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import tkcalendar as tkcal 
from datetime import datetime
import tkinter.font as tk_font
import database as db
import csv


root = tk.Tk()
root.title("Report Wizard")

FONT = tk_font.Font(family='Segoe UI',
              size=12,
              weight='bold',
              underline=0,
              overstrike=0)


status_var = tk.StringVar(root)
status_lab = tk.Label(root, textvariable=status_var, font=FONT)
status_lab.pack()

# -----------------------------------------------------------------------

style = ttk.Style()
style.configure("Treeview", font=('Britannic', 13, 'bold'), columnwidth=5)
style.configure("Treeview.Heading", font=('Britannic' ,14, 'bold'))

# Tkinter Bug Work Around
if root.getvar('tk_patchLevel')=='8.6.9': #and OS_Name=='nt':
    def fixed_map(option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.
        #
        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]
    style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

# -----------------------------------------------------------------------

entry_frame = tk.Frame(root)
entry_frame.pack(padx=10, pady=5)

cal_lab = tk.Label(entry_frame, text='Date: ', font=FONT)
cal = tkcal.DateEntry(entry_frame, selectmode='day', locale='en_IN')
cal_lab.grid(row=0, column=0, padx=20)
cal.grid(row=1, column=0, padx=20)

capital_lab = tk.Label(entry_frame, text="Capital", font=FONT)
capital_lab.grid(row=0, column=1, padx=10, pady=5)
capital_var = tk.StringVar(root, value="0")
capital_entry = ttk.Entry(entry_frame, textvariable= capital_var, width=10)
capital_entry.grid(row=1, column=1, padx=10, pady=5)
capital_var.set("0")

'''capital_btn = ttk.Button(entry_frame, text="Add Capital", command=add_capital).grid(column=2, row=0, rowspan=2, padx=10)

daily_cal_lab = tk.Label(entry_frame, text='Date', font=FONT)
daily_cal = tkcal.DateEntry(entry_frame, selectmode='day', locale='en_IN')
daily_cal_lab.grid(row=0, column=3, padx=20)
daily_cal.grid(row=1, column=3, padx=20)'''

profit_lab = tk.Label(entry_frame, text="Profit", font=FONT)
profit_lab.grid(row=0, column=2, padx=10, pady=5)
profit_var = tk.StringVar(root)
profit_entry = ttk.Entry(entry_frame, textvariable= profit_var, width=10)
profit_entry.grid(row=1, column=2, padx=10, pady=5)

def save_data():
    date = cal.get_date().strftime('%Y%m%d')
    profit = float(profit_var.get())
    capital = float(capital_var.get())
    if not db.connect(db.valid_date, date):
        print("ERROR")
        return
    last_data = db.connect(db.fetch_last_row)
    if last_data:
        opening = last_data[-1]        
    else:
        opening = 0
    closing = opening + profit + capital

    db.connect(db.add_record, date, opening, profit, closing, capital) 
    show_query(plot=False)


save_btn = ttk.Button(entry_frame, text="Save", command=save_data).grid(column=3, row=0, rowspan=2, padx=10)

query_frame_top = tk.Frame(root)
query_frame_top.pack()

query_lab = tk.Label(query_frame_top, text="Query", font=FONT)
query_lab.pack(pady=5)

query_frame = tk.Frame(query_frame_top)
query_frame.pack()

from_cal_lab = tk.Label(query_frame, text='From: ', font=FONT)
from_cal = tkcal.DateEntry(query_frame, selectmode='day', locale='en_IN')
from_cal_lab.grid(row=0, column=0, padx=20)
from_cal.grid(row=1, column=0, padx=20)

to_cal_lab = tk.Label(query_frame, text='To: ', font=FONT)
to_cal = tkcal.DateEntry(query_frame, selectmode='day', locale='en_IN')
to_cal_lab.grid(row=0, column=1, padx=20)
to_cal.grid(row=1, column=1, padx=20)

occur_lab = tk.Label(query_frame, text="Occurance", font=FONT)
occur_lab.grid(row=0, column=2, padx=10, pady=5)
occur_var = tk.StringVar(root)
occur_entry = ttk.Entry(query_frame, textvariable= occur_var, width=10)
occur_entry.grid(row=1, column=2, padx=10, pady=5)

def plot_graph(start, end):
    try:
        plt.close()
    except Exception as e:
        print(e)

    data = db.connect(db.get_data, start, end)
    start_lab = datetime.strptime(data[0][0], '%Y%m%d').strftime('%d-%m-%y')
    end_lab = datetime.strptime(data[-1][0], '%Y%m%d').strftime('%d-%m-%y') 
    x = [datetime.strptime(i[0], '%Y%m%d').strftime('%d/%m') for i in data]
    y = [i[-1] for i in data]
    for i, v in enumerate(y):
        plt.text(i, v+5, "%d" %v, ha="center")
    plt.plot(x, y)

    opening = data[0][1]
    if opening == 0.0:
        opening = data[0][3]
    with open("config.txt") as f:
        percents = [float(x.strip()) / 100 for x in f.readlines()]
        for i , percent in enumerate(percents):
            target = opening + (percent * opening)
            plt.axhline(target)
            plt.text(len(y) - 1, target+5, "%d" %target, ha="center")

    plt.xlabel('Date')
    plt.ylabel('Closing in Rs.')
    plt.title(f'Daily Closing between {start_lab} and {end_lab}')
    plt.show()

def calc_consec_dates(data):
    '''consec_data = []
    count = 0
    start = None
    for i in range(1, len(data)):
        if (data[i] - data[i - 1]).days == 1:
            count += 1
            if not start:
                start = data[i]
        else:
            if count > 0:
                consec_data.append((count, start, data[i - 1]))
                start = None
                count = 0
        
    result = consec_data.sort(key= lambda x:x[2], reverse=True)[0]'''
    
    return result

def consec_wins_losses(data):
    '''wins = [datetime.strptime(x[0], '%Y%m%d') for x in data if x[2] > 0.0]
    losses = [datetime.strptime(x[0], '%Y%m%d') for x in data if x[2] < 0.0]'''

    consec_wins = []
    profit = 0
    consec_wins_amt = []
    consec_losses = []
    consec_losses_amt = []
    count = 0
    results = [x[2] for x in data]
    print(results)
    
    for i in results:
        if i > 0.0:
            count += 1
            profit += i

        else:
            if count > 1:
                consec_wins.append(count)
                consec_wins_amt.append(profit)
            count = 0
            profit = 0

    if len(consec_wins) > 0 and max(consec_wins) > count:
        max_consec_wins = max(consec_wins)
        max_consec_wins_amt = consec_wins_amt[consec_wins.index(max(consec_wins))]
    else:
        max_consec_wins = count
        max_consec_wins_amt = profit
    

    count = 0
    loss = 0
    for i in results:
        if i < 0.0:
            print(i)
            count += 1
            loss += i
        else:
            if count > 1:
                consec_losses.append(count)
                consec_losses_amt.append(loss)
            count = 0
            loss = 0

    if len(consec_losses) > 0 and max(consec_losses) > count:    
        max_consec_losses = max(consec_losses)
        max_consec_loss_amt = consec_losses_amt[consec_losses.index(max(consec_losses))]
    else:
        max_consec_losses = count
        max_consec_loss_amt = loss
    occurance = occur_var.get().strip()
    win_occur = 0
    loss_occur = 0
    if occurance:
        if len(consec_wins) > 0:
            win_occur = consec_wins.count(int(occurance))
        
    return max_consec_wins, max_consec_losses, max_consec_wins_amt, max_consec_loss_amt
    
    

def show_query(plot=True):
    from_date = from_cal.get_date().strftime('%Y%m%d')
    to_date = to_cal.get_date().strftime('%Y%m%d')
    for i in tv.get_children():
        tv.delete(i)
    data = db.connect(db.get_data, from_date, to_date)
    wins, losses, wins_amt, losses_amt = consec_wins_losses(data)
    initial_balance = data[0][1] + data[0][3]
    final_balance = data[-1][-1]
    growth = round(((final_balance - initial_balance) / initial_balance) * 100, 2)
    growth_var.set(f'Growth: {growth} %')
    wins_var.set(f'Max Wins: {wins} Times')
    losses_var.set(f'Max Losses: {losses}')
    wins_amt_var.set(f'Amount: {wins_amt}')
    losses_amt_var.set(f'Amount: {losses_amt}')

    for i,row in enumerate(data):
        formatted_date = datetime.strptime(row[0], '%Y%m%d').strftime('%d-%m-%Y')
        tv.insert(parent='', index=i, iid=i, values=(formatted_date, *row[1:]))
    if plot:
        plot_graph(from_date, to_date)
    capital_var.set('0')
    

query_btn = ttk.Button(query_frame, text="Show", command=show_query).grid(column=3, row=0, rowspan=2, padx=10)

stats_frame = tk.Frame(root)
stats_frame.pack()
growth_var = tk.StringVar(root)
growth_lab = ttk.Label(stats_frame, textvariable=growth_var, font=FONT)
growth_lab.grid(row=0, column=0, rowspan=2, pady=5)

wins_var = tk.StringVar(root)
wins_lab = tk.Label(stats_frame, foreground="green", textvariable=wins_var, font=FONT)
wins_lab.grid(row=0, column=1, pady=5, padx=10)

wins_amt_var = tk.StringVar(root)
wins_amt_lab = tk.Label(stats_frame, foreground="green", textvariable=wins_amt_var, font=FONT)
wins_amt_lab.grid(row=1, column=1, pady=5, padx=10)

losses_var = tk.StringVar(root)
losses_lab = tk.Label(stats_frame, foreground="red", textvariable=losses_var, font=FONT)
losses_lab.grid(row=0, column=2, pady=5, padx=10)

losses_amt_var = tk.StringVar(root)
losses_amt_lab = tk.Label(stats_frame, foreground="red", textvariable=losses_amt_var, font=FONT)
losses_amt_lab.grid(row=1, column=2, pady=5, padx=10)

win_occurance_var = tk.StringVar(root)
win_occurance_lab = ttk.Label(stats_frame, textvariable=win_occurance_var, font=FONT)
win_occurance_lab.grid(row=0, column=3, pady=5)

loss_occurance_var = tk.StringVar(root)
loss_occurance_lab = ttk.Label(stats_frame, textvariable=loss_occurance_var, font=FONT)
loss_occurance_lab.grid(row=1, column=3, pady=5)

result_frame = tk.Frame(root)
result_frame.pack()

tv = ttk.Treeview(
    result_frame, 
    columns=(1, 2, 3, 4, 5), 
    show='headings', 
    height=10
)
tv.grid(row=0, column=0, pady=10)

tv.heading(1, text='Day')
tv.column(1, minwidth=10, width=100) 
tv.heading(2, text='Opening')
tv.column(2, minwidth=10, width=100)
tv.heading(3, text='Result')
tv.column(3, minwidth=10, width=100)
tv.heading(4, text='Capital Add.')    
tv.column(4, minwidth=10, width=100)
tv.heading(5, text='Closing')    
tv.column(5, minwidth=10, width=100)

def export_data():
    
    with open('data.csv', 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(['Date', 'Opening', 'Result', 'Added Capital', 'Closing'])
        for line in tv.get_children():
            csv_writer.writerow(tv.item(line)['values'])

export_button = ttk.Button(root, text="Export", command=export_data).pack()



root.mainloop()