import tkinter as tk
from tkinter import messagebox
import random
import pickle
import os

class QLearningAgent:
    def __init__(self):
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.3
        self.load_q_table()
        
    def get_state_key(self, board):
        return tuple(board)
    
    def choose_action(self, board, possible_actions):
        state_key = self.get_state_key(board)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0 for action in possible_actions}
        
        if random.random() < self.epsilon:
            return random.choice(possible_actions)
        
        q_values = self.q_table[state_key]
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def update_q_table(self, board, action, reward, next_board, possible_next_actions):
        state_key = self.get_state_key(board)
        next_state_key = self.get_state_key(next_board)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0 for action in possible_next_actions}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {action: 0 for action in possible_next_actions}
        
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key].values()) if possible_next_actions else 0
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
    
    def save_q_table(self):
        with open('q_learning_agent.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)
    
    def load_q_table(self):
        if os.path.exists('q_learning_agent.pkl'):
            with open('q_learning_agent.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
    
    def reset_agent(self):
        """Completely reset the agent's learned knowledge"""
        self.q_table = {}
        if os.path.exists('q_learning_agent.pkl'):
            os.remove('q_learning_agent.pkl')

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = [None] * 9
        self.agent = QLearningAgent()
        self.game_over = False
        self.create_board()
        
        if self.current_player == "O":
            self.ai_move()

    def create_board(self):
        for i in range(9):
            self.buttons[i] = tk.Button(self.root, text="", font=("Arial", 24), width=5, height=2,
                                      command=lambda i=i: self.make_move(i))
            self.buttons[i].grid(row=i // 3, column=i % 3)
        
        reset_button = tk.Button(self.root, text="Reset AI", font=("Arial", 12),
                               command=self.reset_agent)
        reset_button.grid(row=3, column=0, columnspan=3, sticky="ew")

    def make_move(self, index):
        if self.game_over:
            return
            
        if self.board[index] == "" and self.current_player == "X":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            
            if self.check_winner():
                self.handle_win()
            elif "" not in self.board:
                self.handle_draw()
            else:
                self.current_player = "O"
                self.ai_move()

    def ai_move(self):
        if self.game_over:
            return
            
        possible_actions = [i for i, cell in enumerate(self.board) if cell == ""]
        
        if possible_actions:
            old_board = self.board.copy()
            
            action = self.agent.choose_action(old_board, possible_actions)
            self.board[action] = "O"
            self.buttons[action].config(text="O")
            
            if self.check_winner():
                self.handle_win()
                reward = 1
                next_possible_actions = []
            elif "" not in self.board:
                self.handle_draw()
                reward = 0.5
                next_possible_actions = []
            else:
                reward = 0
                next_possible_actions = [i for i, cell in enumerate(self.board) if cell == ""]
            
            self.agent.update_q_table(old_board, action, reward, self.board.copy(), next_possible_actions)
            
            self.current_player = "X"

    def check_winner(self):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != "":
                return True
        return False

    def handle_win(self):
        self.game_over = True
        winner = self.current_player
        if winner == "X":
            messagebox.showinfo("Game Over", "You win!")
        else:
            messagebox.showinfo("Game Over", "AI wins!")
        self.reset_game()

    def handle_draw(self):
        self.game_over = True
        messagebox.showinfo("Game Over", "It's a draw!")
        self.reset_game()

    def reset_game(self):
        self.agent.save_q_table()
        self.board = [""] * 9
        for button in self.buttons:
            button.config(text="")
        self.current_player = "X"
        self.game_over = False
        
        if random.random() < 0.5:
            self.current_player = "O"
            self.ai_move()

    def reset_agent(self):
        """Reset the AI's learned knowledge"""
        if messagebox.askyesno("Reset AI", "This will erase all the AI's learning. Continue?"):
            self.agent.reset_agent()
            messagebox.showinfo("Reset AI", "AI knowledge has been reset to beginner level")
            self.reset_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()