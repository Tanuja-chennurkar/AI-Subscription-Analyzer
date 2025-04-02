import pandas as pd

def analyze_subscriptions(raw_data):
    # Implementation from Subscription_Analyzer.py
    # Modified to work with dict input
    
    df = pd.DataFrame(raw_data)
    
    # Your analysis logic
    df['Cost per Hour'] = df['Total (INR)'] / df['Usage']
    
    def categorize(usage):
        if usage < 5: return 'Cancel'
        elif 5 <= usage < 65: return 'Consider Downgrade'
        else: return 'Keep'
    
    df['Recommendation'] = df['Usage'].apply(categorize)
    
    return df.to_dict('records')