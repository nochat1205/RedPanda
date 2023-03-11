import os

dir_path = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.abspath(os.path.join(dir_path, os.path.pardir))

DOC_PATH = os.path.abspath(os.path.join(ROOT_PATH, "doc"))

# 存放解压后的chm文件
temp_path = "temp"
# 存放chm文件
chm_path = "document"
# 存放高亮的临时文件
html_height_line = "html"


# crate dir

def check(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


# document path
def get_chm_path():
    return check(os.path.join(ROOT_PATH, "chm"))

def get_log_path():
    return check(os.path.join(ROOT_PATH, "log"))

if __name__ == "__main__":
    print(dir_path)
    print(ROOT_PATH)