import seaborn as sns

# Get the names of available color palettes
palette_names = sns.color_palette().as_named_colors().keys()

# Print the palette names
for name in palette_names:
    print(name)