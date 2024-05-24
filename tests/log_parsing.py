import re
import ast
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


def parse_logs(log_file):
    # Define a pattern to match each log entry
    pattern = r"Game : (\d+)\nStart Time : (.+?) , End Time : (.+?)\nDifficulties : Orange : (\d+) White : (\d+)\nNumber of Pieces : Orange : \[(.*?)\] White : \[(.*?)\]\nTraining Parameters : \n(.*?)\nEvaluation Coefficients : \n(.*?)\nWinner : (\w+)\n(.*?)\n\n"

    # Read the log file
    with open(log_file, "r") as file:
        logs = file.read()
        # replace <Player.orange: 'orange'> with 'orange' and <Player.white: 'white'> with 'white'
        logs = (
            logs.replace("<Player.orange: 'orange'>", "'orange'")
            .replace("<Player.white: 'white'>", "'white'")
            .replace("inf", "np.inf")
        )
    # Split the logs into individual entries
    entries = re.findall(pattern, logs, re.DOTALL)

    parsed_logs = []
    for entry in entries:
        # Extract the relevant information
        int(entry[0])
        start_time = datetime.strptime(entry[1], "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(entry[2], "%Y-%m-%d %H:%M:%S.%f")
        orange_difficulty = int(entry[3])
        white_difficulty = int(entry[4])
        orange_pieces = list(map(int, entry[5].split(", ")))
        white_pieces = list(map(int, entry[6].split(", ")))
        training_params_str = entry[7].split("\n")
        params = ["stupidity", "max_n_operations", "max_n_samples"]
        training_params = {}
        for i, param in enumerate(params):
            training_params[param] = training_params_str[i].split(" : ")[1]
            if training_params[param] == "None":
                training_params[param] = None
            elif training_params[param] in ["True", "False"]:
                training_params[param] = training_params[param] == "True"
            else:
                try:
                    training_params[param] = float(training_params[param])
                except ValueError:
                    try:
                        training_params[param] = int(training_params[param])
                    except ValueError:
                        try:
                            training_params[param] = ast.literal_eval(
                                training_params[param]
                            )
                        except ValueError:
                            pass
        eval_coeffs = ast.literal_eval(entry[8])
        winner = entry[9] if entry[9] != "None" else "Draw"
        evaluation_scores = eval(entry[10])

        # Store the information in a dictionary
        game_info = {
            "Start Time": start_time,
            "End Time": end_time,
            "Difficulties": {"Orange": orange_difficulty, "White": white_difficulty},
            "Number of Pieces": {"Orange": orange_pieces, "White": white_pieces},
            "Training Parameters": training_params,
            "Evaluation Coefficients": eval_coeffs,
            "Winner": winner,
            "Evaluation Scores": evaluation_scores,
        }
        parsed_logs.append(game_info)

    return parsed_logs


def plot_evaluation_scores(parsed_logs):
    # Extract the evaluation scores for each game
    scores = [log["Evaluation Scores"] for log in parsed_logs]

    # Create a DataFrame from the scores
    df = pd.DataFrame(scores)

    # Plot the evaluation scores
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    df.plot(y=["placing", "moving", "flying"], ax=ax[0], title="Evaluation Scores")
    df.plot(y=["total"], ax=ax[1], title="Total Score")
    df.plot(y=["n_pieces", "n_mills", "entropy"], ax=ax[2], title="Individual Scores")

    plt.tight_layout()
    plt.show()


def compute_statistics(parsed_logs):
    # Extract the evaluation scores for each game
    scores = [log["Evaluation Scores"] for log in parsed_logs]

    # Create a DataFrame from the scores
    df = pd.DataFrame(scores)

    # Compute the mean and standard deviation of the scores
    mean_scores = df.mean()
    std_scores = df.std()

    return mean_scores, std_scores


# Usage
log_file = "evaluation_results/2024-04-30_02-26-55/evaluation_results.txt"
parsed_logs = parse_logs(log_file)
plot_evaluation_scores(parsed_logs)
mean_scores, std_scores = compute_statistics(parsed_logs)
print("Mean Scores:")
print(mean_scores)
print("\nStandard Deviation of Scores:")
print(std_scores)
# Output
