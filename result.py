import pandas as pd
import matplotlib.pyplot as plt
import os

# Create the results directory if it doesn't exist
results_dir = "./results"
os.makedirs(results_dir, exist_ok=True)

# Read the CSV file
df = pd.read_csv('test_result.csv')

# Set the style for the plots
plt.style.use('ggplot')

# Function to create and save a column chart
def create_column_chart(data, x, y, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(data[x], data[y])
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45, ha='right')

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, filename))
    plt.close()

# 1. Compare different test types
test_type_avg = df.groupby('Test Type')['Response Time (seconds)'].mean().reset_index()
create_column_chart(
    test_type_avg,
    'Test Type',
    'Response Time (seconds)',
    'Average Response Time by Test Type',
    'Test Type',
    'Average Response Time (seconds)',
    'test_type_comparison.png'
)

# 2. Direction distribution
direction_counts = df['Direction'].value_counts().reset_index()
direction_counts.columns = ['Direction', 'Count']
create_column_chart(
    direction_counts,
    'Direction',
    'Count',
    'Direction Distribution',
    'Direction',
    'Count',
    'direction_distribution.png'
)

# 3. Average response time by direction
direction_avg = df.groupby('Direction')['Response Time (seconds)'].mean().reset_index()
create_column_chart(
    direction_avg,
    'Direction',
    'Response Time (seconds)',
    'Average Response Time by Direction',
    'Direction',
    'Average Response Time (seconds)',
    'direction_response_time.png'
)

# 4. Test type and direction combined (stacked column graph)
test_direction_avg = df.groupby(['Test Type', 'Direction'])['Response Time (seconds)'].mean().unstack()

plt.figure(figsize=(12, 6))
test_direction_avg.plot(kind='bar', stacked=True, figsize=(12, 6))

plt.title('Average Response Time by Test Type and Direction', fontsize=16)
plt.xlabel('Test Type', fontsize=12)
plt.ylabel('Average Response Time (seconds)', fontsize=12)
plt.legend(title='Direction', title_fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')

# Add value labels on each segment of the stacked bars
for c in plt.gca().containers:
    plt.gca().bar_label(c, fmt='%.2f', label_type='center')

plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'test_type_direction_comparison.png'))
plt.close()

print(f"Charts have been created and saved in the '{results_dir}' folder.")
