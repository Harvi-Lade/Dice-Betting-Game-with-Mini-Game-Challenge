import random
import time
import json
import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(filename='game_errors.log', level=logging.ERROR)

# Constants
STARTING_POINTS = 20
BONUS_ROLL_NUMBER = 6
MINI_GAME_BONUS_RANGE = (5, 15)
DICE_ART = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

# Colorama Codes
RESET = Style.RESET_ALL
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
CYAN = Fore.CYAN

class Player:
    """Class representing a player in the dice game."""
    def __init__(self, name):
        self.name = name
        self.points = STARTING_POINTS

    def is_active(self):
        """Check if player still has points to play"""
        return self.points > 0
    
class DiceGame:
    """Main class for the dice game, containing the game loop and functionalities."""

    def __init__(self, players):
        self.players = players

    def roll_dice(self):
        """Simulate rolling a dice."""
        return random.randint(1, 6)
    
    def place_bet(self, player):
        """Allow a player to place a valid bet."""
        while True:
            try:
                bet = int(input(f"{CYAN}{player.name}, how much do you want to bet? {RESET}"))
                if 0 < bet <= player.points:
                    return bet
                else:
                    print(f"{RED}Invalid bet! Bet should be between 1 and {player.points} points.{RESET}")
            except ValueError:
                print(f"{RED}Please enter a valid number.{RESET}")

    def handle_roll(self, player, bet):
        """Manage the main roll logic, including handlin bonus rolls."""

        print(f"\n{player.name} is rolling the dice...")
        time.sleep(0.5)
        result = self.roll_dice()
        print(f"{YELLOW}{player.name} rolled a {DICE_ART[result]} ({result})!{RESET}")

        if result >= 4:
            player.points += bet
            print(f"{GREEN}{player.name} won the bet and now has {player.points} points!{RESET}")
            if result == BONUS_ROLL_NUMBER:
                print(f"{BLUE}Bonus Roll! You get an extra roll for rolling a 6!{RESET}")
                self.bonus_roll(player, bet)
        else:
            if player.points == bet:
                player.points -= bet
                print(f"\n{RED}{player.name} lost the bet and all the points as well.")
            else:
                player.points -= bet
                print(f"{RED}{player.name} lost the bet and now has {player.points} points!{RESET}")
    
    def bonus_roll(self, player, bet):
        """Handle bonus roll for player if they roll a 6."""

        print(f"\n{player.name} is rolling the dice...")
        time.sleep(0.5)
        bonus_result = self.roll_dice()
        print(f"{YELLOW}{player.name} rolled a bonus {DICE_ART[bonus_result]} ({bonus_result}){RESET}")
        if bonus_result >= 4:
            player.points += bet
            print(f"{GREEN}Bonus roll success! {player.name} won an additional {bet} points and now has total {player.points} points!{RESET}")
        else:
            player.points -= bet
            print(f"{RED}Bonus roll lost. {player.name} lost {bet} points and now has total {player.points} points!{RESET}")
    
    def play_mini_game(self, player):
        """Offer the player a chance to earn bonus points via a guessing game."""

        guessed_correctly, actual = self.guessing_game(player)
        if guessed_correctly:
            bonus_points = random.randint(*MINI_GAME_BONUS_RANGE)
            player.points += bonus_points
            print(f"{GREEN}Correct guess! {player.name} won {bonus_points} bonus points and now has total {player.points} points!.{RESET}")
        else:
            print(f"{RED}Wrong guess! The correct number was {actual}.{RESET}")

    def guessing_game(self, player):
        """Mini-game: Player guesses a number between 1 and 5."""

        print("\nMini-Game: Guessing Game!")
        while True:
            try:
                guess = int(input(f"{CYAN}{player.name}, guess a number between 1 and 5: {RESET}"))
                if 1 <= guess <= 5:
                    actual = random.randint(1,5)
                    return guess == actual, actual
                else:
                    print(f"{RED}Please guess a number between 1 and 5.{RESET}")
            except ValueError:
                print(f"{RED}Invalid input. Enter a number between 1 and 5.{RESET}")
    
    def get_yes_no_input(self, prompt):
        """Prompt user for a 'yes' or 'no' response and validate input."""
        while True:
            response = input(prompt).strip().lower()
            if response in ['yes', 'no']:
                return response
            else:
                print(f"{RED}Invalid input. Please enter 'yes' or 'no'.")

    def play_round(self):
        """Main game loop where players take turns."""
        while True:
            #Get active players
            active_players = [player for player in self.players if player.is_active()]

            #Check if only one player is left with points
            if len(active_players) == 1:
                winner = active_players[0]
                print(f"\n{GREEN}{winner.name} is the last player with points and wins with {winner.points} points!{RESET}")
                return winner.points, winner.name
            
            #Process each active player's turn
            for player in active_players:
                print(f"\n{BLUE}{player.name}'s turn! You have {player.points} points.{RESET}")
                bet = self.place_bet(player)
                self.handle_roll(player, bet)

                #check again if only one player is left after a roll
                if len([p for p in self.players if p.is_active()]) == 1:
                    last_player = [p for p in self.players if p.is_active()][0]
                    print(f"\n{GREEN}{last_player.name} is the last player with points and wins with {last_player.points} points!{RESET}")
                    return last_player.points, last_player.name

                if player.points <= 0:
                    print(f"{RED}{player.name} has no more points and is out of the game.{RESET}")
                    continue

                #Ask if player wants to play the Mini-Game for extra points
                play_mini_game_option = self.get_yes_no_input("Do you want to play the Mini-Game to earn bonus points (yes/no)?: ")
                if play_mini_game_option == 'yes':
                    self.play_mini_game(player)
            
            continue_game = self.get_yes_no_input("\nDo you want to continue playing (yes/no)?: ").lower()
            if continue_game == 'no':
                max_points = max(player.points for player in self.players)
                return max_points, [player.name for player in self.players if player.points == max_points][0]
    
    def manage_high_scores(self, score, player_name):
        """Manage high scores, loading from and saving to a JSON file."""
        try:
            with open("high_scores.json", "r") as file:
                high_scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            high_scores = []
        
        high_scores.append({"name": player_name, "score": score})
        high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:5]

        print("\nHigh Scores:")
        for idx, record in enumerate(high_scores, 1):
            print(f"{YELLOW}{idx}. {record['name']} - {record['score']} points{RESET}")
        
        try:
            with open("high_scores.json", "w") as file:
                json.dump(high_scores, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save high scores: {e}")

def main():
    """Initialize the game and handle main execution."""
    players = []

    while True:
        try:
            num_players = int(input("Enter the number of players: "))
            if num_players > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    for i in range(num_players):
        name = input(f"Enter name of the player {i + 1}: ").strip() or f"Player {i + 1}"
        players.append(Player(name))
    
    game = DiceGame(players)
    winner_points, winner_name = game.play_round()
    game.manage_high_scores(winner_points, winner_name)


# Run the game
if __name__ == "__main__":
    main()