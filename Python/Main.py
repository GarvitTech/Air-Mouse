import serial
import pyautogui
import time
import sys
pyautogui.FAILSAFE = False

def main():
    ser = None
    try:
        ser = serial.Serial('/dev/cu.usbserial-140', 115200, timeout=1)
        print("✓ Connected to Arduino")
        time.sleep(2)
        ser.reset_input_buffer()
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("Available ports:")
        from serial.tools import list_ports
        ports = list(list_ports.comports())
        for p in ports:
            print(f"  {p.device} - {p.description}")
        return
    screen_width, screen_height = pyautogui.size()
    mouse_x, mouse_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(mouse_x, mouse_y)
    calibrated = False
    base_pitch = 0
    base_roll = 0
    print("\n✓ AIR MOUSE ACTIVE")
    print("Move device to control cursor")
    print("Press Ctrl+C to stop\n")
    error_count = 0
    success_count = 0
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line_bytes = ser.readline()
                    try:
                        line = line_bytes.decode('ascii').strip()
                    except:
                        try:
                            line = line_bytes.decode('utf-8', errors='ignore').strip()
                        except:
                            line = line_bytes.decode('latin-1').strip()
                    
                    if line:
                        print(f"RX: '{line}'")
                        if ',' in line:
                            parts = line.split(',')
                            if len(parts) == 4:
                                pitch = float(parts[0])
                                roll = float(parts[1])
                                left_click = parts[2] == '1'
                                right_click = parts[3] == '1'
                                
                            elif len(parts) == 7:
                                pitch = float(parts[3])
                                roll = float(parts[4])
                                left_click = parts[5] == '1'
                                right_click = parts[6] == '1'
                                
                            else:
                                print(f"Unknown format with {len(parts)} parts")
                                continue
                            if not calibrated:
                                base_pitch = pitch
                                base_roll = roll
                                calibrated = True
                                print(f"Calibrated: Pitch={pitch:.1f}°, Roll={roll:.1f}°")
                                continue
                            delta_pitch = pitch - base_pitch
                            delta_roll = roll - base_roll
                            sensitivity = 3.0
                            move_x = delta_roll * sensitivity
                            move_y = delta_pitch * sensitivity
                            mouse_x += move_x
                            mouse_y += move_y
                            mouse_x = max(20, min(screen_width - 20, mouse_x))
                            mouse_y = max(20, min(screen_height - 20, mouse_y))
                            pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
                            if left_click:
                                pyautogui.click()
                                time.sleep(0.2)
                            if right_click:
                                pyautogui.click(button='right')
                                time.sleep(0.2)
                            success_count += 1
                            error_count = 0
                            if success_count % 50 == 0:
                                print(f"✓ Frames: {success_count}, Position: ({mouse_x:.0f}, {mouse_y:.0f})")
                time.sleep(0.01)
            except ValueError as e:
                error_count += 1
                if error_count % 10 == 0:
                    print(f"Data error #{error_count}: {e}")
                continue
            except Exception as e:
                error_count += 1
                print(f"Unexpected error #{error_count}: {e}")
                if error_count > 20:
                    print("Too many errors. Stopping.")
                    break
                continue
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        if ser is not None:
            ser.close()
            print(f"✓ Disconnected. Successfully processed {success_count} frames.")
if __name__ == "__main__":
    main()
