class EventEmitter:
    def __init__(self):
        self._handlers = {}

    def on(self, event_name, handler):
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def emit(self, event_name, *args, **kwargs):
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                handler(*args, **kwargs)
