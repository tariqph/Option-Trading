

def row_color_strat(merged_data):
    color1 = 'rgb(255,60,60)'
    color2 = 'rgb(9,49,69)'
    color3 = 'rgb(3,163,30)'
    
    deltas = merged_data['CE_Delta'].values

    
    row_colors = []
    for delta in deltas:
        if delta >= 0.5 and delta < 0.55:
            row_colors.append(color3)
        elif delta >=0.55 and delta < 0.6:
            row_colors.append(color1)
        else:
            row_colors.append(color2)
            
    return row_colors