class ControlReference:
    control_reference = {}

    @classmethod
    def add_control_reference(cls, key, value):
        try:
            cls.control_reference[key] = value
        except KeyError as e:
            print(e)
        finally:
            pass

    @classmethod
    def return_control_reference(cls):
        return cls.control_reference