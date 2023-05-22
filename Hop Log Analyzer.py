from tkinter import *
from tkinterdnd2 import *
from collections import OrderedDict

#Takes the raw log and separates it by hop
def extract_hops(log_file):
    hops = {}
    with open(log_file, 'r') as file:
        lines = file.readlines()
        if lines:
            separator = ' '.join(lines[0].split()[-3:])
            current_hop = None
            hop_count = 1
            for line in lines:
                if line.strip():
                    words = line.split()[1:]  # Exclude the datestamp
                    message = ' '.join(words)
                    if ' '.join(words[-3:]) == separator:
                        current_hop = f'Hop {hop_count}'
                        hops[current_hop] = [message]
                        hop_count += 1
                    else:
                        hops[current_hop].append(message)
    return hops

#takes the hop-separated dict from extract_hops and does the formatting and connection time math
def process_hops(hops):
    player_times = {}
    for hop, entries in hops.items():
        players = {}
        last_disconnection_time = None
        for entry in entries:
            words = entry.split()
            time = words[0]
            player_name = words[1]
            action = words[3]
            if action == 'connected':
                if player_name not in players:
                    players[player_name] = {'connection_time': time, 'disconnection_time': None}
            elif action == 'disconnected':
                players[player_name]['disconnection_time'] = time
                last_disconnection_time = time

        # If a player has a connection but no disconnection, use the last disconnection time found in the section
        for player, times in players.items():
            if times['disconnection_time'] is None and last_disconnection_time is not None:
                times['disconnection_time'] = last_disconnection_time

        hop_player_times = {}
        for player, times in players.items():
            conn_time = times['connection_time'].split(':')
            disc_time = times['disconnection_time'].split(':')
            conn_minutes = int(conn_time[0]) * 60 + int(conn_time[1])
            disc_minutes = int(disc_time[0]) * 60 + int(disc_time[1])
            elapsed_minutes = disc_minutes - conn_minutes
            elapsed_seconds = int(disc_time[2]) - int(conn_time[2])

            if elapsed_seconds < 0:
                elapsed_minutes -= 1
                elapsed_seconds += 60

            hop_player_times[player] = f'{elapsed_minutes:02d}:{elapsed_seconds:02d}'

        player_times[hop] = hop_player_times

    return player_times


#counts hop participation using hop data from process_hops()
def count_player_hops(player_times):
    player_counts = {}
    
    # Iterate through each hop in the dictionary
    for hop, player_dict in player_times.items():
        # Iterate through each player in the current hop
        for player in player_dict:
            if player in player_counts:
                player_counts[player] += 1
            else:
                player_counts[player] = 1
    
    return player_counts

#sort the output from count_player_hops() alphabetically, leaving the hop leader at the top
def sort_player_counts(player_counts):
    first_player = next(iter(player_counts))  # Get the first player in the dictionary
    sorted_counts = sorted(player_counts.items(), key=lambda x: x[0].lower() if x[0].lower() != first_player.lower() else '')  # Sort the player counts
    
    sorted_player_counts = {}
    sorted_player_counts[first_player] = player_counts[first_player]  # Keep the first player at the beginning
    
    # Convert the sorted list back into a dictionary
    for player, count in sorted_counts:
        if player != first_player:
            sorted_player_counts[player] = count
    
    return sorted_player_counts


#takes the input from the GUI and does the outputs
def main(event):
    if event.data.endswith(".txt"):
        var.set(event.data)


        #hop separated log to console
        for section, entries in extract_hops(event.data).items():
            print(f'{section}')
            for entry in entries:
                print(f'{entry}')
            print()


        #Hop counter
        textbox.insert("end", f'Total hop count: {len(extract_hops(event.data))}\n\n', "bold")


        #print player time per hop log
        textbox.insert("end", 'Time spent during each hop:\n', "bold")

        # Iterate through each hop in the player_times dictionary
        for hop, player_dict in process_hops(extract_hops(event.data)).items():
            textbox.insert("end", f"{hop}:\n", "underline")
    
            # Iterate through each player and their time in the current hop
            for player, time in player_dict.items():
                textbox.insert("end", f"{player}: {time}\n")
    
            textbox.insert("end", "\n")


        #print name x hop count output
        textbox.insert("end", f'Hop participation count:\n', "bold")
        #Print the sorted player counts
        for player, count in sort_player_counts(count_player_hops(process_hops(extract_hops(event.data)))).items():
            textbox.insert("end", f"{player} x{count}\n")


#GUI Work
ws = TkinterDnD.Tk()
ws.title('Hop Log Analyzer, by Darkstar1592[K2]')
ws.geometry('400x450')
ws.config(bg='#fcba03')

var = StringVar()
"""
Label(ws, text='Hop leader name', bg='#fcba03').pack(anchor=NW, padx=10)
leader = Text(ws, height=2, width=80)
leader.pack(fill=X, padx=10)
"""

Label(ws, text='', bg='#fcba03').pack(anchor=NW, padx=10)
e_box = Entry(ws, textvar=var, width=80)
e_box.insert(0, "Drag and drop hop file")
e_box.config(state='disabled')
e_box.pack(fill=X, padx=10)
e_box.drop_target_register(DND_FILES)
e_box.dnd_bind('<<Drop>>', main)

textbox = Text(ws, height=22, width=50, font=('Courier',12,''))
textbox.tag_configure("bold", font=('Courier',12,'bold'))
textbox.tag_configure("underline", font=('Courier',12,'underline'))
textbox.pack(fill=BOTH, expand=1, padx=10, pady=10)
textbox.drop_target_register(DND_FILES)
textbox.dnd_bind('<<Drop>>', main)

ws.mainloop()
