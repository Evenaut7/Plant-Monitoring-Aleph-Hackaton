import matplotlib.pyplot as plt
from collections import Counter

class ChartManager:

    # Each Plant
    @staticmethod
    def plot_health_evolution(history_collection, plant_name):
        health_weights = {"Dead": 0, "Critical": 1, "Poor": 2, "Fair": 3, "Good": 4, "Excellent": 5}
        dates = []
        health_scores = []
        history_list = list(history_collection)
        history_list.reverse()

        for obs in history_list:
            dates.append(obs.date_time)
            health_scores.append(health_weights.get(obs.health_state, 3))

        plt.figure(figsize=(10, 5))
        plt.plot(dates, health_scores, marker='o', linestyle='-', color='#4CAF50', linewidth=2)
        plt.title(f"Health Evolution: {plant_name}")
        plt.xlabel("Date & Time")
        plt.ylabel("Health State")
        plt.yticks(list(health_weights.values()), list(health_weights.keys()))
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

    # All Plants
    @staticmethod
    def plot_current_health_pie(observations_collection):
        health_counts = Counter(obs.health_state for obs in observations_collection)
        labels = list(health_counts.keys())
        sizes = list(health_counts.values())
        colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF5722']

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)])
        plt.title("Health State Overview")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_specimen_inventory(plants_collection):
        specimen_counts = Counter(plant.specimen.specimen_name for plant in plants_collection)
        labels = list(specimen_counts.keys())
        sizes = list(specimen_counts.values())

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.4})
        plt.title("Plant Inventory by Specimen")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_soil_vs_health(observations_collection):
        data = {}
        health_categories = set()

        for obs in observations_collection:
            soil = obs.soil_condition
            health = obs.health_state
            health_categories.add(health)
            
            if soil not in data:
                data[soil] = {}
            data[soil][health] = data[soil].get(health, 0) + 1

        health_categories = list(health_categories)
        soils = list(data.keys())
        bottoms = [0] * len(soils)

        plt.figure(figsize=(10, 6))

        for health in health_categories:
            values = [data[soil].get(health, 0) for soil in soils]
            plt.bar(soils, values, label=health, bottom=bottoms)
            bottoms = [bottoms[i] + values[i] for i in range(len(soils))]

        plt.title("Soil Condition vs. Health State")
        plt.xlabel("Soil Condition")
        plt.ylabel("Number of Records")
        plt.legend(title="Health State")
        plt.tight_layout()
        plt.show()