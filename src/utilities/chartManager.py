import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from collections import Counter

class ChartManager:

    @staticmethod
    def get_health_evolution_figure(history_collection, plant_name):
        health_weights = {"Dead": 0, "Critical": 1, "Poor": 2, "Fair": 3, "Good": 4, "Excellent": 5}
        dates = []
        health_scores = []
        
        history_list = list(history_collection)[:15]
        history_list.reverse()

        for obs in history_list:
            # FILTER: Ignore if no data, if empty, or if "Unknown"
            if not obs.health_state or str(obs.health_state).strip() in ["", "Unknown"]:
                continue
                
            dates.append(obs.date_time.strftime("%H:%M:%S"))
            health_scores.append(health_weights.get(obs.health_state, 3))

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        if dates:
            ax.plot(dates, health_scores, marker='o', linestyle='-', color='#4CAF50', linewidth=2)
        else:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')

        ax.set_title(f"Evolution: {plant_name}", fontsize=10)
        ax.set_yticks(list(health_weights.values()))
        ax.set_yticklabels(list(health_weights.keys()), fontsize=8)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        fig.tight_layout()
        return fig

    @staticmethod
    def get_current_health_pie_figure(observations_collection):
        # FILTER: Collect only valid health states that are not empty
        valid_health_states = [
            obs.health_state for obs in observations_collection 
            if obs.health_state and str(obs.health_state).strip() not in ["", "Unknown"]
        ]
        
        health_counts = Counter(valid_health_states)
        labels = list(health_counts.keys())
        sizes = list(health_counts.values())
        colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF5722']

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)])
            ax.set_title("Health State Overview")
        else:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')

        fig.tight_layout()
        return fig

    @staticmethod
    def get_pests_incidence_figure(observations_collection):
        # FILTER: Ignore empty, "Unknown", and also "No" or "None" (because we want to plot ACTIVE pests)
        valid_pests = [
            obs.pests for obs in observations_collection 
            if obs.pests and str(obs.pests).strip() not in ["", "Unknown", "None", "No"]
        ]
        
        pests_counts = Counter(valid_pests)
        labels = list(pests_counts.keys())
        counts = list(pests_counts.values())

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if counts:
            ax.bar(labels, counts, color='#e57373')
            ax.set_title("Active Pests Incidence")
            ax.set_xlabel("Pest Type")
            ax.set_ylabel("Number of Records")
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')

        fig.tight_layout()
        return fig

    @staticmethod
    def get_specimen_inventory_figure(plants_collection):
        # FILTER: Ignore if the plant has no assigned specimen or is empty
        valid_specimens = [
            plant.specimen.specimen_name for plant in plants_collection 
            if plant.specimen and plant.specimen.specimen_name and str(plant.specimen.specimen_name).strip() != ""
        ]
        
        specimen_counts = Counter(valid_specimens)
        labels = list(specimen_counts.keys())
        sizes = list(specimen_counts.values())

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.4})
            ax.set_title("Plant Inventory by Specimen")
        else:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')

        fig.tight_layout()
        return fig

    @staticmethod
    def get_soil_vs_health_figure(observations_collection):
        data = {}
        health_categories = set()

        for obs in observations_collection:
            soil = obs.soil_condition
            health = obs.health_state
            
            # FILTER: Ignore if health is missing OR if soil condition is missing
            if not soil or str(soil).strip() in ["", "Unknown"]:
                continue
            if not health or str(health).strip() in ["", "Unknown"]:
                continue
            
            health_categories.add(health)
            
            if soil not in data:
                data[soil] = {}
            data[soil][health] = data[soil].get(health, 0) + 1

        health_categories = list(health_categories)
        soils = list(data.keys())
        bottoms = [0] * len(soils)

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if soils:
            for health in health_categories:
                values = [data[soil].get(health, 0) for soil in soils]
                ax.bar(soils, label=health, bottom=bottoms, height=values)
                bottoms = [bottoms[i] + values[i] for i in range(len(soils))]

            ax.set_title("Soil Condition vs. Health State")
            ax.set_xlabel("Soil Condition")
            ax.set_ylabel("Number of Records")
            ax.legend(title="Health State")
        else:
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center')

        fig.tight_layout()
        return fig