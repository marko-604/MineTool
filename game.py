import os
import sys
import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard  # Add this import
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QRect
import csv
from datetime import timedelta

wallet = 100  # Initial money in the wallet
bet_amount = 1  # Bet amount per round
gains = 1.13  # Multiplier for winning






base_dir = "screenshots"
# Load gem and bomb images for matching
gem_img = cv2.imread('jewel_gray.PNG', cv2.IMREAD_GRAYSCALE)
bomb_img = cv2.imread('bomb_highlighted.png', cv2.IMREAD_GRAYSCALE)
bomb2_img = cv2.imread('THEBOMB.png', cv2.IMREAD_GRAYSCALE)
cashout_img = cv2.imread('cashout.png', cv2.IMREAD_GRAYSCALE)
bomba = cv2.imread('bomba.png', cv2.IMREAD_GRAYSCALE)
gem_img2 = cv2.imread('jewel_ highlighted.PNG', cv2.IMREAD_GRAYSCALE)
gem_img3 = cv2.imread('THEGEMM.png', cv2.IMREAD_GRAYSCALE)
upper_gem = cv2.imread('A5.png', cv2.IMREAD_GRAYSCALE)
bomba_upperdecker = cv2.imread('bombupper.png', cv2.IMREAD_GRAYSCALE)
bomb_anotherup = cv2.imread('bombupp.png', cv2.IMREAD_GRAYSCALE)


matching_threshold = 0.65

# Define positions and sizes
grid_start_x, grid_start_y = 600, 200
square_size = 100
spacing = 11
cashout_button_position = (212, 477)
cashout_clicking = ((212 + 240) // 2, (477 + 20))
bet_button_position = (212, 371)
bet_clicking = ((212 + 240) // 2, (371 + 20))
button_width, button_height = 240, 40
wins_count = 0


win = True
# Row and column labels
row_labels = ['A', 'B', 'C', 'D', 'E']
col_labels = ['1', '2', '3', '4', '5']

# Initialize CSV file with headers
csv_filename = "grid_results.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Gem", "Gem", "Gem", "Win", "Position"])



class TransparentOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iteration = 1  # Initialize iteration counter

        self.start_time = None  # To store the start time of the game
        self.elapsed_time = timedelta(0)  # To accumulate the total runtime
        # Initialize overlay and game automation states
        self.overlay_visible = True
        self.game_running = False
        self.num_clicks = 3  # Number of random squares to click
        self.bet_counter = 0

        # Set up the transparent overlay window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)  # Adjust to your screen resolution

        # Overlay toggle button
        self.overlay_button = QPushButton('Turn Overlay Off', self)
        self.overlay_button.setGeometry(50, 50, 150, 50)
        self.overlay_button.clicked.connect(self.toggle_overlay)
        self.overlay_button.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        # Game automation toggle button
        self.game_button = QPushButton('Start Game Automation', self)
        self.game_button.setGeometry(50, 110, 150, 50)
        self.game_button.clicked.connect(self.toggle_game)
        self.game_button.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        # Timer for the game automation loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_game)

        # Start listening for the "Esc" key to stop the game automation
        keyboard.add_hotkey('esc', self.stop_game)

    def toggle_overlay(self):
        # Toggle overlay visibility
        self.overlay_visible = not self.overlay_visible
        self.overlay_button.setText('Turn Overlay On' if not self.overlay_visible else 'Turn Overlay Off')
        self.update()

    def toggle_game(self):
        # Toggle game automation
        self.game_running = not self.game_running
        if self.game_running:
            print(f"Wallet Amount: {wallet}")
            self.game_button.setText('Stop Game Automation\n\t(esc)')
            self.timer.start(1000)  # Run the game every 1 second

            # Set the start time for runtime tracking
            if self.start_time is None:
                self.start_time = time.time()
        else:
            print("Stopping game automation...")
            self.game_button.setText('Start Game Automation')
            self.timer.stop()

            # Update elapsed time when stopped
            if self.start_time:
                self.elapsed_time += timedelta(seconds=time.time() - self.start_time)
                self.start_time = None

            # Print total elapsed time in hours:minutes:seconds
            print(f"Total Runtime: {str(self.elapsed_time)}")

    def stop_game(self):
        # Stop the game automation immediately
        if self.game_running:
            print("Game automation stopped by keyboard shortcut.")
            self.game_running = False
            self.game_button.setText('Start Game Automation')
            self.timer.stop()

            # Update elapsed time when stopped
            if self.start_time:
                self.elapsed_time += timedelta(seconds=time.time() - self.start_time)
                self.start_time = None

            # Print total elapsed time in hours:minutes:seconds
            print(f"Total Runtime: {str(self.elapsed_time)}")

    def run_game(self):
        global wins_count,wallet
        #print("Running game automation...")

        try:
            if self.start_time:
                current_runtime = timedelta(seconds=(time.time() - self.start_time) + self.elapsed_time.total_seconds())
                print(f"Current Runtime: {str(current_runtime)}")
            # Click Bet button
            pyautogui.moveTo(bet_clicking[0], bet_clicking[1], duration=0.2)
            pyautogui.click()
            print("Bet Counter:", self.iteration)
            # Place the bet and deduct the bet amount from the wallet
            wallet -= bet_amount
            print(f"Bet placed. Remaining wallet: ${wallet}")

            time.sleep(1)

            # Generate grid positions and randomly select positions to click
            grid_positions = [
                (grid_start_x + col * (square_size + spacing) + square_size // 2,
                 grid_start_y + row * (square_size + spacing) + square_size // 2)
                for row in range(5) for col in range(5)
            ]

            classified_positions = []
            for idx, position in enumerate(grid_positions):
                row = idx // 5  # Determine row index
                col = idx % 5  # Determine column index
                label = f"{row_labels[row]}{col_labels[col]}"
                classified_positions.append((label, position))
            # Print the classified positions
            #for label, pos in classified_positions:
                 #print(f"{label}: {pos}")



            selected_positions = random.sample(grid_positions, self.num_clicks)
            # Collect all rows of data for this game
            all_row_data = []
            row_data = [0, 0, 0, 0,"","",""]
            self.iteration += 1
            # Randomly click selected positions and process the grid squares
            for idx, position in enumerate(selected_positions):
                label, _ = next(
                    ((row_label + col_label, pos) for row_label, col_label, pos in [
                        (row_labels[idx // 5], col_labels[idx % 5], pos)
                        for idx, pos in enumerate(grid_positions)
                    ] if pos == position),
                    (None, None)
                )
                # Validate position format
                if not isinstance(position, tuple) or len(position) != 2:
                    raise ValueError(f"Invalid position format: {position}. Expected a tuple (x, y).")

                # Click the position
                #  print(f"Clicking grid position at center: {position}")
                pyautogui.moveTo(position[0], position[1], duration=0.2)
                pyautogui.click()
                time.sleep(1)

                # Define the region for the screenshot
                region = (
                    position[0] - square_size // 2,
                    position[1] - square_size // 2,
                    square_size,
                    square_size
                )

                # Capture and process the screenshot
                screenshot = pyautogui.screenshot(region=region)
                screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                # Create a new folder for this iteration

                iteration_dir = os.path.join(base_dir, str(self.iteration))
                os.makedirs(iteration_dir, exist_ok=True)
                # Save the screenshot in the iteration folder
                filename = os.path.join(iteration_dir, f"{label}.PNG")
                cv2.imwrite(filename, screen_img)
                #print(f"Saved screenshot for grid position {position} as {filename}")

                is_bomb1 = self.is_match(screen_img, bomb_img)
                is_bomb2 = self.is_match(screen_img, bomb2_img)
                is_bomb3 = self.is_match(screen_img, bomba)
                is_jewel3 = self.is_match(screen_img,gem_img3)
                is_gem_toprow = self.is_match(screen_img, upper_gem)
                is_bomb_toprow = self.is_match(screen_img, bomba_upperdecker)
                is_bomb_anothertop = self.is_match(screen_img,bomb_anotherup)
                # Check for gem or bomb using template matching

                if is_jewel3 or is_gem_toprow:
                    #print(f"Gem Found at {label}{position}!")
                    row_data[idx] = 1
                    row_data[idx + 4] = label
                elif is_bomb1 or is_bomb2 or is_bomb3 or is_bomb_toprow or is_bomb_anothertop:
                    print(f"Bomb Found!")
                    row_data[idx] = 0
                    row_data[idx + 4] = label
                else:
                    print(f"No match Found! Error.")
                    row_data[idx] = 3
                    row_data[idx + 4] = label

                print(row_data)
            # Append the processed row data to the list
            all_row_data.append(row_data)
            for row in all_row_data:
                if row[0] == 1 and row[1] == 1 and row[2] == 1:
                    row[3] = 1
                    wins_count += 1
                    wallet += bet_amount * gains  # Add the winnings to the wallet
                    print(f"Win! Total:{wins_count}. Wallet:{wallet}")
                if row[0] == 3 or row[1] == 3 or row[2] == 3:
                    row[3] = 8888899999


            # Write all data to CSV after processing all selected positions
            with open(csv_filename, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(all_row_data)

            # Click Cashout button
            pyautogui.moveTo(cashout_clicking[0], cashout_clicking[1], duration=0.2)

            pyautogui.click()

        except Exception as e:
            print(f"An error occurred: {e}")


    def is_match(self, screen_img, template_img):
        result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val >= matching_threshold

    def paintEvent(self, event):
        if not self.overlay_visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the 5x5 grid in red
        pen = QPen(QColor(255, 0, 0, 150), 2)  # 150 alpha for semi-transparency
        painter.setPen(pen)
        for row in range(5):
            for col in range(5):
                top_left_x = grid_start_x + col * (square_size + spacing)
                top_left_y = grid_start_y + row * (square_size + spacing)
                painter.drawRect(top_left_x, top_left_y, square_size, square_size)

        # Draw the Cashout button overlay in red
        pen.setColor(QColor(255, 0, 0, 150))
        painter.setPen(pen)
        painter.drawRect(cashout_button_position[0], cashout_button_position[1], button_width, button_height)

        # Draw text in the middle of the Cashout button
        text = "Cashout"
        font = QFont("Arial", 12)  # Customize font style and size
        painter.setFont(font)
        text_rect = QRect(
            cashout_button_position[0],
            cashout_button_position[1],
            button_width,
            button_height
        )
        painter.drawText(text_rect, Qt.AlignCenter, text)

        # Draw the Bet button overlay in red
        painter.setPen(pen)
        painter.drawRect(bet_button_position[0], bet_button_position[1], button_width, button_height)

        # Draw text in the middle of the Bet button
        text = "Bet"
        text_rect = QRect(
            bet_button_position[0],
            bet_button_position[1],
            button_width,
            button_height
        )
        painter.drawText(text_rect, Qt.AlignCenter, text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    overlay.show()
    sys.exit(app.exec_())
