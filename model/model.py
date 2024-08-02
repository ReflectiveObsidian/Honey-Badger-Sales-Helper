from datetime import datetime

class Model:
    def __init__(self, view):
        self.view = view
        self.call_logs_observers = []
        self.salesperson_sound_device_id = 0
        self.customer_sound_device_id = 0
        self.customer_id = ""
        self.salesperson_id = ""
        self.customer_phone = ""

        self.initialise()

    def set_salesperson_sound_device_id(self, device_id):
        self.salesperson_sound_device_id = device_id
        self.__update_view()

    def get_salesperson_sound_device_id(self):
        return self.salesperson_sound_device_id
    
    def set_customer_sound_device_id(self, device_id):
        self.customer_sound_device_id = device_id
        self.__update_view()

    def get_customer_sound_device_id(self):
        return self.customer_sound_device_id

    def set_call_log_observer(self, observer):
        self.call_logs_observers.append(observer)

    def update_call_log_observers(self):
        for observer in self.call_logs_observers:
            observer(self.call_logs)

    def get_call_logs(self):
        return self.call_logs
    
    def add_call_log(self, call_log):
        self.call_logs.append(call_log)
        self.update_call_log_observers()
        self.__update_view()

    def clear_call_logs(self):
        self.call_logs = []
        self.update_call_log_observers()
        self.__update_view()

    def get_emotion(self):
        if self.emotion.__len__() == 0:
            return "waiting..."
        else:
            return self.emotion[self.emotion.__len__() - 1][0]
    
    def set_emotion(self, emotion):
        timestamp = datetime.now()
        self.emotion.append([emotion, timestamp])
        self.__update_view()

    def get_personalities(self):
        return self.personalities
    
    def set_personalities(self, personalities):
        self.personalities = personalities
        self.__update_view()

    def get_warnings(self):
        return self.warnings
    
    def set_warnings(self, warnings):
        self.warnings = warnings
        self.__update_view()

    def get_todo_list(self):
        return self.todo_list
    
    def set_todo_list(self, todo):
        self.todo_list = todo
        self.__update_view()

    def set_summary(self, summary):
        self.summary = summary
        self.__update_view()

    def get_summary(self):
        return self.summary
    
    def set_customer_id(self, customer_id):
        self.customer_id = customer_id
        self.__update_view()

    def get_customer_id(self):
        return self.customer_id
    
    def set_salesperson_id(self, salesperson_id):
        self.salesperson_id = salesperson_id
        self.__update_view()

    def get_salesperson_id(self):
        return self.salesperson_id
    
    def set_customer_phone(self, customer_phone):
        self.customer_phone = customer_phone
        self.__update_view()

    def get_customer_phone(self):
        return self.customer_phone

    def initialise(self):
        self.call_logs = []
        self.emotion = []
        self.personalities = ["waiting..."]
        self.warnings = ""
        self.todo_list = "Generating..."
        self.summary = "Generating..."

        self.__update_view()

    def __update_view(self):
        self.view.update(self)
        