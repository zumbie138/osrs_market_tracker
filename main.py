from collector import Collector
from database import Database
from config import Config
from market_analysis import MarketAnalysis
from datetime import datetime
import tkinter as tk
import threading
import traceback
import time
import gc

POLL_SECONDS = Config.POLL_SECONDS
running = False
current_command = None
process_thread = None
stop_event = threading.Event()

colector = Collector()
database = Database()
ma = MarketAnalysis()

root = tk.Tk()
root.configure(bg='Black')
root.title('OSRS market tracker')

main_frame = tk.Frame(root, bg='black')
control_frame = tk.Frame(root, bg='black')


def log_error(timestamp, erro):
    with open('log_erros.txt', 'a', encoding='utf-8') as arquivo_log:
        arquivo_log.write(f"\n{'='*50}\n")
        arquivo_log.write(f'Timestamp: {timestamp}\n')
        arquivo_log.write(f'Tipo de erro: {type(erro).__name__}\n')
        arquivo_log.write(f'Mensagem: {str(erro)}\n')
        arquivo_log.write('Traceback:\n')
        arquivo_log.write(traceback.format_exc())
        arquivo_log.write(f"\n{'='*50}\n")

def run_all_process():
    #coleta os dados crus do endpoint e salva no database
    colector.data_collect(table='latest')
    colector.data_collect(table='5m')
    
    #limpa dados com timestamp de mais de 3 dias
    database.cleanup_old_data()

    #coleta dados do database da tabela latest e da tabela 5m
    df_latest = database.get_database('latest')
    df_5m = database.get_database('fiveminutes')

    #processa os dados e cria uma nova tabela alerts
    ma.process_analysis_data(df_latest, df_5m)

def run_fetch_only():
    #coleta os dados crus do endpoint e salva no database
    colector.data_collect(table='latest')
    colector.data_collect(table='5m')
    
    #limpa dados com timestamp de mais de 3 dias
    database.cleanup_old_data()

def start_execution(command):
    global running, current_command, process_thread, stop_event
    if running:
        return

    running = True
    current_command = command
    
    stop_event.clear()
    
    show_control_screen()
    
    process_thread = threading.Thread(
        target=lambda: run(command),
        daemon=True
    )
    process_thread.start()
    
def stop_execution():
    global running, process_thread, stop_event
    
    running = False
    stop_event.set()
    
    if process_thread and process_thread.is_alive():
        process_thread.join(timeout=2)
    
    stop_event.clear()
    show_main_screen()
    
def show_main_screen():
    control_frame.grid_remove()
    main_frame.grid(row=0, column=0, padx=20, pady=20)

def show_control_screen():
    main_frame.grid_remove()
    control_frame.grid(row=0, column=0, padx=20, pady=20)

def run(command):
    global running, stop_event
    database.delete_table('mapping')
    colector.data_collect(table='mapping')
    while running:
        timestamp = datetime.now()
        
        print(f'\033[38;2;212;175;55mSalvando novos registros: {timestamp}\033[0m')
        try:
            match command:
                case 'run_all':
                    run_all_process()
                case 'fetch_only':
                    run_fetch_only()
                    
        except Exception as e:
            log_error(timestamp, e)
            
        print('processo finalizado')
        gc.collect()
        stop_event.wait(timeout=POLL_SECONDS)

tk.Button(main_frame, text='RODAR FETCH', command=lambda: start_execution('fetch_only'), fg='black',bg='#AA0000').grid(row=0, column=1)
tk.Button(main_frame, text='RODAR TUDO', command=lambda: start_execution('run_all'), fg='black',bg='#AA0000').grid(row=1, column=1)
tk.Button(control_frame, text='STOP', command=stop_execution, fg='black',bg='#AA0000').grid(row=0, column=1)

show_main_screen()
root.update_idletasks()
width = max(root.winfo_reqwidth(), 300)
height = max(root.winfo_reqheight(), 200)
root.geometry(f"{width}x{height}")
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')
root.mainloop()