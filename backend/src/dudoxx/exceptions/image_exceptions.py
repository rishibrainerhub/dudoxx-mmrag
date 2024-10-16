class ErrorEncodingImage(Exception):
    def __init__(self, message: str = "Error encoding image"):
        self.message = message
        super().__init__(self.message)


class ErrorProcessingImage(Exception):
    def __init__(self, message: str = "Error processing image"):
        self.message = message
        super().__init__(self.message)
