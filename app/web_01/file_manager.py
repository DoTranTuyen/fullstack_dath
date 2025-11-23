from core.__Include_Library import *

class FileManager:
    def __init__(self, wrapper_folder , folder_name: str, file_name: str):
        """
        Khởi tạo FileManager với đường dẫn thư mục và file.

        :param folder_name: Tên thư mục chứa file
        :param file_name: Tên file cần xử lý
        """
        self.folder_path = os.path.join(wrapper_folder, folder_name)
        self.file_path = os.path.join(self.folder_path, file_name)
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.folder_path, exist_ok=True)
    
    def read_json(self):
        """ Đọc dữ liệu từ file JSON """
        if not os.path.exists(self.file_path):
            return None  # Nếu file chưa tồn tại, trả về None

        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_json(self, data):
        """ Ghi dữ liệu vào file JSON """
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False) 
        
    def get_pwd(self):
        return self.file_path