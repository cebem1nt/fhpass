import os
import shutil

class Files:
    def __init__(self) -> None:
        self.DIR = '.password_manager'

    def is_first_ses(self):
        if not os.path.exists(self.DIR):
            return True
        return False
    
    def set_pswd(self, par, crypt):
        os.makedirs(self.DIR)
        with open(os.path.join(self.DIR, 'pswd_hash.txt'), "w") as file:
            file.write(crypt.hash_data(par))

    def get_pswd(self):
        with open(os.path.join(self.DIR, 'pswd_hash.txt'), 'r') as file:
            return file.readline()
        
    def set_saved_pswds(self, name, pswd, crypt):
        with open(os.path.join(self.DIR, 'pswds.txt'), 'a') as file:
            encrypted_password = crypt.encrypt_password(pswd)
            file.write(f"{name} {encrypted_password.decode()}" + '\n')

    def get_saved_pswds(self, crypt) -> list:
        """
        Takes Crpt instance as decryptor
        and returns all saved logins and passwords
        !logins are not encrypted!
        """

        if not os.path.exists(os.path.join(self.DIR, 'pswds.txt')):
            with open(os.path.join(self.DIR, 'pswds.txt'), "w") as file:
                pass


        with open(os.path.join(self.DIR, 'pswds.txt'), 'r') as file:
            log_pas = []
            for line in file:
                if len(line) > 5:
                    x = line.split(' ')
                    decrypted_password = crypt.decrypt_password(x[1].encode())
                    log_pas.append((x[0], decrypted_password))
        return log_pas
    
    def delete_saved_pas(self, login):
        with open(os.path.join(self.DIR, 'pswds.txt'), 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            key = line.rstrip().split(' ')[0]
            if key != login:
                new_lines.append(line.strip())

        with open(os.path.join(self.DIR, 'pswds.txt'), 'w') as file:
            file.write('\n'.join(new_lines) + '\n')

    def reboot(self):
        shutil.rmtree(self.DIR)