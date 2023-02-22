# функция для получения полного пути до файла
def file_directory(directory):
    # directory - путь к файлу, начиная с папок внутри папки игры
    file_directory = open(f"../{directory}", mode="rb").name
    return file_directory
