import time
import threading

class AgentLogger:
    def __init__(self, max_logs=500):
        self.logs = []
        self.max_logs = max_logs
        self.lock = threading.Lock()

    def log(self, source: str, message: str, level: str = "INFO"):
        with self.lock:
            timestamp = time.strftime("%H:%M:%S")
            log_entry = {
                "time": timestamp,
                "source": source,
                "level": level,
                "message": message
            }
            self.logs.append(log_entry)
            # Imprimimos también en la consola real del backend
            print(f"[{timestamp}] [{source}] {message}")
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)

    def get_logs(self, limit=100):
        with self.lock:
            return self.logs[-limit:]

    def clear(self):
        with self.lock:
            self.logs = []

# Instancia global
agent_log = AgentLogger()
