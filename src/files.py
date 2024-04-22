import os
import shutil

class Files:
    def __init__(self) -> None:
        self.HOME_DIR = os.path.expanduser('~')
        self.DIR = os.path.join(self.HOME_DIR, '.password_manager')

    def is_first_ses(self):
        return not os.path.exists(self.DIR)
    
    def set_pswd(self, par, crypt):
        """
        Sets entry hashed password to pswd_hash.txt
        """
        os.makedirs(self.DIR, exist_ok=True)

        with open(os.path.join(self.DIR, 'pswd_hash.txt'), "w") as file:
            file.write(crypt.hash_data(par))

    def get_pswd(self):
        """
        Gets entry saved password hash from pswd_hash.txt
        """

        with open(os.path.join(self.DIR, 'pswd_hash.txt'), 'r') as file:
            return file.readline()
        
    def set_saved_pswds(self, name, login, pswd, crypt):
        """
        Writes new name/login/password trio to pswds.txt file
        """

        with open(os.path.join(self.DIR, 'pswds.txt'), 'a') as file:

            encrypted_password = crypt.encrypt_value(pswd).decode()
            encrypted_login = crypt.encrypt_value(login).decode()
            encrypted_name = crypt.encrypt_value(name).decode()

            file.write(f"{encrypted_name} {encrypted_login} {encrypted_password}" + '\n')

    def get_saved_pswds(self, crypt) -> list:
        """
        Takes Crpt instance as decryptor
        and returns list of tuples with name, login, password
        """
        name_log_pas = []
        path = os.path.join(self.DIR, 'pswds.txt')

        if os.path.exists(path):

            with open(path, 'r') as file:
                for line in file:
                    if len(line) > 5:
                        x = line.split() # [name, login, password]

                        d_name = crypt.decrypt_value(x[0].encode())
                        d_login = crypt.decrypt_value(x[1].encode())
                        d_password = crypt.decrypt_value(x[2].encode())

                        name_log_pas.append((d_name, d_login, d_password))

        return name_log_pas
    
    def delete_saved_pas(self, line_index):
        """
        Deletes saved name login password by line_index
        """

        file_path = os.path.join(self.DIR, 'pswds.txt')

        with open(file_path, 'r') as file:
            lines = file.readlines()

        if 0 <= line_index < len(lines):
            lines.pop(line_index)

            with open(file_path, 'w') as file:
                for line in lines:
                    
                    stripped_line = line.strip()

                    if stripped_line:
                        file.write(stripped_line + '\n')

    def reboot(self):
        shutil.rmtree(self.DIR)