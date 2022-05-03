import keyboard  # using module keyboard


# Expecting a TTL signal (keyboard press, 5, or r, or t)
def wait_for_ttl_keyboard():
    while True:
        try:
            if keyboard.is_pressed('5') or \
                    keyboard.is_pressed('T') or \
                    keyboard.is_pressed('t') or \
                    keyboard.is_pressed('r') or \
                    keyboard.is_pressed('R'):
                print('You entered the TTL!')
                break  # finishing the loop
            else:
                pass
        except:
            break
    return None
