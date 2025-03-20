# # src/utils/data_logging.py
import csv
import json

def log_data(data, filename, format='csv'):
    """Logs data to a file (CSV or JSON)."""
    try:
        if format == 'csv':
            with open(filename, 'a', newline='') as csvfile:  # Append mode
                writer = csv.writer(csvfile)

                # Write header if the file is new
                if csvfile.tell() == 0:
                    header = list(data.keys())
                    writer.writerow(header)

                writer.writerow(data.values())

        elif format == 'json':
            with open(filename, 'a') as jsonfile:  # Append mode
                json.dump(data, jsonfile)
                jsonfile.write('\n')  # Add newline to separate entries

        else:
            print(f"Unsupported data format: {format}")
            return False

        return True  # Successfully logged data

    except Exception as e:
        print(f"Error logging data: {e}")
        return False

def load_data(filename, format='csv'):
    """Loads data from a file (CSV or JSON)."""
    try:
        if format == 'csv':
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
                return data

        elif format == 'json':
            data = []
            with open(filename, 'r') as jsonfile:
                for line in jsonfile:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        continue
            return data

        else:
            print(f"Unsupported data format: {format}")
            return None

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def visualize_data(filename, format='csv'):
    """Visualizes data using Matplotlib (example: resource collection over time)."""
    import matplotlib.pyplot as plt

    data = load_data(filename, format)
    if not data:
        print("No data to visualize.")
        return

    try:
        # Assuming data contains 'time_step' and 'collected_resources' keys
        time_steps = [int(d['time_step']) for d in data]
        collected_resources = [float(d['collected_resources']) for d in data]

        plt.plot(time_steps, collected_resources)
        plt.xlabel("Time Step")
        plt.ylabel("Collected Resources")
        plt.title("Resource Collection Over Time")
        plt.show()

    except KeyError as e:
        print(f"Missing key in data: {e}.  Data must have `time_step` and `collected_resources` keys.")
    except Exception as e:
        print(f"Error visualizing data: {e}")

if __name__ == '__main__':
    # Example Usage
    data = {
        'time_step': 1,
        'agent_x': 5,
        'agent_y': 5,
        'energy': 80,
        'collected_resources': 2
    }

    filename = 'simulation_data.csv'  # Or 'simulation_data.json'
    log_data(data, filename, format='csv')

    loaded_data = load_data(filename, format='csv')
    print("Loaded Data:\n", loaded_data)

    visualize_data(filename, format='csv') # Run visualization on data.