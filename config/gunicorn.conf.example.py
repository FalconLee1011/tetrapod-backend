import multiprocessing as mp
bind = "127.0.0.1:9001"
workers = mp.cpu_count() - 1
accesslog = "tetrapod.log"