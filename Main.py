from Suggestor import Suggestor  # Sınıfı doğrudan import et
from UI import run_ui

class Main:    
    if __name__ == "__main__":
        data = run_ui()
        suggestor = Suggestor(data)