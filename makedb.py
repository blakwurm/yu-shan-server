import data

def main():
    data.create_db()

if __name__ == '__main__':
    import plac; plac.call(main)