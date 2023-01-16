def file_directory(directory, name):
    file_directory = open(f"../data/{directory}/{name}", mode="rb").name
    return file_directory
