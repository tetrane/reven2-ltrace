import cProfile

if __name__ == "__main__":
    cProfile.run("from .ltrace import main\nmain()", sort="tottime")
