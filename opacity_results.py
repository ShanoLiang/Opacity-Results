import pandas as pd
import matplotlib.pyplot as plt
import json

# Load CSV file
df = pd.read_csv("basic-questionnaire-study_all_tidy.csv")

# Filter answer and correctAnswer rows
answer_rows = df[df['answer'].isin(['Left Image', 'Right Image'])].copy()
correct_rows = df[df['correctAnswer'].str.contains('opacity_left', na=False)].copy()

# Merge based on participantId and trialId
merged = pd.merge(
    answer_rows[['participantId', 'trialId', 'answer', 'duration']],
    correct_rows[['participantId', 'trialId', 'correctAnswer']],
    on=['participantId', 'trialId'],
    how='inner'
)

# Extract opacity values, labels, and differences
def extract_opacities(row):
    data = json.loads(row['correctAnswer'])
    return pd.Series({
        'opacity_left': data['opacity_left'],
        'opacity_right': data['opacity_right'],
        'opacity_diff': abs(data['opacity_left'] - data['opacity_right']),
        'label_with_diff': f"{data['opacity_left']} vs {data['opacity_right']}\n(Δ={abs(data['opacity_left'] - data['opacity_right']):.2f})",
        'label_simple': f"{data['opacity_left']} vs {data['opacity_right']}"
    })

merged = merged.join(merged.apply(extract_opacities, axis=1))
merged['duration'] = pd.to_numeric(merged['duration'], errors='coerce')

# ================= Plot 1 =================
# Response Time vs Opacity Difference
grouped_diff = merged.groupby(['participantId', 'opacity_diff'])['duration'].mean().reset_index()

plt.figure(figsize=(10, 6))
for pid, user_data in grouped_diff.groupby('participantId'):
    plt.plot(user_data['opacity_diff'], user_data['duration'], marker='o', label=pid[:8])

plt.title('Response Time vs. Opacity Difference (Per Participant)')
plt.xlabel('Opacity Difference (|left - right|)')
plt.ylabel('Average Response Time (ms)')
plt.grid(True)
plt.legend(title='Participant ID')
plt.tight_layout()
plt.savefig("response_time_vs_opacity_diff.png")
plt.close()

# ================= Plot 2 =================
# Response Time per Opacity Pair
grouped_label = merged.groupby(['participantId', 'label_simple'])['duration'].mean().reset_index()

plt.figure(figsize=(14, 6))
for pid, user_data in grouped_label.groupby('participantId'):
    plt.plot(user_data['label_simple'], user_data['duration'], marker='o', label=pid[:8])

plt.title('Response Time per Opacity Pair')
plt.xlabel('Opacity Left vs Right')
plt.ylabel('Average Response Time (ms)')
plt.xticks(rotation=90, ha='center')
plt.grid(True)
plt.legend(title='Participant ID')
plt.tight_layout()
plt.savefig("response_time_per_opacity_pair.png")
plt.close()

# ================= Plot 3 =================
# Average Accuracy per Opacity Pair (All Participants)
def determine_correct_answer(row):
    if row['opacity_left'] > row['opacity_right']:
        return "Left Image"
    elif row['opacity_right'] > row['opacity_left']:
        return "Right Image"
    else:
        return "Either"

merged['derived_correct'] = merged.apply(determine_correct_answer, axis=1)
merged['is_correct'] = (merged['answer'] == merged['derived_correct']).astype(int)

avg_accuracy = merged.groupby('label_simple')['is_correct'].mean().reset_index()

plt.figure(figsize=(14, 6))
plt.plot(avg_accuracy['label_simple'], avg_accuracy['is_correct'], marker='o')
plt.title('Average Accuracy per Opacity Pair (All Participants)')
plt.xlabel('Opacity Left vs Right')
plt.ylabel('Accuracy Rate')
plt.ylim(0, 1.05)
plt.xticks(rotation=90, ha='center')
plt.grid(True)
plt.tight_layout()
plt.savefig("accuracy_per_opacity_pair.png")
plt.close()