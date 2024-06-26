import curses
from files import Files
from cyrypt import Crpt
from cyrypt import derive_key

class FHpass:
    def __init__(self, stdscr) -> None:
        self.height, self.width = stdscr.getmaxyx()
        self.files = Files()
        self.cr = None
        self.s_pswds = None
        
    def welcome(self, stdscr):
        stdscr.clear()
        stdscr.keypad(True)
        
        if self.files.is_first_ses():
            self.registrate(stdscr)

        else:
            self.log_in(stdscr)

        stdscr.refresh()

    def registrate(self, stdscr):
        stdscr.addstr(1, 0, "  ______  _                               ", curses.color_pair(6))
        stdscr.addstr(2, 0, " |  ____|| |                              ", curses.color_pair(6)) 
        stdscr.addstr(3, 0, " | |__   | |__   _ __    __ _  ___   ___  ", curses.color_pair(6))                      
        stdscr.addstr(4, 0, " |  __|  | '_ \\ | '_ \\  / _` |/ __| / __| ", curses.color_pair(6))  
        stdscr.addstr(5, 0, " | |     | | | || |_) || (_| |\\__ \\ \\__ \\ ", curses.color_pair(6))  
        stdscr.addstr(6, 0, " |_|     |_| |_|| .__/  \\__,_||___/ |___/ ", curses.color_pair(6))  
        stdscr.addstr(7, 0, "                | |                       ", curses.color_pair(6))  
        stdscr.addstr(8, 0, "                |_|                       ", curses.color_pair(6))  


        stdscr.addstr(10,0, '[info]: Welcome to the fhpass, a linux/macos password manager',         curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(11,0, '[info]: Store passwords on your local machine',   curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(12,0, '[warning]: if you forget your login password, you will not get acces.', curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(13,0, '[info]: first login, welcome. lets create your password',               curses.color_pair(1) | curses.A_BOLD)

        pswds_y = 15
        error_y = pswds_y + 1

        while True:
            stdscr.addstr(pswds_y, 0, 'create password: ')
            pswd = pswd_creating(stdscr, error_y, pswds_y)
            
            clear_line(stdscr, error_y, 0, self.width)
            stdscr.addstr(pswds_y, 0, 'repeat password: ')
            
            r_pswd = pswd_creating(stdscr, error_y, pswds_y)
            clear_line(stdscr, error_y, 0, self.width)
            
            if pswd == r_pswd:
                bpswd = pswd.encode('utf-8')
                stdscr.addstr(error_y, 0, 'password created')
                stdscr.addstr(error_y+1, 0, 'press any button to continue')

                self.cr = Crpt(derive_key(bpswd, generate_salt=True))
                self.files.set_pswd(pswd, self.cr)

                self.s_pswds = self.files.get_saved_pswds(self.cr)

                stdscr.getch()
                stdscr.clear()
                break
            
            else: 
                stdscr.addstr(error_y, 0, 'incorrect password', curses.color_pair(2))
        
            stdscr.refresh()

        self.menu(stdscr)
    
    def log_in(self, stdscr):
        stdscr.addstr(0, 0, '[info]: loging in', curses.color_pair(1))
        stdscr.addstr(1, 0, '[password]: ')

        pswd = inp_handling(stdscr, 1, 13)
        stored_pswd = self.files.get_pswd()
        bpswd = pswd.encode('utf-8')

        self.cr = Crpt(derive_key(bpswd))

        if self.cr.verify_hash(pswd, stored_pswd):
            stdscr.addstr(2, 0, 'Login in ...')
            self.s_pswds = self.files.get_saved_pswds(self.cr)

            stdscr.getch()
            self.menu(stdscr)
    
        stdscr.refresh()        

    def menu(self, stdscr):
        selected = None
        current_login = None
        current_password = None
        start = 0
        end = self.height - 7
        cursor = 0 

        collison = 0
        # there was a problem with cursor's position, this variable was only one solution i found,
        # you can remove this variable and see what was the problem. i hope you'll find a better solution

        stdscr.clear()

        while True:
            draw_interface(stdscr, self.width, self.height)
            self.s_pswds = self.files.get_saved_pswds(self.cr)

            draw_pswds_list(stdscr, self.s_pswds, cursor+collison, start, end, self.width, self.height)

            if self.s_pswds and selected is not None:
                current_name, current_login, current_password = self.s_pswds[selected]
                draw_login_pswd_context(stdscr, current_name, current_login, current_password, self.width)
                
            stdscr.refresh()
        
            key = stdscr.getch()

            if key == 265: #F1
                break

            elif key == 268: #F4
                k = stdscr.getch()
                if k == curses.KEY_ENTER or k == 10:
                    self.files.reboot()
                    break

            elif key == 266: #F2
                self.add_name_pswd_login(stdscr)
                start = 0
                cursor = 0
                collison = 0
                end = self.height - 7

            elif key == 10: # ENTER
                selected = cursor

            elif key == 259 or key == ord('k'): #arrow up
                if cursor > start:
                    cursor -= 1

                if cursor == start and start > 0:
                    collison +=1
                    start -= 1
                    end -= 1

            elif key == 258 or key == ord('j'): #arrow down
                if cursor < len(self.s_pswds)-1:
                    cursor += 1
                
                if cursor == end and end < len(self.s_pswds):
                    start += 1
                    end += 1
                    collison -= 1

            elif key == 267 and current_login: # F3
                self.files.delete_saved_pas(cursor+collison)
                clear_section(stdscr, 3, 10, (self.width//3)+4, self.width-5)

                start = 0
                cursor = 0
                collison = 0
                end = self.height - 7
                selected = None

                current_name, current_login, current_password = (None, None, None)

    def add_name_pswd_login(self, stdscr):
        x = (self.width // 3) + 4
        y = self.height-9
        inp_pos = x + 13

        max_input_length = (self.width - inp_pos)-4
        div_length = max_input_length+13

        stdscr.addstr(y, x, '~'*div_length, curses.color_pair(4))
        stdscr.addstr(y+1, x, 'Add name, login and password', curses.color_pair(6))
        stdscr.addstr(y+2, x, '[name tag]: ', curses.color_pair(7))
        name = inp_handling(stdscr, y+2, inp_pos, max_input_length, invisible=False)

        stdscr.addstr(y+3, x, '[login]: ', curses.color_pair(7))
        login = inp_handling(stdscr, y+3, inp_pos, max_input_length, invisible=False)

        stdscr.addstr(y+4, x, '[password]: ', curses.color_pair(7))
        password = inp_handling(stdscr, y+4 , inp_pos, max_input_length, invisible=False)

        self.files.set_saved_pswds(name, login, password, self.cr)            
        clear_section(stdscr, y, y+5, x, inp_pos+max_input_length)

def clear_line(stdscr, y, x, length=1):
    stdscr.addstr(y, x, ' '*length)

def clear_section(stdscr, y_start, y_end, section_start, section_end):
    for i in range(y_start, y_end):
        clear_line(stdscr, i, section_start, section_end)

def draw_login_pswd_context(stdscr, name, login, pswd, width):
    max_x = width-2
    y = 3
    x = (width // 3) + 4

    s_width = (max_x - x)
    div_length = (s_width//2)-2

    clear_section(stdscr, y-1, y+5, x, s_width)

    stdscr.addstr(y, x, f'Name: {name}', curses.color_pair(4))
    stdscr.addstr(y+1, x, f'Login: {login}', curses.color_pair(3))
    stdscr.addstr(y+2, x, '#='*div_length, curses.color_pair(4))

    stdscr.addstr(y+3, x, f'Password: {pswd}', curses.color_pair(1))
    stdscr.addstr(y+5, x, '__ delete', curses.color_pair(3))
    stdscr.addstr(y+5, x, 'F3', curses.color_pair(5))

    

def draw_pswds_list(stdscr, pswds, cur_pos, start, end, w_width, w_height):
    max_x = w_width // 3
    max_y = w_height - 3
    max_inp_length = max_x // 2
    
    y = 3
    x = 1

    clear_section(stdscr, y, max_y, x, max_x-2)

    if pswds:
        for i, pswd in enumerate(pswds[start:end]): 
            name = pswd[0]
            whtspc = ' '*(max_inp_length-len(name))
            corrected_name = check_length(name, max_length=max_inp_length)

            password_string = f'{corrected_name}{whtspc}: '

            clear_line(stdscr, y, x, max_x-2)

            if cur_pos == i:
                stdscr.addstr(y, x, password_string + '*********', curses.color_pair(5))

            else:
                stdscr.addstr(y, x, password_string, curses.color_pair(0))
                stdscr.addstr(y, len(password_string), ' *********', curses.color_pair(1))
                
            y+=1

        if start > 0:
            stdscr.addstr(2, x, '>....<', curses.color_pair(2))

        elif start == 0:
            clear_line(stdscr, 2, x, max_x-2)

        if len(pswds) > end+start:
            stdscr.addstr(y, x, '>....<', curses.color_pair(2))

        elif len(pswds) < end+start:
            clear_line(stdscr, y, x, max_x-2)

    else:
        clear_line(stdscr, 2, x, max_x-2)
        stdscr.addstr(y+1, x, "#/#/#/#/#/#/#/#/#/#/#/#/#/#   ",  curses.color_pair(4))
        stdscr.addstr(y+2, x, "                              ",)
        stdscr.addstr(y+3, x, "You dont have any passwords   ",  curses.color_pair(3))
        stdscr.addstr(y+4, x, "Press [a] to add a password   ", curses.color_pair(3))
        stdscr.addstr(y+5, x, "                              ",)



def draw_interface(stdscr, width, height):
    for x in range(width):
        stdscr.addstr(0, x, '-')
        stdscr.addstr(height - 2, x, '-')

    for i in range(2, height-3):
        stdscr.addstr(i, width-2, '#', curses.color_pair(4))

    for i in range(2, height-4, 2):
        stdscr.addstr(i, width // 3, '|', curses.color_pair(4))
        stdscr.addstr(i+1, width // 3, '%', curses.color_pair(4))


    y = height-1
    x = 0
    controls_text = "__ quit; __ add password; __ reset; _______ navigation; _____ select;"
    controls_chars = ["F1", "F2", "F4", "UP/DOWN", "ENTER"]

    for part in controls_text.split(" "):
        if part.startswith("_"):
            char = controls_chars.pop(0)
            stdscr.addstr(y, x, char, curses.color_pair(5))
        else:
            stdscr.addstr(y, x, part, curses.color_pair(3))
        x += len(part)+1

def inp_handling(stdscr, y, x, max_inp_length=20, invisible=True):
        output = ''
        output_x = x

        while True:
            key = stdscr.getch()

            if key != 9:
                if (key == curses.KEY_ENTER or key == 10) and len(output) > 0:
                    if invisible:
                        for i in range(output_x, x-1, -1):
                            stdscr.addstr(y, i, ' ')
                    break

                elif key == curses.KEY_BACKSPACE or key == 127:
                    output = output[:-1]

                    if output_x > x:
                        stdscr.addstr(y, output_x - 1, ' ')
                        output_x -= 1

                else:
                    if (output_x < x + max_inp_length) and key != 10:
                        output += chr(key)
                        if invisible:
                            stdscr.addstr(y, output_x, '*', curses.color_pair(3))
                        else:
                            stdscr.addstr(y, output_x, chr(key), curses.color_pair(1))
                        output_x += 1 

        return output

def pswd_creating(stdscr, error_line, input_pos_y, input_pos_x=17):
        while True:
            output = inp_handling(stdscr, input_pos_y, input_pos_x)
            if len(output) >= 3 < 20:
                return output
            else: 
                if len(output) < 3:
                    stdscr.addstr(error_line, 0, 'password is too short', curses.color_pair(2))

def check_length(par, max_length=12):
    if len(par) > max_length:
        return par[:max_length-3] + '...' 
    return par

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    curses.init_pair(5, -1, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)

    process = FHpass(stdscr)
    process.welcome(stdscr)

if __name__ == '__main__':
    curses.wrapper(main)
