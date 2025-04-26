from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from datetime import datetime
import os

app = Flask(__name__)

# Set your Gemini API Key
genai.configure(api_key="AIzaSyC0n-O4RXYcOTQoaU6dIT1zak1vAU6oedk")  # Replace with your real key

questions = {
    "Self-Awareness": [
        "I can easily describe how I feel to others.",
        "I recognize how my emotions affect my behavior.",
        "I am aware of my strengths and weaknesses.",
        "I reflect on my emotions and their causes.",
        "I stay aware of my feelings even under stress.",
        "I know when my mood is influencing my decisions.",
        "I can quickly identify when I am becoming angry or upset.",
        "I recognize patterns in my emotional reactions.",
        "I understand the impact of my emotions on my performance.",
        "I seek feedback about my behavior and emotional reactions."
    ],
    "Self-Management": [
        "I stay calm even in high-pressure situations.",
        "I manage impulsive feelings effectively.",
        "I am able to delay immediate gratification to achieve long-term goals.",
        "I adapt quickly to changing situations.",
        "I think before I act when I’m emotional.",
        "I maintain a positive attitude even during tough times.",
        "I recover quickly after emotional setbacks.",
        "I avoid blaming others when things go wrong.",
        "I stay focused despite distractions.",
        "I handle criticism without becoming defensive."
    ],
    "Social Awareness": [
        "I can easily read other people’s emotional states.",
        "I notice when someone feels uncomfortable even if they don't say it.",
        "I listen actively and empathetically to others.",
        "I understand group dynamics and emotions.",
        "I sense the emotional climate of a room.",
        "I try to understand things from others' perspectives.",
        "I show genuine concern for others’ emotions.",
        "I notice non-verbal cues like facial expressions and body language.",
        "I consider others’ feelings when making decisions.",
        "I value diverse emotional expressions in a group or team."
    ],
    "Relationship Management": [
        "I communicate clearly and openly with others.",
        "I manage conflicts effectively and calmly.",
        "I inspire and motivate others positively.",
        "I collaborate well with different personalities.",
        "I maintain strong personal and professional relationships.",
        "I provide feedback without offending others.",
        "I apologize sincerely when necessary.",
        "I lead by example during emotional challenges.",
        "I encourage open emotional expression in teams or groups.",
        "I build bonds with others by showing empathy and trust."
    ]
}

def calculate_scores(scores):
    final_scores = {}
    for section, answers in scores.items():
        total = sum(map(int, answers))  # Ensure conversion to int
        final_scores[section] = round((total / 50) * 100, 2)
    return final_scores

def calculate_average_eq(final_scores):
    total_score = sum(final_scores.values())
    average_eq = total_score / len(final_scores)
    return round(average_eq, 2)

def generate_summary(final_scores):
    prompt = f"""
User's Emotional Intelligence Test Results:

Self-Awareness Score: {final_scores['Self-Awareness']}%
Self-Management Score: {final_scores['Self-Management']}%
Social Awareness Score: {final_scores['Social Awareness']}%
Relationship Management Score: {final_scores['Relationship Management']}%

Based on these scores, write a short 5-sentence emotional profile summary.
Focus on strengths, weaknesses, and areas of growth.
Friendly, empathetic tone.
"""
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(prompt)
        summary = response.text
        return summary.strip()
    except Exception as e:
        print("Error generating summary:", e)
        return "Summary generation failed."

def save_to_csv(name, final_scores, average_eq):
    test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        "Name": name,
        "Test Date & Time": test_time,
        "Self-Awareness": final_scores['Self-Awareness'],
        "Self-Management": final_scores['Self-Management'],
        "Social Awareness": final_scores['Social Awareness'],
        "Relationship Management": final_scores['Relationship Management'],
        "Total EQ Score": average_eq
    }
    csv_file = 'eq_test_results.csv'
    fieldnames = ["Name", "Test Date & Time", "Self-Awareness", "Self-Management", "Social Awareness", "Relationship Management", "Total EQ Score"]

    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def plot_eq_graph(final_scores, average_eq):
    if not os.path.exists('static'):
        os.makedirs('static')

    plt.figure(figsize=(8, 6))
    sections = list(final_scores.keys())
    scores = list(final_scores.values())

    sns.barplot(x=sections, y=scores, palette="viridis")
    plt.xlabel("EQ Sections")
    plt.ylabel("Scores (%)")
    plt.title("Emotional Intelligence Section Scores")
    plt.axhline(average_eq, color='red', linestyle='--', label=f'Average EQ: {average_eq}%')
    plt.legend()
    plt.tight_layout()

    graph_path = 'static/eq_graph.png'
    plt.savefig(graph_path)
    plt.close()
    return graph_path

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        user_scores = {}

        for section in questions.keys():
            user_scores[section] = []
            for i in range(10):
                answer = request.form.get(f"{section}_{i}")
                user_scores[section].append(answer)

        final_scores = calculate_scores(user_scores)
        average_eq = calculate_average_eq(final_scores)
        summary = generate_summary(final_scores)
        graph_path = plot_eq_graph(final_scores, average_eq)

        save_to_csv(name, final_scores, average_eq)

        return render_template('result.html', name=name, final_scores=final_scores, average_eq=average_eq, summary=summary, graph_path=graph_path)

    return render_template('home.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
