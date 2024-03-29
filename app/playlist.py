from collections import deque
from config import *
from random import shuffle


class Playlist:
    def __init__(self):
        self.queue = deque()
        self.loop_queue = deque()
        self.history = deque()
        self.trackname_history = deque()
        self.loop = False
        self.loop_song = False

    def __len__(self):
        return len(self.queue)

    def add_name(self, trackname):
        self.trackname_history.append(trackname)
        if len(self.trackname_history) > MAX_TRACKNAME_HISTORY_LENGTH:
            self.trackname_history.popleft()

    def add(self, track):
        self.queue.append(track)
    
    def next(self, current_song):
        if self.loop == True:
           self.queue.appendleft(self.history[-1])

        if len(self.queue) == 0:
            return None

        return self.queue[0]
    
    def prev(self, current_song):
        if current_song == None:
            self.queue.appendleft(self.history[-1])
            return self.queue[0]

        index = self.history.index(current_song)

        self.queue.appendleft(self.history[index - 1])

        if current_song != None:
            self.queue.insert(1, current_song)
    
    def shuffle(self):
        shuffle(self.queue)
    
    def empty(self):
        self.queue.clear()
        self.history.clear()