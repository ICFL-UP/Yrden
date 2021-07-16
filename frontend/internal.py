class InternalPrinter:
    """Internal Business Logic"""
    def process(self):
        print("Internal Hello")

class MyApplication:
    def __init__(self, *, plugins: list=list()):
        self.internal_models = [InternalPrinter()]
        self.plugins = plugins

    def run(self):
        print("Starting program")
        print("-" * 79)

        modules_to_execute = self.internal_models + self.plugins
        for module in modules_to_execute:
            module.process()

        print("-" * 79)
        print("Program done")
        print()