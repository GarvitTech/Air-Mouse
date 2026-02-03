#!/usr/bin/env python3
import serial
import pyautogui
import time
import sys

# Simple and robust version
pyautogui.FAILSAFE = False

def main():
    # Initialize serial variable
    ser = None
    
    # Try to connect
    try:
        ser = serial.Serial('/dev/cu.usbserial-140', 115200, timeout=1)
        print("✓ Connected to Arduino")
        time.sleep(2)  # Wait for Arduino
        
        # Clear buffer
        ser.reset_input_buffer()
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("Available ports:")
        from serial.tools import list_ports
        ports = list(list_ports.comports())
        for p in ports:
            print(f"  {p.device} - {p.description}")
        return
    
    # Screen info
    screen_width, screen_height = pyautogui.size()
    mouse_x, mouse_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(mouse_x, mouse_y)
    
    # Calibration
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
                # Read line
                if ser.in_waiting > 0:
                    line_bytes = ser.readline()
                    
                    # Try different decodings
                    try:
                        line = line_bytes.decode('ascii').strip()
                    except:
                        try:
                            line = line_bytes.decode('utf-8', errors='ignore').strip()
                        except:
                            line = line_bytes.decode('latin-1').strip()
                    
                    if line:
                        # Debug: print all received data
                        print(f"RX: '{line}'")
                        
                        # Check if it's CSV data
                        if ',' in line:
                            parts = line.split(',')
                            
                            # We accept different formats:
                            # Format 1: pitch,roll,left,right (4 parts)
                            # Format 2: accX,accY,accZ,pitch,roll,left,right (7 parts)
                            
                            if len(parts) == 4:
                                # Format 1
                                pitch = float(parts[0])
                                roll = float(parts[1])
                                left_click = parts[2] == '1'
                                right_click = parts[3] == '1'
                                
                            elif len(parts) == 7:
                                # Format 2
                                pitch = float(parts[3])
                                roll = float(parts[4])
                                left_click = parts[5] == '1'
                                right_click = parts[6] == '1'
                                
                            else:
                                # Unknown format, skip
                                print(f"Unknown format with {len(parts)} parts")
                                continue
                            
                            # Calibration on first valid reading
                            if not calibrated:
                                base_pitch = pitch
                                base_roll = roll
                                calibrated = True
                                print(f"Calibrated: Pitch={pitch:.1f}°, Roll={roll:.1f}°")
                                continue
                            
                            # Calculate movement
                            delta_pitch = pitch - base_pitch
                            delta_roll = roll - base_roll
                            
                            # Apply sensitivity (adjust as needed)
                            sensitivity = 3.0
                            move_x = delta_roll * sensitivity
                            move_y = delta_pitch * sensitivity
                            
                            # Update mouse position
                            mouse_x += move_x
                            mouse_y += move_y
                            
                            # Keep in bounds
                            mouse_x = max(20, min(screen_width - 20, mouse_x))
                            mouse_y = max(20, min(screen_height - 20, mouse_y))
                            
                            # Move mouse
                            pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
                            
                            # Handle clicks
                            if left_click:
                                pyautogui.click()
                                time.sleep(0.2)
                            
                            if right_click:
                                pyautogui.click(button='right')
                                time.sleep(0.2)
                            
                            # Success
                            success_count += 1
                            error_count = 0
                            
                            # Show progress every 50 frames
                            if success_count % 50 == 0:
                                print(f"✓ Frames: {success_count}, Position: ({mouse_x:.0f}, {mouse_y:.0f})")
                
                # Small delay
                time.sleep(0.01)
                
            except ValueError as e:
                # Data parsing error
                error_count += 1
                if error_count % 10 == 0:
                    print(f"Data error #{error_count}: {e}")
                continue
                
            except Exception as e:
                # Other errors
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