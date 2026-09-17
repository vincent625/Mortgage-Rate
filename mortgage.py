import requests
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
import time

def run_smart_scan(b):
    with output:
        clear_output()
        
        # --- SETUP ---
        price = price_input.value
        dp_percent = down_payment_input.value
        raw_score = credit_slider.value
        down_payment_dollars = price * (dp_percent / 100)
        loan_amt = int(price - down_payment_dollars)
        
        # Score Buckets
        bucket_floor = int(raw_score / 20) * 20
        if bucket_floor > 840: bucket_floor = 840
        if bucket_floor < 600: bucket_floor = 600
        min_fico = bucket_floor
        max_fico = bucket_floor + 19

        product = product_dropdown.value
        
        print(f"🚀 Starting Smart National Scan")
        print(f"💰 Loan Amount: ${loan_amt:,} | Score: {min_fico}-{max_fico}")
        print("⏳ Scanning 51 regions (with auto-fallback)...")
        
        progress.value = 0
        display(progress)
        
        results = []
        
        url = "https://www.consumerfinance.gov/oah-api/rates/rate-checker"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        }

        # Base Params
        params_base = {
            "price": price,
            "loan_amount": loan_amt,
            "min_down": int(down_payment_dollars),
            "minfico": min_fico,
            "maxfico": max_fico
        }

        # Handle Fixed vs ARM params
        if "Fixed" in product:
            params_base["rate_structure"] = "fixed"
            params_base["loan_term"] = int(product.split('-')[0])
            params_base["arm_type"] = "5-1"
        else:
            params_base["rate_structure"] = "arm"
            params_base["loan_term"] = 30
            params_base["arm_type"] = product.split(' ')[0].replace('/', '-')

        # Loop through states
        for i, state in enumerate(all_states):
            
            # --- STRATEGY: Try Jumbo first, if empty/fail, try Conforming ---
            # (Or vice versa depending on amount, but checking both ensures coverage)
            
            # 1. Determine primary likely type
            if loan_amt > 766550:
                primary_type = 'jumbo'
                secondary_type = 'conf'
            else:
                primary_type = 'conf'
                secondary_type = 'jumbo'

            # Helper function to fetch data
            def fetch_data(l_type):
                p = params_base.copy()
                p['state'] = state
                p['loan_type'] = l_type
                try:
                    r = requests.get(url, params=p, headers=headers)
                    if r.status_code == 200:
                        d = r.json()
                        if 'data' in d and d['data']:
                            return d['data'], d.get('timestamp')
                    elif r.status_code == 429:
                        print(f"⚠️ Rate limited at {state}. Slowing down...")
                        time.sleep(2)
                except:
                    pass
                return None, None

            # Attempt 1: Primary Type
            rates_dict, timestamp = fetch_data(primary_type)
            used_type = primary_type

            # Attempt 2: Secondary Type (Fallback) if Attempt 1 failed
            if not rates_dict:
                rates_dict, timestamp = fetch_data(secondary_type)
                used_type = secondary_type

            # Process Success
            if rates_dict:
                rates_float = [float(r) for r in rates_dict.keys()]
                min_rate = min(rates_float)
                total_lenders = sum(rates_dict.values())
                
                date_str = timestamp.split('T')[0] if timestamp else "N/A"

                results.append({
                    "State": state,
                    "Lowest Rate (%)": min_rate,
                    "Total Lenders": total_lenders,
                    "Loan Type Used": used_type.upper(),
                    "Date Range": date_str
                })

            # Polite Delay
            time.sleep(0.1)
            progress.value = i + 1

        # --- DISPLAY RESULTS ---
        if not results:
            print("❌ No data found. Possible reasons:")
            print("1. Loan amount is too high/low for the selected product.")
            print("2. Down payment is too low (Jumbo often needs 20%+).")
            print("3. Server is blocking requests (Try again in 1 minute).")
            return

        df = pd.DataFrame(results)
        df_sorted = df.sort_values(by=["Lowest Rate (%)", "Total Lenders"], ascending=[True, False])
        df_sorted.reset_index(drop=True, inplace=True)
        df_sorted.index += 1
        
        print("\n🏆 TOP 10 STATES WITH LOWEST RATES")
        print("=" * 60)
        display(df_sorted.head(10))
        
        print(f"\n📊 National Average of Lows: {df['Lowest Rate (%)'].mean():.3f}%")
        
        # Visualization
        top_10 = df_sorted.head(10)
        plt.figure(figsize=(12, 5))
        bars = plt.bar(top_10['State'], top_10['Lowest Rate (%)'], color='#ff7f0e')
        
        # Dynamic Y-axis
        ymin = top_10['Lowest Rate (%)'].min() - 0.25
        ymax = top_10['Lowest Rate (%)'].max() + 0.25
        plt.ylim(ymin, ymax)
        
        plt.ylabel('Interest Rate (%)')
        plt.title(f'Lowest {product} Rates by State (Top 10)')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}%', ha='center', va='bottom', fontsize=9)
        
        plt.show()

# --- UI SETUP ---
style = {'description_width': 'initial'}

all_states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", 
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", 
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", 
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

product_dropdown = widgets.Dropdown(
    options=["30-Year Fixed", "15-Year Fixed", "7/1 ARM", "5/1 ARM", "5/3 ARM"],
    value='30-Year Fixed',
    description='Product:'
)

credit_slider = widgets.IntSlider(value=800, min=600, max=850, description='Credit Score:')
price_input = widgets.IntText(value=1000000, description='Price ($):', style=style)
down_payment_input = widgets.BoundedFloatText(value=20.0, min=0, max=100, step=0.5, description='Down Pymt %:', style=style)

progress = widgets.IntProgress(value=0, min=0, max=51, description='Scanning:', bar_style='info')

run_button = widgets.Button(
    description='Start Smart Scan',
    button_style='success',
    icon='play'
)

output = widgets.Output()
run_button.on_click(run_smart_scan)

print("🇺🇸 Smart National Rate Scanner (Auto-detects Jumbo/Conf per state)")
display(product_dropdown, credit_slider, price_input, down_payment_input, run_button, output)
