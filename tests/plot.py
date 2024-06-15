import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Function to parse the evaluation file
def parse_evaluation_file(file_path):
    games = []
    with open(file_path, "r") as file:
        game_data = {}
        for line in file:
            line = line.strip()
            if line.startswith("Game"):
                if game_data:
                    games.append(game_data)
                game_data = {"Game": int(line.split(":")[1].strip())}
            elif line.startswith("Start Time"):
                game_data["Start Time"] = line.split(":")[1].strip()
            elif line.startswith("End Time"):
                game_data["End Time"] = line.split(":")[1].strip()
            elif line.startswith("Difficulties"):
                difficulties = line.split(" : ")[1:]
                game_data["Orange Difficulty"] = int(difficulties[1][0])
                game_data["White Difficulty"] = int(difficulties[2][0])
            elif line.startswith('{"placing"'):
                game_config = eval(line)
                game_data.update(game_config)
            elif line.startswith("{"):
                line = line.replace("inf", "np.inf")
                eval_data = eval(line)
                game_data.update(eval_data)
            elif line.startswith("Winner"):
                game_data["Winner"] = line.split(":")[1].strip()
    if game_data:
        games.append(game_data)
    return games


# Function to generate a pandas DataFrame from parsed data
def create_dataframe(parsed_data):
    df = pd.DataFrame(parsed_data)
    return df


def plot_game_data(game_data):
    orange_scores = game_data["orange"]
    white_scores = game_data["white"]

    # Remove -inf values from white_scores
    white_scores = [score for score in white_scores if score != float("-inf")]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(orange_scores, label="Orange Player", color="orange")
    plt.plot(white_scores, label="White Player", color="blue")
    plt.xlabel("Turn")
    plt.ylabel("Score")
    plt.title("Game Scores")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Calculate and print statistics
    orange_mean = np.mean(orange_scores)
    white_mean = np.mean(white_scores)
    orange_std = np.std(orange_scores)
    white_std = np.std(white_scores)
    orange_max = np.max(orange_scores)
    white_max = np.max(white_scores)
    orange_min = np.min(orange_scores)
    white_min = np.min(white_scores)
    orange_median = np.median(orange_scores)
    white_median = np.median(white_scores)

    print("Orange Player Statistics:")
    print(f"Mean Score: {orange_mean}")
    print(f"Standard Deviation: {orange_std}")
    print(f"Max Score: {orange_max}")
    print(f"Min Score: {orange_min}")
    print(f"Median Score: {orange_median}")
    print()

    print("White Player Statistics:")
    print(f"Mean Score: {white_mean}")
    print(f"Standard Deviation: {white_std}")
    print(f"Max Score: {white_max}")
    print(f"Min Score: {white_min}")
    print(f"Median Score: {white_median}")


# Main function
def main():
    file_path = "evaluation_results/2024-04-29_09-40-58/evaluation_results.txt"  # Change this to your file path
    parsed_data = parse_evaluation_file(file_path)
    df = create_dataframe(parsed_data)
    for key in df.columns:
        # print a sample
        print(f"{key}: {df[key].iloc[0]}")
    plot_game_data(game_data=parsed_data[0])


if __name__ == "__main__":
    main()
