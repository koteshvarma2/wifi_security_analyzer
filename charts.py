import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def get_color_for_security(sec_type):
    sec_type = sec_type.lower()
    if "wpa3" in sec_type:
        return "#4caf50" # Green
    elif "wpa2" in sec_type:
        if "enterprise" in sec_type:
            return "#388e3c" # Darker green
        return "#8bc34a" # Light Green
    elif "wpa" in sec_type:
        return "#ffeb3b" # Yellow
    elif "wep" in sec_type:
        return "#ff9800" # Orange
    elif "open" in sec_type:
        return "#f44336" # Red
    return "#9e9e9e" # Grey

def create_security_pie_chart(security_counts, is_dark_mode=True):
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    bg_color = '#2b2b2b' if is_dark_mode else '#ffffff'
    text_color = '#ffffff' if is_dark_mode else '#000000'
    
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    
    labels = []
    sizes = []
    colors = []
    
    for sec_type, count in security_counts.items():
        if count > 0:
            labels.append(sec_type)
            sizes.append(count)
            colors.append(get_color_for_security(sec_type))
            
    if sizes:
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=90, textprops={'color': text_color, 'fontsize': 8}
        )
    else:
        ax.text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center', color=text_color)
        
    ax.set_title("Security Distribution", color=text_color)
    fig.tight_layout()
    return fig

def create_channel_bar_chart(channels_dict, is_dark_mode=True):
    fig = Figure(figsize=(5, 4), dpi=100)
    
    bg_color = '#2b2b2b' if is_dark_mode else '#ffffff'
    text_color = '#ffffff' if is_dark_mode else '#000000'
    
    fig.patch.set_facecolor(bg_color)
    
    channels_24 = channels_dict.get('2.4GHz', {})
    channels_5 = channels_dict.get('5GHz', {})
    
    if channels_5:
        # Two subplots
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        
        # 2.4GHz
        ax1.set_facecolor(bg_color)
        ax1.bar(list(channels_24.keys()), list(channels_24.values()), color='#2196f3')
        ax1.set_xticks(list(channels_24.keys()))
        ax1.set_title("2.4GHz Channel Usage", color=text_color, fontsize=10)
        ax1.tick_params(colors=text_color, labelsize=8)
        
        # 5GHz
        ax2.set_facecolor(bg_color)
        # 5GHz has many channels, only show ones that have count > 0 to save space
        c5_keys = [k for k, v in channels_5.items() if v > 0]
        c5_vals = [channels_5[k] for k in c5_keys]
        ax2.bar(c5_keys, c5_vals, color='#9c27b0')
        ax2.set_xticks(c5_keys)
        ax2.set_title("5GHz Channel Usage", color=text_color, fontsize=10)
        ax2.tick_params(colors=text_color, labelsize=8)
        
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color(text_color)
    else:
        # Just 2.4GHz
        ax1 = fig.add_subplot(111)
        ax1.set_facecolor(bg_color)
        ax1.bar(list(channels_24.keys()), list(channels_24.values()), color='#2196f3')
        ax1.set_xticks(list(channels_24.keys()))
        ax1.set_xlabel("Channel (2.4GHz)", color=text_color)
        ax1.set_ylabel("Network Count", color=text_color)
        ax1.set_title("Channel Usage", color=text_color)
        ax1.tick_params(colors=text_color)
        for spine in ax1.spines.values():
            spine.set_color(text_color)
            
    fig.tight_layout()
    return fig
