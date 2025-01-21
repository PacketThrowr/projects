from sqlalchemy.types import TypeDecorator, String

class CustomEnum(TypeDecorator):
    impl = String

    def __init__(self, enum_class):
        self.enum_class = enum_class
        super().__init__()

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_class):  # If it's an enum instance
            return value.value  # Store the string representation
        elif value in [e.value for e in self.enum_class]:  # If it's already a valid value
            return value
        else:
            raise ValueError(f"Invalid value {value} for enum {self.enum_class}")

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.enum_class(value)  # Convert string back to enum instance
        return None
